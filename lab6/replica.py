import rpyc
from rpyc.utils.server import ThreadedServer
from typing import List, Tuple
from threading import RLock, Event
from utils import *
from config import *

class ReplicaNode(rpyc.Service):
    def __init__(self, my_id: int):
        self.id = my_id
        self.X = 0
        self.can_write = True if self.id == 1 else False
        self.peer_connections = [BASE_PORT+i for i in range(1,N+1) if i != self.id]
        self.history: List[Tuple[int, int]] = []
        self.uncommitted_history: List[Tuple[int, int]] = []
        self.LOCK = RLock()
        self.permission_granted_event = Event()
        self.DEBUG_MODE = False
        self.changes_committed = True

    def exposed_read(self):
        return self.X
        
    def exposed_set_debug(self, state: bool):
        self.DEBUG_MODE = state

    def exposed_get_history(self):
        return self.history

    def exposed_get_status(self):
        return {
            "Replica ID": self.id, 
            "Changes committed": self.changes_committed,
            "Primary (has token)": self.can_write,
            "Debug mode": self.DEBUG_MODE
        }

    def exposed_set(self, value: int):
        '''
        Tries to set the local variable equal to the parameter 'value'.
        For that, it first checks if the local replica is the primary (can_write).
        
        If it is not, it must try to get the write token, waiting up to a maximum of 27 seconds,
        with several attempts in between. If all of them fail, the function returns False, meaning
        it was impossible to obtain write permission for the time being. 
        
        In all other cases, returns True.
        '''

        BACKOFF_LIMIT = 10

        self.LOCK.acquire()
        if self.can_write:
            debug(self.DEBUG_MODE, "[DEBUG] I have the write token")
            self.__set_local(value)
            self.LOCK.release()
        else:
            self.LOCK.release()
            debug(self.DEBUG_MODE, "[DEBUG] I do not have the write token")
            
            self.request_write()

            #linear backoff on retries 
            #backing off exponentially would not make sense for this use case, as network failures
            #and other interferences are never the cause of delay
            backoff_counter = 1
            interrupted = False
            while not self.permission_granted_event.wait(backoff_counter*0.5):
                if backoff_counter == BACKOFF_LIMIT:
                    interrupted = True
                    break
                self.request_write()
                backoff_counter = backoff_counter + 1 if backoff_counter <= BACKOFF_LIMIT else backoff_counter

            if interrupted:
                return False
            
            with self.LOCK:
                self.permission_granted_event.clear()
                self.__set_local(value)
        
        return True

    def request_write(self):
        '''
        Sends asynchronous requests to all other replicas, requesting the write token.
        The function set_write is used as callback for the async calls.
        '''
        
        #assumes replicas will never fail and will all be available when requested
        #TODO: handle possible errors in a better way
        requests_in_flight = []
        debug(self.DEBUG_MODE, "[DEBUG] Trying to get the write token...")
        for port in self.peer_connections:
            conn = rpyc.connect("localhost", port=port)
            ask_for_permission_async = rpyc.async_(conn.root.ask_for_write_permission)
            async_result = ask_for_permission_async()
            async_result.add_callback(self.set_write)
            requests_in_flight.append(async_result)
        [ar.wait() for ar in requests_in_flight]

    def set_write(self, async_result):
        '''
        Callback function for the write requests. 
        Takes in a rpyc.AsyncResult object as parameter,
        getting its value and setting the write token if 
        permission was granted.
        '''

        primary_id, had_token, permission_granted = async_result.value
        if had_token:
            debug_sentence = f"[DEBUG] Replica {primary_id} had the write token "
            if permission_granted:
                debug_sentence += "and granted it!"
                with self.LOCK:
                    self.can_write = True
                    self.permission_granted_event.set()
            else:
                debug_sentence += f"and did not grant it! Mean replica {primary_id}! :("
            debug(self.DEBUG_MODE, debug_sentence)

    def exposed_ask_for_write_permission(self):
        '''
        Releases write token if belonged to this replica and all of the local
        changes were committed. Returns a 3-tuple (int, bool, bool)
        containing respectively the local replica ID, a boolean saying whether 
        it had or not the token and another boolean representing the permission grant.
        '''
        
        with self.LOCK:
            #check if local changes are committed
            had_token = self.can_write
            if self.can_write and self.changes_committed:
                self.can_write = False
                return (self.id, had_token, True)
            return (self.id, had_token, False)
    
    def exposed_commit_changes(self):
        '''
        Commits local changes, making the write token free to whoever asks for it.
        '''

        #TODO: think of a way not to hold this lock for that long
        with self.LOCK:
            if not self.changes_committed:
                self.broadcast_updates()
                self.uncommitted_history = []
                self.changes_committed = True
    
    def broadcast_updates(self):
        '''
        Asynchronously sends the uncommitted updates to all other replicas, along
        with the local replica ID and the latest value of X.
        '''

        #assumes replicas will never fail and will all be available when requested
        #TODO: handle possible errors in a better way
        confirmations = [False for peer in self.peer_connections]
        while not all(confirmations):
            requests_in_flight = []

            for i in range(len(self.peer_connections)):
                if confirmations[i] == False:
                    port = self.peer_connections[i]
                    conn = rpyc.connect("localhost", port=port)
                    replicate_changes_async = rpyc.async_(conn.root.replicate_changes)
                    ar_obj = replicate_changes_async(self.id, self.X, self.uncommitted_history)
                    async_request = (i, ar_obj)
                    requests_in_flight.append(async_request)

            for confirmation_id, ar_obj in requests_in_flight:
                confirmations[confirmation_id] = ar_obj.value

    def exposed_replicate_changes(self, primary_id, new_X, new_changes):
        '''
        Function that receives the pushed changes from the primary and 
        updates all local variables accordingly. Returns True to acknowledge
        for the primary that the update operation went successfully.        
        '''

        debug(self.DEBUG_MODE, f"[DEBUG] Received push from replica {primary_id} containing value {new_X} as a result of {len(new_changes)} new change(s)")
        
        with self.LOCK:
            self.X = new_X
            self.history.extend(new_changes)
        return True

    def __set_local(self, value: int):
        '''
        Sets local X to new value and inserts new update operation into the history array.
        Unsets the committed state variable.
        '''

        debug(self.DEBUG_MODE, f"[DEBUG] Changing X from {self.X} to {value}")
        self.X = value
        history_entry = (self.id, value)
        self.history.append(history_entry)
        self.uncommitted_history.append(history_entry)
        self.changes_committed = False
