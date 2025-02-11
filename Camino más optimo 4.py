import pygame
import sys
import time
from queue import PriorityQueue

# Inicializar pygame
pygame.init()

# Configuración de colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
GREY = [255,175,0]

# Configuración de la cuadrícula
WIDTH, HEIGHT = 800, 800
ROWS = 50  # Ajusta para cambiar la densidad de la cuadrícula
SIZE = WIDTH // ROWS
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Camino Más Corto con Dijkstra")

# Variables globales
start = None
end = None
grid = []
obstacles = set()
visited_nodes = 0
path_length = 0
search_time = 0


# Clase Nodo que representa cada celda
class Node:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.x = row * SIZE
        self.y = col * SIZE
        self.color = WHITE
        self.neighbors = []

    def get_pos(self):
        return self.row, self.col

    def is_barrier(self):
        return self.color == RED

    def reset(self):
        self.color = WHITE

    def make_start(self):
        self.color = CYAN

    def make_end(self):
        self.color = GREEN

    def make_barrier(self):
        self.color = RED

    def make_path(self):
        self.color = BLUE

    def make_visited(self):
        self.color = GREY

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, SIZE, SIZE))

    def update_neighbors(self, grid):
        self.neighbors = []
        
        # Movimiento en las 4 direcciones principales
        if self.row < ROWS - 1 and not grid[self.row + 1][self.col].is_barrier():  # Abajo
            self.neighbors.append(grid[self.row + 1][self.col])
        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():  # Arriba
            self.neighbors.append(grid[self.row - 1][self.col])
        if self.col < ROWS - 1 and not grid[self.row][self.col + 1].is_barrier():  # Derecha
            self.neighbors.append(grid[self.row][self.col + 1])
        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():  # Izquierda
            self.neighbors.append(grid[self.row][self.col - 1])

        # Movimiento en las 4 direcciones diagonales
        if self.row < ROWS - 1 and self.col < ROWS - 1 and not grid[self.row + 1][self.col + 1].is_barrier():  # Abajo-Derecha
            self.neighbors.append(grid[self.row + 1][self.col + 1])
        if self.row < ROWS - 1 and self.col > 0 and not grid[self.row + 1][self.col - 1].is_barrier():  # Abajo-Izquierda
            self.neighbors.append(grid[self.row + 1][self.col - 1])
        if self.row > 0 and self.col < ROWS - 1 and not grid[self.row - 1][self.col + 1].is_barrier():  # Arriba-Derecha
            self.neighbors.append(grid[self.row - 1][self.col + 1])
        if self.row > 0 and self.col > 0 and not grid[self.row - 1][self.col - 1].is_barrier():  # Arriba-Izquierda
            self.neighbors.append(grid[self.row - 1][self.col - 1])


# Inicialización de la cuadrícula
def create_grid():
    return [[Node(i, j) for j in range(ROWS)] for i in range(ROWS)]


# Dibujar cuadrícula
def draw_grid(win):
    for row in grid:
        for node in row:
            node.draw(win)

    for i in range(ROWS):
        pygame.draw.line(win, BLACK, (0, i * SIZE), (WIDTH, i * SIZE))
        pygame.draw.line(win, BLACK, (i * SIZE, 0), (i * SIZE, HEIGHT))
    pygame.display.update()


# Algoritmo de Dijkstra
def dijkstra_algorithm(draw, grid, start, end):
    global visited_nodes, path_length, search_time
    visited_nodes = 0
    path_length = 0
    search_time = 0

    start_time = time.time()
    count = 0
    queue = PriorityQueue()
    queue.put((0, count, start))
    distances = {node: float("inf") for row in grid for node in row}
    distances[start] = 0
    prev_node = {node: None for row in grid for node in row}

    while not queue.empty():
        current_distance, _, current_node = queue.get()
        if current_node == end:
            reconstruct_path(prev_node, end, draw)
            search_time = time.time() - start_time
            return True

        for neighbor in current_node.neighbors:
            temp_distance = current_distance + 1

            if temp_distance < distances[neighbor]:
                distances[neighbor] = temp_distance
                prev_node[neighbor] = current_node
                count += 1
                queue.put((temp_distance, count, neighbor))
                if neighbor != start and neighbor != end:
                    neighbor.make_visited()
                visited_nodes += 1
        draw()

    search_time = time.time() - start_time
    return False


# Reconstrucción del camino
def reconstruct_path(prev_node, current, draw):
    global path_length
    while prev_node[current]:
        current = prev_node[current]
        if current != start:
            current.make_path()
        path_length += 1
        draw()


# Función principal
def main():
    global start, end, grid
    grid = create_grid()
    run = True
    started = False

    while run:
        draw_grid(WINDOW)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()

            if pygame.mouse.get_pressed()[0]:  # Click izquierdo
                pos = pygame.mouse.get_pos()
                row, col = pos[0] // SIZE, pos[1] // SIZE
                node = grid[row][col]

                if not start and node != end:
                    start = node
                    start.make_start()
                elif not end and node != start:
                    end = node
                    end.make_end()
                elif node != end and node != start:
                    node.make_barrier()
                    obstacles.add(node.get_pos())

            elif pygame.mouse.get_pressed()[2]:  # Click derecho
                pos = pygame.mouse.get_pos()
                row, col = pos[0] // SIZE, pos[1] // SIZE
                node = grid[row][col]
                node.reset()
                if node == start:
                    start = None
                elif node == end:
                    end = None
                if node.get_pos() in obstacles:
                    obstacles.remove(node.get_pos())

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for node in row:
                            node.update_neighbors(grid)
                    dijkstra_algorithm(lambda: draw_grid(WINDOW), grid, start, end)
                    print("-----------------------------------------------")
                    print(f"Tiempo de búsqueda: {search_time:.4f} segundos")
                    print(f"Nodos analizados: {visited_nodes}")
                    print(f"Longitud del camino: {path_length}")

                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = create_grid()
                    obstacles.clear()

    pygame.quit()


if __name__ == "__main__":
    main()
