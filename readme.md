# Snake 3D

A modern, OpenGL-powered interpretation of the classic Snake game.

This project was developed as a final assignment for the 3D Computer Graphics course. It goes beyond simple 2D rendering by introducing a fully 3D environment, dynamic lighting, custom shaders, and complex coordinate mapping on a 3D cube.

## Game Modes

### 1. Planar Mode (The Classic)
A tribute to the original game, but placed in a 3D space.

Experience: Play on a flat surface with depth perception.  
Camera: Use the orbital camera to inspect the board from different angles while playing.  
Visuals: Dynamic shadows and lighting that react to the snake's position.

### 2. Cube Mode (The Challenge)
This mode changes the rules of geometry. The snake moves on the surface of a rotating cube.

The Challenge: The snake wraps around edges.
Math: Implements complex topology transitions to map 2D grid logic onto a 3D manifold seamlessly.

## Technical Highlights

This project demonstrates various computer graphics concepts:

- Custom GLSL Shaders  
  The food object (apple) uses custom vertex and fragment shaders to create a pulsating animation and per-pixel lighting effects that operate outside the fixed pipeline.

- Phong Lighting Model  
  The scene is lit by dynamic point lights attached to the snake's head and the apple, creating an immersive atmosphere.

- Tessellated Geometry  
  The floor and cube faces are tessellated to ensure lighting calculations (Gouraud/Phong) look smooth even near the edges.

## Requirements

- Python 3.11+
- Pygame (window management and input)
- PyOpenGL (graphics API bindings)

## Installation and Running

1. Clone the repository or extract the source code.
2. Install required dependencies (recommended to use a virtual environment):

   pip install -r requirements.txt

3. Run the game:

   python main.py

## Controls

| Context | Key | Action |
|--------|-----|--------|
| Menu | 1 | Start Planar Mode |
| Menu | 2 | Start Cube Mode |
| Movement | Arrow Left / Right | Turn Snake Left / Right (relative to head) |
| Camera | W / S | Rotate Camera Up / Down |
| Camera | A / D | Rotate Camera Left / Right |
| Camera | Q / E | Zoom In / Out |
| General | ESC | Return to Menu / Exit |

## Project Structure

- main.py  
  Entry point. Handles the game loop, state machine (Menu/Game/GameOver), and texture loading.

- logic_2d.py  
  Contains the logic for the Cube mode, including the edge-transition dictionary (CUBE_TRANSITIONS).

- logic_cube.py  
  Logic for the standard flat mode.

- graphics.py  
  Abstraction layer for OpenGL calls (drawing cubes, handling lights, rendering the HUD).

- utils.py  
  Math helpers (matrices, rotation) and shader compilation tools.

- pulse.vert / pulse.frag  
  GLSL code for the animated apple.

- config.py  
  Configuration constants.

## Demo
