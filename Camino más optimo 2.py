import pygame
import math
import time
from queue import PriorityQueue

# Configuraciones generales
WIDTH = 800
ROWS = 50
GRID_COLOR = (200, 200, 200)
BACKGROUND_COLOR = (255, 255, 255)

# Definición de colores
START_COLOR = [0,125,255]
END_COLOR = (0, 255, 0)
OBSTACLE_COLOR = (255, 0, 0)
OPEN_COLOR = [255,125,0]
CLOSED_COLOR = [255,175,0]
PATH_COLOR = [0,0,255]

# Inicializar pygame
pygame.init()
win = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("Camino más corto con A*")

# Clase para manejar las celdas de la cuadrícula
class Cell:
    def __init__(self, row, col, width):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.width = width
        self.color = BACKGROUND_COLOR
        self.neighbors = []

    def get_pos(self):
        return self.row, self.col

    def is_closed(self):
        return self.color == CLOSED_COLOR

    def is_open(self):
        return self.color == OPEN_COLOR

    def is_obstacle(self):
        return self.color == OBSTACLE_COLOR

    def is_start(self):
        return self.color == START_COLOR

    def is_end(self):
        return self.color == END_COLOR

    def reset(self):
        self.color = BACKGROUND_COLOR

    def make_start(self):
        self.color = START_COLOR

    def make_closed(self):
        self.color = CLOSED_COLOR

    def make_open(self):
        self.color = OPEN_COLOR

    def make_obstacle(self):
        self.color = OBSTACLE_COLOR

    def make_end(self):
        self.color = END_COLOR

    def make_path(self):
        self.color = PATH_COLOR

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        self.neighbors = []
        directions = [
            (0, 1), (1, 0), (0, -1), (-1, 0),  # Horizontal y vertical
            (-1, -1), (-1, 1), (1, -1), (1, 1) # Diagonales
        ]
        for d in directions:
            row, col = self.row + d[0], self.col + d[1]
            if 0 <= row < ROWS and 0 <= col < ROWS and not grid[row][col].is_obstacle():
                self.neighbors.append((grid[row][col], 1 if d[0] == 0 or d[1] == 0 else math.sqrt(2)))

# Funciones para el algoritmo y configuración de la cuadrícula
def heuristic(cell1, cell2):
    x1, y1 = cell1.get_pos()
    x2, y2 = cell2.get_pos()
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

def reconstruct_path(came_from, current, draw):
    path_length = 0
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw()
        path_length += 1
    return path_length

def algorithm(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    g_score = {cell: float("inf") for row in grid for cell in row}
    g_score[start] = 0
    f_score = {cell: float("inf") for row in grid for cell in row}
    f_score[start] = heuristic(start, end)

    open_set_hash = {start}
    start_time = time.time()

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            path_length = reconstruct_path(came_from, end, draw)
            elapsed_time = time.time() - start_time
            return elapsed_time, count, path_length

        for neighbor, move_cost in current.neighbors:
            tentative_g_score = g_score[current] + move_cost

            if tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + heuristic(neighbor, end)
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()

        draw()

        if current != start:
            current.make_closed()

    return None, count, 0

def make_grid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            cell = Cell(i, j, gap)
            grid[i].append(cell)
    return grid

def draw_grid(win, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, GRID_COLOR, (0, i * gap), (width, i * gap))
        pygame.draw.line(win, GRID_COLOR, (i * gap, 0), (i * gap, width))

def draw(win, grid, rows, width):
    win.fill(BACKGROUND_COLOR)
    for row in grid:
        for cell in row:
            cell.draw(win)
    draw_grid(win, rows, width)
    pygame.display.update()

def get_clicked_pos(pos, rows, width):
    gap = width // rows
    y, x = pos
    return y // gap, x // gap

def main(win, width):
    grid = make_grid(ROWS, width)
    start, end = None, None

    run = True
    while run:
        draw(win, grid, ROWS, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if pygame.mouse.get_pressed()[0]:  # Izquierdo
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                cell = grid[row][col]
                if not start and cell != end:
                    start = cell
                    start.make_start()
                elif not end and cell != start:
                    end = cell
                    end.make_end()
                elif cell != end and cell != start:
                    cell.make_obstacle()

            elif pygame.mouse.get_pressed()[2]:  # Derecho
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                cell = grid[row][col]
                cell.reset()
                if cell == start:
                    start = None
                elif cell == end:
                    end = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for cell in row:
                            cell.update_neighbors(grid)

                    elapsed_time, analyzed_coords, path_length = algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end)
                    if elapsed_time is not None:
                        print("-"*100)
                        print(f"Tiempo de búsqueda: {elapsed_time:.4f} segundos")
                        print(f"Coordenadas analizadas: {analyzed_coords}")
                        print(f"Longitud del camino: {path_length} coordenadas")

                if event.key == pygame.K_c:
                    start, end = None, None
                    grid = make_grid(ROWS, width)

    pygame.quit()

main(win, WIDTH)
