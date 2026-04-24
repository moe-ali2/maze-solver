# maze-solver

A simple interactive maze solver built with Python and Pygame.
The AI agent finds the shortest path on a 10x10 grid using BFS or A*.

---

## Files

| File       | Purpose                          |
|------------|----------------------------------|
| `main.py`  | Agent logic, grid, and game loop |
| `ui.py`    | Grid and panel drawing           |

---

Agent
Type: Goal-Based Agent (AIMA model)
Algorithms: BFS · A*
Goal: Find the shortest path from S to G

## Controls

| Key         | Action              |
|-------------|---------------------|
| `1`         | Draw mode: Wall     |
| `2`         | Draw mode: Erase    |
| `3`         | Draw mode: Start    |
| `4`         | Draw mode: Goal     |
| `B`         | Switch to BFS       |
| `A`         | Switch to A*        |
| `-`         | Speed: Slow         |
| `N`         | Speed: Normal       |
| `=`         | Speed: Fast         |
| `SPACE`     | Start the agent     |
| `C`         | Clear all walls     |
| `R`         | Reset the grid      |


## How to Run

### 1. Install dependencies
```bash
pip install pygame
python main.py
