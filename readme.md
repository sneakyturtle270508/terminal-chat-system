
made by chatgpt 
the ideas by William

# Complete Build Guide: LAN Chat System

## Table of Contents
1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [System Architecture](#system-architecture)
4. [Setup Instructions](#setup-instructions)
5. [File Structure](#file-structure)
6. [Building the Server](#building-the-server)
7. [Building the Client](#building-the-client)
8. [Testing the System](#testing-the-system)
9. [Troubleshooting](#troubleshooting)
10. [Advanced Configuration](#advanced-configuration)

## Overview

This LAN Chat System is a Python-based client-server application that allows multiple users to communicate in chat rooms over a local area network. The system features automatic server discovery, room-based communication, and comprehensive server administration tools.

### Key Features
- **Automatic Server Discovery**: Clients automatically find the server using UDP broadcast
- **Room-based Chat**: Users join specific rooms using PIN codes
- **Server Administration**: Complete control over rooms, users, and server state
- **Multi-threading**: Handles multiple clients simultaneously
- **Real-time Communication**: Instant message delivery within rooms
- **Activity Logging**: Tracks all server activities and user actions

## Prerequisites

### Software Requirements
- **Python 3.6 or higher**
- **Operating System**: Windows, macOS, or Linux
- **Network**: All devices must be on the same LAN/subnet

### Python Modules Used
All modules are part of Python's standard library:
- `socket` - Network communication
- `threading` - Concurrent operations
- `time` - Timing functions
- `os` - Operating system interface

### Network Requirements
- Open UDP port 5001 (for server discovery)
- Open TCP port 5000 (for chat communication)
- Firewall configured to allow these ports
- All devices on same subnet (e.g., 192.168.1.x)

## System Architecture

```
┌─────────────────┐     UDP Broadcast     ┌─────────────────┐
│     CLIENT      │◄─────────────────────►│     SERVER      │
│                 │      (Port 5001)      │                 │
│  - Discovery    │                       │  - Discovery    │
│  - Chat Input   │     TCP Connection    │  - User Mgmt    │
│  - Message RX   │◄─────────────────────►│  - Room Mgmt    │
└─────────────────┘      (Port 5000)      │  - Broadcasting │
                                          │  - Admin Tools  │
                                          └─────────────────┘
```

### Communication Flow
1. **Discovery Phase**: Client broadcasts UDP packet to find server
2. **Connection Phase**: Client establishes TCP connection to server
3. **Authentication Phase**: Client provides PIN and username
4. **Chat Phase**: Real-time message exchange within rooms

## Setup Instructions

### Step 1: Create Project Directory
```bash
mkdir lan-chat-system
cd lan-chat-system
```

### Step 2: Create Server File
Create `server.py` with the provided server code.

### Step 3: Create Client File
Create `client.py` with the provided client code.

### Step 4: Verify Python Installation
```bash
python --version
# or
python3 --version
```

### Step 5: Test File Execution
```bash
python server.py
python client.py
```

## File Structure

```
lan-chat-system/
├── server.py          # Server application
├── client.py          # Client application
├── README.md          # This guide
└── docs/
    └── documentation.md   # Detailed documentation
```

## Building the Server

### Core Components

#### 1. Network Setup
The server listens on two ports:
- **Port 5000 (TCP)**: Main chat communication
- **Port 5001 (UDP)**: Server discovery broadcasts

#### 2. Data Structures
```python
rooms = {}  # {pin: [{"conn": conn, "name": name}, ...]}
log = []    # Activity log with MAX_LOG entries
```

#### 3. Server States
- **server_running**: Master control for entire server
- **server_active**: Controls new client acceptance
- **server_stopped**: Blocks message processing

### Key Functions Explained

#### UDP Discovery Handler
```python
def udp_discovery():
    # Listens for "DISCOVER_SERVER" broadcasts
    # Responds with "SERVER_HERE" to announce presence
```

#### Client Handler
```python
def handle_client(conn, addr):
    # 1. Check if server accepts new clients
    # 2. Get PIN and username from client
    # 3. Add client to appropriate room
    # 4. Handle ongoing message relay
    # 5. Clean up on disconnect
```

#### Administrative Dashboard
```python
def print_dashboard(show_help=False):
    # Displays current server state
    # Shows active rooms and users
    # Provides command interface
```

## Building the Client

### Core Components

#### 1. Server Discovery
```python
def discover_server(timeout=5):
    # Broadcasts UDP packet to find server
    # Returns server IP or None if not found
```

#### 2. Message Reception
```python
def receive(sock):
    # Continuously listens for server messages
    # Runs in separate thread for non-blocking operation
```

#### 3. Main Communication Loop
- Connects to discovered server
- Starts receive thread
- Handles user input and message sending

### Client Flow
1. **Discovery**: Broadcast to find server
2. **Connection**: Establish TCP connection
3. **Setup**: Provide PIN and username
4. **Communication**: Send/receive messages
5. **Cleanup**: Handle disconnection gracefully

## Testing the System

### Basic Testing Steps

#### 1. Start the Server
```bash
python server.py
```
Expected output:
```
=== SERVER DASHBOARD ===
Server aktiv for nye klienter: False
Server stoppet (meldinger blokkert): False
Ingen aktive rom.

Skriv /help for kommandoer.

Server klar. Bruk /start for å aktivere. /help for kommandoer.
Server> 
```

#### 2. Activate the Server
Type `/start` in server console:
```
Server> /start
[Server] Serveren startet. Nye klienter og meldinger OK.
```

#### 3. Start Client
Open new terminal:
```bash
python client.py
```
Expected output:
```
[Klient] Fant server på 192.168.1.100
[Klient] Koble til server 192.168.1.100:5000
Skriv inn PIN for rommet du vil bli med i: 
```

#### 4. Join Room
Enter a PIN (e.g., "1234") and username (e.g., "TestUser")

#### 5. Test Communication
Type messages in client terminal - they should appear to all users in the same room.

### Multi-Client Testing
1. Start multiple client instances
2. Have some join the same room (same PIN)
3. Have others join different rooms (different PINs)
4. Verify message isolation between rooms

### Server Administration Testing
Test all server commands:
- `/start` - Activate server
- `/standby` - Block new clients
- `/stop` - Block all messages
- `/room <PIN>` - Close a room
- `/room <PIN> <user>` - Kick a user
- `/logg` - View activity log
- `/help` - Show help

## Troubleshooting

### Common Issues and Solutions

#### Server Discovery Fails
**Problem**: Client shows "Fant ingen server på LAN"
**Solutions**:
- Ensure server is running and activated (`/start`)
- Check firewall settings (allow UDP 5001)
- Verify devices are on same subnet
- Try manual IP entry in client code

#### Connection Refused
**Problem**: Client can discover but can't connect
**Solutions**:
- Check if TCP port 5000 is blocked
- Ensure server is in active state
- Verify server isn't in standby mode

#### Messages Not Appearing
**Problem**: Messages sent but not received
**Solutions**:
- Check if server is stopped (`/stop` command)
- Verify users are in same room (same PIN)
- Ensure client receive thread is running

#### Server Commands Not Working
**Problem**: Server commands don't execute
**Solutions**:
- Ensure exact command syntax (case-sensitive)
- Check for typos in command names
- Verify server isn't completely stopped

### Network Troubleshooting

#### Check Network Connectivity
```bash
# Ping other devices
ping 192.168.1.100

# Check if ports are open (Linux/Mac)
netstat -an | grep 5000
netstat -an | grep 5001
```

#### Firewall Configuration
**Windows**:
- Open Windows Defender Firewall
- Allow Python through firewall
- Create inbound rules for ports 5000-5001

**Linux**:
```bash
sudo ufw allow 5000
sudo ufw allow 5001
```

**macOS**:
- System Preferences → Security & Privacy → Firewall
- Add Python to allowed applications

## Advanced Configuration

### Customizing Ports
Modify these constants in both files:
```python
PORT = 5000          # TCP chat port
BROADCAST_PORT = 5001 # UDP discovery port
```

### Adjusting Timeouts
```python
# In client.py
def discover_server(timeout=5):  # Discovery timeout
client.settimeout(timeout)

# In server.py
server.settimeout(1.0)  # Accept timeout
```

### Modifying Buffer Sizes
```python
# Increase for larger messages
msg = sock.recv(1024)  # Change 1024 to larger value
```

### Adding Authentication
Consider implementing:
- Password protection for rooms
- User authentication system
- Encrypted communication (SSL/TLS)

### Scaling Considerations
- **Maximum Clients**: Limited by system resources
- **Message Size**: Currently 1024 bytes
- **Room Capacity**: No built-in limits
- **Performance**: Suitable for small to medium LANs

### Security Enhancements
- Input validation and sanitization
- Rate limiting for messages
- Connection limits per IP
- Logging and monitoring improvements

## Deployment Options

### Single Machine Testing
Run server and multiple clients on same computer using different terminals.

### LAN Deployment
1. Run server on dedicated machine
2. Distribute client.py to all user machines
3. Ensure network connectivity
4. Configure firewalls appropriately

### Virtual Environment Setup
```bash
# Create virtual environment
python -m venv chat-env

# Activate (Windows)
chat-env\Scripts\activate

# Activate (Linux/Mac)
source chat-env/bin/activate

# Run applications
python server.py
python client.py
```

This completes the comprehensive build guide for the LAN Chat System. The system is ready for deployment and can be extended with additional features as needed.