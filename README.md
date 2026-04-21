# Impostor Game - Client/Server Project

## 🚀 Introduction
In this project we will build an impostor-style game using a client/server architecture. The goal is to simulate communication between multiple clients and a centralized server, allowing players to interact in real time within the game environment.

## 🎮 Game Description
It's a word-deduction game where participants receive a secret word, except for one, who is the imposter. The goal is to discover the imposter, who must disguise themselves and guess the word to avoid being voted out.

## ⚙️ Project Description
This project is developed using a client/server model. The server is implemented in the C programming language and runs inside a Linux-based Docker container. It is responsible for handling connections, managing game logic, and coordinating communication between clients.

The client application runs on a Windows environment and connects to the server using sockets. It is responsible for user interaction, sending player actions to the server, and receiving updates about the game state.

## 💻 Technologies Used
- C (Server-side development)
- Python (Client-side development)
- Docker (Linux container for server execution)
- Sockets (Network communication)

## 📦 Features
- Real-time communication between client and server
- Multiple client connections handled by the server
- Game state synchronization
- Basic impostor game mechanics

## ❓ How It Works
1. The server is started inside a Docker container.
2. The client application is executed on a Windows machine.
3. Clients connect to the server using sockets.
4. The server processes incoming requests and updates the game state.
5. Clients receive updates and reflect changes in the user interface.


## Prerequisites
- Docker installed on your system
- Python 3.x installed on your Windows machine
- Git (optional, for cloning the project)

## Step-by-Step Execution

### 1. Start the Server Inside Docker Container

First, ensure your Docker container has the `server` folder containing `server.c` and the passwords file.

**Inside the Docker container (Linux environment):**

```bash
# Navigate to the server folder
cd /path/to/server

# Compile the server code
gcc server.c -o server

# Run the server
./server
```

> The server will start listening for client connections. Keep this terminal running.

### 2. Set Up and Run the Client (Windows)

Open a new **Command Prompt** or **PowerShell** window and navigate to the game folder containing `main.py`:

```bash
cd C:\path\to\game\folder
```

#### Create a virtual environment:

```bash
python -m venv venv
```

#### Activate the virtual environment:


**On PowerShell:**
```bash
.\venv\Scripts\activate
```
> You should see `(venv)` appear at the beginning of the command line.

#### Install the required library:

```bash
pip install customtkinter
```

#### Run the game client:

```bash
python main.py
```

### 3. Play the Game

Once the client connects to the server, the impostor game interface will appear. Follow the on-screen instructions to play.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `python` not recognized | Make sure Python is added to your PATH |
| `customtkinter` import error | Run `pip install customtkinter` again inside the activated venv |
| Server connection refused | Check that the server is running inside Docker and the port is exposed correctly |
| Virtual environment activation fails on PowerShell | Run `Set-ExecutionPolicy RemoteSigned` first on administrator level before and try again|

## Notes
- The server must be running **before** you launch the client and running on the port 5000 of the docker container.
- Keep the Docker container active throughout the gaming session.
- The passwords file must be in the same directory as `server.c` for authentication to work.
