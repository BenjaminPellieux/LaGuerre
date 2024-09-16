
# LaGuerre

LaGuerre is a Python-based strategy game combining elements of network communication, artificial intelligence, and cybersecurity techniques. The project implements game mechanics with multiplayer capabilities and integrates basic hacking and cybersecurity challenges.

## Features

### 1. **Game Logic & AI (Algo/Dev)**
   - **Network & Server**: Multiplayer communication between clients and server, handling requests and managing player interactions.
   - **AI**: Implementation of AI strategies for in-game decision-making, including pathfinding and tactical algorithms.
   - **Pathfinding**: Efficient algorithms to determine optimal movement and decision paths for game entities.
   - **Game Algorithms**: Contains decision-making processes that power the game's internal mechanics.

### 2. **Cybersecurity (Hack/Cyber)**
   - **Basic Linux Commands**: Explores various command-line operations crucial for basic server management and system operations.
   - **Reverse Engineering**: Introduces techniques for understanding compiled code and working with binary data.
   - **Steganography**: Implements methods for hiding and extracting data within various file formats (e.g., images, audio files).

## Prerequisites

To run the project, ensure the following dependencies are installed:

- **Python 3.6+**
- Necessary Python libraries (listed in `requirements.txt` if available)

Install dependencies with:
```bash
pip install -r requirements.txt
```

## How to Run

1. **Clone the repository**:
   ```bash
   git clone https://github.com/BenjaminPellieux/LaGuerre.git
   ```
   
2. **Navigate to the project directory**:
   ```bash
   cd LaGuerre
   ```

3. **Launch the game interface**:
   ```bash
   python Interface.py
   ```

4. **Run a test client for multiplayer**:
   ```bash
   python Client.py
   ```

## Project Structure

- **Algo/**: Contains core algorithms for AI, pathfinding, and network logic for multiplayer gameplay.
- **hack/**: Houses various scripts and challenges related to cybersecurity, including Linux commands, reverse engineering, and steganography.
- **Interface.py**: Main script for launching the graphical interface of the game.
- **Client.py & Client2.py**: Test clients used for simulating network interactions in the multiplayer mode.
- **sujet.md**: Documentation of the project's goals and a detailed explanation of features.
- **out.pdf**: Report providing further details on game mechanics and design strategy.

## Cybersecurity Section (`hack/`)
This section focuses on various hacking and cyber-related challenges:
- **Linux Commands**: Basic server commands for network management and file manipulation.
- **Reverse Engineering**: Techniques for analyzing and understanding low-level code and binaries.
- **Steganography**: Exercises in hiding and extracting hidden information within files.

## License
This project is licensed under the MIT License.

