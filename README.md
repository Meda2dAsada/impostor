# Impostor Game - Client/Server Project

## Introduction
In this project we will build an impostor-style game using a client/server architecture. The goal is to simulate communication between multiple clients and a centralized server, allowing players to interact in real time within the game environment.

## Project Description
This project is developed using a client/server model. The server is implemented in the C programming language and runs inside a Linux-based Docker container. It is responsible for handling connections, managing game logic, and coordinating communication between clients.

The client application runs on a Windows environment and connects to the server using sockets. It is responsible for user interaction, sending player actions to the server, and receiving updates about the game state.

## Technologies Used
- C (Server-side development)
- Python (Client-side development)
- Docker (Linux container for server execution)
- Sockets (Network communication)

## Features
- Real-time communication between client and server
- Multiple client connections handled by the server
- Game state synchronization
- Basic impostor game mechanics

## How It Works
1. The server is started inside a Docker container.
2. The client application is executed on a Windows machine.
3. Clients connect to the server using sockets.
4. The server processes incoming requests and updates the game state.
5. Clients receive updates and reflect changes in the user interface.