## Distributed Systems

This repository contains work developed during the undergraduation course of Distributed Systems, taught in 2020 at UFRJ.

The projects are incrementally distributed among several assignments, for each folder in this repository. 

- lab1
    - Contains a simple echo client/server; a distributed systems' version of a Hello World program.
- lab2
    - A client/server application that involves counting words from a file (located in the server) that is selected by the client. 
    The purpose of this assignment was to exercise not only the development of an application with the client/server model, but also to design a layered architecture.
- lab3
    - This assignment directly extends the previous, enhancing the server logic by making two versions of it: a properly iterative one and a concurrent one. The iterative (which was also the case of the original) gains the ability to handle connections with multiple clients (although the processing itself is still synchronous), whereas the concurrent implementation is, as the name implies, fully concurrent, doing the processing in another thread.