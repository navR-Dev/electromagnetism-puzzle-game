# Electromagnetism Puzzle Game

A real-time interactive physics sandbox that visualizes electric and magnetic fields using heterogeneous parallelism (CPU + GPU). Built with **Python**, accelerated by **PyOpenCL**, and rendered via **Pygame**.

---

## Features

- **Free Play Mode**  
  Drop positive and negative charges or magnetic loops anywhere on the screen to generate dynamic field lines.

- **Electromagnetic Field Simulation**  
  Calculates electric and magnetic fields based on user input using physically inspired formulas.

- **GPU-Accelerated Physics**  
  Uses **PyOpenCL** for fast parallel computation of vector fields on supported devices.

- **CPU-Based Rendering**  
  Optimized vector field rendering using parallel loops for smooth and responsive visuals.

- **Interactive UI**  
  Simple click-based system to add elements and experiment freely.

---

## Project Structure

electromagnetism-puzzle-game/ <br>
└── src/<br>
├── main.py # Entry point of the game<br>
├── game.py # Main game loop and interaction logic<br>
├── ui.py # UI rendering (menus, overlays)<br>
└── physics.py # Physics engine using OpenCL<br>

---

## How To Run

1. Download the code and extract to any directory
2. Navigate to the code in an administrator terminal window
3. Install the required libraries using `pip install -r requirements.txt`
4. Run the code by entering the command `run.bat`

---
