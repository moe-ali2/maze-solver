import pygame

WHITE  = (255, 255, 255)
BLACK  = (30,  30,  30)
GRAY   = (180, 180, 180)
LGRAY  = (220, 220, 220)
DGRAY  = (60,  60,  60)
PANEL_BG = (235, 238, 242)
GREEN  = (34,  197,  94)
RED    = (220,  60,  60)
BLUE   = (59,  130, 246)
DBLUE  = (30,   80, 180)
LBLUE  = (186, 230, 253)
YELLOW = (250, 204,  21)

EMPTY, WALL, START, GOAL = ".",

def draw_grid(screen, font, grid, agent, ROWS, COLS, CELL):

    path_cells = set(agent.path)    if agent else set()
    visited    = agent.visited      if agent else set()
    agent_pos  = agent.pos          if agent else None

    for r in range(ROWS):
        for c in range(COLS):
            element, temp     = c * CELL, r * CELL
            cell     = grid[r][c]
            position = (r, c)

            if   cell == START:          color = GREEN
            elif cell == GOAL:           color = RED
            elif cell == WALL:           color = BLACK
            elif position in path_cells: color = YELLOW
            elif position in visited:    color = LBLUE
            else:                        color = WHITE

            pygame.draw.rect(screen, color, (element, temp, CELL, CELL))
            pygame.draw.rect(screen, LGRAY, (element, temp, CELL, CELL), 1)

            if cell in (START, GOAL):
                label = font.render(cell, True, WHITE)
                screen.blit(label, label.get_rect(center=(element + CELL // 2, temp + CELL // 2)))

    if agent_pos:
        cx  = agent_pos[1] * CELL + CELL // 2
        cy  = agent_pos[0] * CELL + CELL // 2
        rad = CELL // 2 - 8
        pygame.draw.circle(screen, DBLUE, (cx, cy), rad + 3)
        pygame.draw.circle(screen, BLUE,  (cx, cy), rad)

def draw_panel(screen, font, font_bold, mode, algo, speed, stats, COLS, CELL, PANEL_W, HEIGHT):

    panel_x = COLS * CELL

    pygame.draw.rect(screen, PANEL_BG, (panel_x, 0, PANEL_W, HEIGHT))
    pygame.draw.line(screen, GRAY, (panel_x, 0), (panel_x, HEIGHT), 2)

    def text(content, temp, color=DGRAY, bold=False):

        f = font_bold if bold else font
        screen.blit(f.render(content, True, color), (panel_x + 12, temp))

    def divider(temp):

        pygame.draw.line(screen, GRAY, (panel_x + 8, temp), (panel_x + PANEL_W - 8, temp), 1)

    temp = 10
    text("Maze Solver", temp, BLUE, bold=True); temp += 22
    divider(temp); temp += 8

    controls = [
        ("DRAW MODE", [("1", "Wall"), ("2", "Erase"), ("3", "Start"), ("4", "Goal")], mode),
        ("ALGORITHM", [("B", "BFS"),  ("A", "A*")],                                   algo),
        ("SPEED",     [("-", "Slow"), ("N", "Normal"), ("=", "Fast")],                 speed),
    ]
    for title, options, active in controls:
        text(f"-- {title} --", temp, GRAY); temp += 18
        for key, name in options:
            color = BLUE if name == active else DGRAY
            text(f"[{key}] {name}", temp, color); temp += 18
        temp += 4; divider(temp); temp += 8

    text("-- ACTIONS --", temp, GRAY); temp += 18
    for line in ["[SPACE] Start", "[C] Clear", "[R] Reset"]:
        text(line, temp); temp += 18
    temp += 4; divider(temp); temp += 8

    text("-- LEGEND --", temp, GRAY); temp += 18
    legend = [
        (WHITE,  "Empty"),
        (BLACK,  "Wall"),
        (LBLUE,  "Visited"),
        (YELLOW, "Path"),
        (BLUE,   "Agent"),
    ]
    for color, label in legend:
        pygame.draw.rect(screen, color, (panel_x + 12, temp + 2, 13, 13))
        pygame.draw.rect(screen, GRAY,  (panel_x + 12, temp + 2, 13, 13), 1)
        screen.blit(font.render(label, True, DGRAY), (panel_x + 30, temp + 2))
        temp += 18
    temp += 4; divider(temp); temp += 8

    found = stats.get("found")
    if found is True:
        text("Path Found!",                         temp, GREEN, bold=True); temp += 20
        text(f"  Steps   : {stats['steps']}",       temp); temp += 18
        text(f"  Visited : {stats['visited']}",      temp); temp += 18
        text(f"  Time    : {stats['elapsed']:.2f}s", temp)
    elif found is False:
        text("No Path Found",                        temp, RED, bold=True); temp += 20
        text(f"  Visited : {stats['visited']}",       temp); temp += 18
        text(f"  Time    : {stats['elapsed']:.2f}s",  temp)
    else:

        message = stats.get("msg", "")
        if message:
            text(message, temp, stats.get("msg_color", DGRAY))