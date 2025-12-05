# Pacman AI: Python Implementation

## 📌 Project Overview

This repository features a fully functional **Pacman clone** built from scratch using Python and the **Pygame** library. The project demonstrates the implementation of **Artificial Intelligence** in a real-time arcade environment, featuring both a utility-based autonomous agent and algorithmic enemy tracking.

The game offers two distinct modes: a classic **Human Player** mode and a fully autonomous **AI Mode** where Pacman plays by itself using a decision-making algorithm.

## 🚀 Key Features

### 🧠 Intelligent Agents

  * **AI Pacman (Utility-Based Agent):** The agent calculates a "utility score" for every possible move in real-time. It prioritizes food and energy pellets while heavily penalizing directions that lead to ghosts or dead ends. It also includes a memory system to prevent repetitive looping.
  * **Ghost AI (Pathfinding):** Ghosts act as "Chasers," using **Breadth-First Search (BFS)** to calculate the shortest path to the player through the maze walls, making them formidable opponents.
  * **Dynamic Behavior:** Ghosts switch between "Chase" and "Scared" (Random Walk) modes when Pacman consumes an energy pellet.

### 🎮 Game Engine

  * **Procedural Sound Generation:** The game generates sound effects (beeps) mathematically using Python's `wave` and `struct` libraries, removing the need for external audio files.
  * **State Management:** Handles menu states, game loops, win/loss conditions, and score tracking seamlessly.
  * **Collision System:** Pixel-perfect collision detection for walls, collectibles, and entities.

## 🛠 Installation & Usage

### Prerequisites

Ensure you have Python installed. The only external dependency is `pygame`.

```bash
pip install pygame
```

### Running the Game

Clone the repository and run the main script:

```bash
git clone https://github.com/M-Eness/Utility-Based-Pacman.git
cd Utility-Based-Pacman
python pacman.py
```

### 🕹 Controls & Modes

Upon running the game, you will be greeted with a main menu:

  * **Press `1` - Human Mode:**
      * Control Pacman manually using the **Arrow Keys**.
      * Goal: Eat all dots and avoid ghosts.
  * **Press `2` - AI Mode:**
      * Watch the **Utility Agent** play the game autonomously.
      * Observe how the AI makes decisions to avoid ghosts and clear the map.

## 📂 Project Structure

```text
.
├── pacman.py           # The complete game engine, AI logic, and main loop
└── beep.wav            # Sound file (Auto-generated on first run)
```

## 🧠 Code Highlights

The project showcases several core CS concepts:

  * **Graph Theory:** Managing grid-based movement and wall collision.
  * **Search Algorithms:** BFS implementation for enemy pathfinding.
  * **Heuristics:** Manhattan distance calculations for the AI's utility function.
  * **Object-Oriented Programming:** Modular class structure for `PacmanAgent`, `Ghost`, and `Game` engine.

## 📜 License

This project is open-source and available under the MIT License.
