import pygame
import math
import time

# Configuración inicial de Pygame
pygame.init()
WIDTH, HEIGHT = 800, 800
ROWS = 50  # Número de filas en la cuadrícula
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Algoritmo 1")

# Definición de colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
CYAN = [0, 125, 255]
GREEN = (0, 255, 0)
ORANGE = [255, 125, 0]  # Color para celdas abiertas en búsqueda

# Tamaño de cada celda
CELL_SIZE = WIDTH // ROWS

# Estados de cada celda
EMPTY, START, END, OBSTACLE, PATH, CLOSED, OPEN = 0, 1, 2, 3, 4, 5, 6

# Inicialización del grid
grid = [[EMPTY for _ in range(ROWS)] for _ in range(ROWS)]
start_pos, end_pos = None, None

# Funciones de utilidad
def draw_grid(win):
    for x in range(ROWS):
        for y in range(ROWS):
            color = WHITE
            if grid[x][y] == START:
                color = CYAN
            elif grid[x][y] == END:
                color = GREEN
            elif grid[x][y] == OBSTACLE:
                color = RED
            elif grid[x][y] == PATH:
                color = BLUE
            elif grid[x][y] == CLOSED:
                color = BLUE
            elif grid[x][y] == OPEN:
                color = ORANGE  # Color de celdas abiertas en búsqueda
            pygame.draw.rect(win, color, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    for i in range(ROWS):
        pygame.draw.line(win, BLACK, (0, i * CELL_SIZE), (WIDTH, i * CELL_SIZE))
        pygame.draw.line(win, BLACK, (i * CELL_SIZE, 0), (i * CELL_SIZE, HEIGHT))

    pygame.display.update()

def get_clicked_pos(pos):
    x, y = pos
    row = x // CELL_SIZE
    col = y // CELL_SIZE
    return row, col

def heuristic(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

def get_neighbors(pos):
    x, y = pos
    directions = [
        (1, 0), (-1, 0), (0, 1), (0, -1), 
        (1, 1), (1, -1), (-1, 1), (-1, -1)
    ]
    neighbors = []
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if 0 <= nx < ROWS and 0 <= ny < ROWS and grid[nx][ny] != OBSTACLE and grid[nx][ny] != CLOSED:
            cost = 1 if dx == 0 or dy == 0 else math.sqrt(2)
            neighbors.append((cost, (nx, ny)))
    return neighbors

def reconstruct_path(came_from, current):
    path_length = 0
    while current in came_from:
        current = came_from[current]
        path_length += 1
        if current != start_pos:
            grid[current[0]][current[1]] = PATH  # Marcar el camino en azul
    return path_length

def find_shortest_path(start, end):
    open_set = {start: 0}  # Set inicial con el nodo de inicio
    came_from = {}  # Diccionario para reconstruir el camino
    analyzed_nodes = 0
    counted_nodes = set()  # Mantiene un registro de nodos ya contados
    start_time = time.time()

    while open_set:
        # Encuentra el nodo con el menor costo en el conjunto abierto
        current = min(open_set, key=open_set.get)
        
        # Si llegamos al final, termina la búsqueda
        if current == end:
            end_time = time.time()
            path_length = reconstruct_path(came_from, end)  # Reconstruye y mide el camino
            print("---------------------------")
            print("Camino encontrado!")
            print(f"Tiempo: {end_time - start_time:.4f} segundos")
            print(f"Nodos analizados: {analyzed_nodes}")
            print(f"Longitud del camino: {path_length} nodos")
            grid[end[0]][end[1]] = END
            return True

        # Marca el nodo actual como cerrado y remuévelo de open_set
        grid[current[0]][current[1]] = CLOSED
        open_set.pop(current)
        
        # Si el nodo actual no es el nodo de inicio ni el de fin, y no ha sido contado, cuéntalo
        if current != start and current not in counted_nodes:
            analyzed_nodes += 1
            counted_nodes.add(current)  # Marca el nodo como contado

        # Expande vecinos
        neighbors = get_neighbors(current)
        for cost, neighbor in neighbors:
            temp_cost = cost + heuristic(neighbor, end)
            if neighbor not in open_set and grid[neighbor[0]][neighbor[1]] != CLOSED:
                open_set[neighbor] = temp_cost
                came_from[neighbor] = current  # Registra de dónde venimos para reconstruir el camino
                grid[neighbor[0]][neighbor[1]] = OPEN  # Marcar como abierto para visualización
                # Si el vecino aún no está contado, cuenta el nodo abierto
                if neighbor != start and neighbor not in counted_nodes:
                    analyzed_nodes += 1
                    counted_nodes.add(neighbor)  # Marca el nodo como contado

        # Actualiza visualización
        draw_grid(WIN)
        #pygame.time.delay(50)  # Control de velocidad de animación (en milisegundos)

    # Si no se encontró camino
    end_time = time.time()
    print("No se encontró un camino.")
    print(f"Tiempo: {end_time - start_time:.4f} segundos")
    print(f"Nodos analizados (sin incluir inicio, sin duplicados): {analyzed_nodes}")
    return False

def reset_grid():
    global start_pos, end_pos, grid
    grid = [[EMPTY for _ in range(ROWS)] for _ in range(ROWS)]
    start_pos, end_pos = None, None

def main():
    global start_pos, end_pos
    running = True
    while running:
        draw_grid(WIN)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if pygame.mouse.get_pressed()[0]:  # Click izquierdo
                pos = get_clicked_pos(pygame.mouse.get_pos())
                if not start_pos:
                    start_pos = pos
                    grid[start_pos[0]][start_pos[1]] = START
                elif not end_pos and pos != start_pos:
                    end_pos = pos
                    grid[end_pos[0]][end_pos[1]] = END
                elif pos != start_pos and pos != end_pos:
                    grid[pos[0]][pos[1]] = OBSTACLE
            elif pygame.mouse.get_pressed()[2]:  # Click derecho para borrar
                pos = get_clicked_pos(pygame.mouse.get_pos())
                if grid[pos[0]][pos[1]] == START:
                    start_pos = None
                elif grid[pos[0]][pos[1]] == END:
                    end_pos = None
                grid[pos[0]][pos[1]] = EMPTY

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start_pos and end_pos:
                    find_shortest_path(start_pos, end_pos)
                if event.key == pygame.K_c:
                    reset_grid()

    pygame.quit()

if __name__ == "__main__":
    main()