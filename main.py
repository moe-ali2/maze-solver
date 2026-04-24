
import pygame, sys, heapq, time
from collections import deque
from ui import draw_grid, draw_panel, DGRAY, RED, BLUE
 
# Constants
 
ROWS, COLS  = 10, 10
CELL        = 60
PANEL_W     = 260
WIDTH       = COLS * CELL + PANEL_W
HEIGHT      = ROWS * CELL
 
EMPTY, WALL, START, GOAL = ".", "#", "S", "G"
SPEEDS = {"Slow": 300, "Normal": 150, "Fast": 40}
 
 
# Grid helpers
 
def make_grid():
    """Return a blank grid with S at top-left and G at bottom-right."""
    grid = [[EMPTY] * COLS for _ in range(ROWS)]
    grid[0][0]               = START
    grid[ROWS - 1][COLS - 1] = GOAL
    return grid
 
 
def find(grid, symbol):
    """Return (row, col) of a symbol, or None if not found."""
    for r, row in enumerate(grid):
        for c, cell in enumerate(row):
            if cell == symbol:
                return (r, c)
    return None
 
 
def neighbors(grid, row, col):
    """Yield walkable neighbors in 4 directions (up/down/left/right)."""
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nr, nc = row + dr, col + dc
        if 0 <= nr < ROWS and 0 <= nc < COLS and grid[nr][nc] != WALL:
            yield nr, nc
 
 
# Agent
 
class Agent:
    def __init__(self, start, goal, algo, grid):
        self.pos    = start
        self.goal   = goal
        self.algo   = algo
        self.grid   = grid
        self.visited = {start}        # cells seen so far
        self.parent  = {start: None}  # used to reconstruct the final path
        self.path    = []
        self.done    = False
        self.found   = False
 
        if algo == "BFS":
            self.queue = deque([start])
        else:  # A*
            self.g_cost        = {start: 0}
            self.expanded      = set()
            self.priority_queue = [(self.heuristic(start), 0, start)]
 
    def heuristic(self, cell):
        """Manhattan distance from cell to goal (used by A*)."""
        return abs(cell[0] - self.goal[0]) + abs(cell[1] - self.goal[1])
 
    def build_path(self):
        """Trace parent links backwards to build the solution path."""
        path, current = [], self.goal
        while current:
            path.append(current)
            current = self.parent[current]
        self.path = path[::-1]  # reverse so path goes start → goal
 
    def step(self):
        """Advance the agent by one step: Perceive → Think → Act."""
        if self.done:
            return
 
        if self.algo == "BFS":
            if not self.queue:
                self.done = True
                return
            current = self.queue.popleft()
            self.pos = current
            self.visited.add(current)
 
            if current == self.goal:
                self.found = self.done = True
                self.build_path()
                return
 
            for neighbor in neighbors(self.grid, *current):
                if neighbor not in self.parent:
                    self.parent[neighbor] = current
                    self.queue.append(neighbor)
 
        else:  # A*
            # Skip cells that were already expanded (stale heap entries)
            while self.priority_queue and self.priority_queue[0][2] in self.expanded:
                heapq.heappop(self.priority_queue)
 
            if not self.priority_queue:
                self.done = True
                return
 
            _, cost, current = heapq.heappop(self.priority_queue)
            self.expanded.add(current)
            self.pos = current
            self.visited.add(current)
 
            if current == self.goal:
                self.found = self.done = True
                self.build_path()
                return
 
            for neighbor in neighbors(self.grid, *current):
                new_cost = cost + 1
                if new_cost < self.g_cost.get(neighbor, float("inf")):
                    self.g_cost[neighbor] = new_cost
                    self.parent[neighbor] = current
                    self.visited.add(neighbor)
                    heapq.heappush(
                        self.priority_queue,
                        (new_cost + self.heuristic(neighbor), new_cost, neighbor)
                    )
 
 
#  Main 
 
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Maze Solver")
 
    font_small = pygame.font.SysFont("monospace", 14)
    font_bold  = pygame.font.SysFont("monospace", 14, bold=True)
    clock      = pygame.time.Clock()
 
    grid         = make_grid()
    mode         = "Wall"
    algo         = "BFS"
    speed        = "Normal"
    agent        = None
    running      = False
    last_tick    = 0
    mouse_pressed = False
    start_time   = None
 
    stats = {
        "msg"    : "Draw walls then press SPACE",
        "msg_color": DGRAY,
        "found"  : None,
        "steps"  : 0,
        "visited": 0,
        "elapsed": 0.0,
    }
 
    def reset():
        nonlocal agent, running, last_tick, start_time
        agent = None
        running = False
        last_tick = 0
        start_time = None
        stats.update(msg="", msg_color=DGRAY, found=None,
                     steps=0, visited=0, elapsed=0.0)
 
    def launch():
        """Start the agent when SPACE is pressed."""
        nonlocal agent, running, last_tick, start_time
        if running:
            return
        start = find(grid, START)
        goal  = find(grid, GOAL)
        if not start or not goal:
            stats.update(msg="Place S and G first!", msg_color=RED)
            return
        reset()
        agent      = Agent(start, goal, algo, grid)
        running    = True
        last_tick  = pygame.time.get_ticks()
        start_time = time.time()
        stats.update(msg=f"Exploring ({algo})...", msg_color=BLUE, found=None)
 
    def handle_click(mx, my):
        """Place or erase cells on mouse click."""
        if running or not (0 <= mx < COLS * CELL and 0 <= my < HEIGHT):
            return
        r, c = my // CELL, mx // CELL
        if not (0 <= r < ROWS and 0 <= c < COLS):
            return
        cell = grid[r][c]
        if   mode == "Wall"  and cell == EMPTY:
            grid[r][c] = WALL
        elif mode == "Erase" and cell == WALL:
            grid[r][c] = EMPTY
        elif mode == "Start" and cell not in (START, GOAL):
            old = find(grid, START)
            if old:
                grid[old[0]][old[1]] = EMPTY
            grid[r][c] = START
        elif mode == "Goal"  and cell not in (START, GOAL):
            old = find(grid, GOAL)
            if old:
                grid[old[0]][old[1]] = EMPTY
            grid[r][c] = GOAL
 
    # Game loop
    while True:
        clock.tick(60)
        now = pygame.time.get_ticks()
 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
 
            if event.type == pygame.KEYDOWN:
                key = event.key
                if   key == pygame.K_1:      mode  = "Wall"
                elif key == pygame.K_2:      mode  = "Erase"
                elif key == pygame.K_3:      mode  = "Start"
                elif key == pygame.K_4:      mode  = "Goal"
                elif key == pygame.K_b:      algo  = "BFS"
                elif key == pygame.K_a:      algo  = "A*"
                elif key == pygame.K_MINUS:  speed = "Slow"
                elif key == pygame.K_n:      speed = "Normal"
                elif key == pygame.K_EQUALS: speed = "Fast"
                elif key == pygame.K_SPACE:  launch()
                elif key == pygame.K_c and not running:
                    for r in range(ROWS):
                        for c in range(COLS):
                            if grid[r][c] == WALL:
                                grid[r][c] = EMPTY
                    reset()
                    stats.update(msg="Walls cleared.", msg_color=DGRAY)
                elif key == pygame.K_r and not running:
                    grid = make_grid()
                    reset()
                    stats.update(msg="Grid reset.", msg_color=DGRAY)
 
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pressed = True
                handle_click(*event.pos)
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mouse_pressed = False
            if event.type == pygame.MOUSEMOTION and mouse_pressed:
                handle_click(*event.pos)
 
        if running and agent and (now - last_tick) >= SPEEDS[speed]:
            last_tick = now
            if not agent.done:
                agent.step()
            else:
                running = False
                elapsed = round(time.time() - start_time, 2)
                if agent.found:
                    stats.update(found=True,
                                 steps=len(agent.path) - 1,
                                 visited=len(agent.visited),
                                 elapsed=elapsed)
                else:
                    stats.update(found=False,
                                 visited=len(agent.visited),
                                 elapsed=elapsed)
 
        # Draw everything
        screen.fill((245, 245, 245))
        draw_grid(screen, font_small, grid, agent, ROWS, COLS, CELL)
        draw_panel(screen, font_small, font_bold,
                   mode, algo, speed, stats, COLS, CELL, PANEL_W, HEIGHT)
        pygame.display.flip()
 
 
if __name__ == "__main__":
    main()
