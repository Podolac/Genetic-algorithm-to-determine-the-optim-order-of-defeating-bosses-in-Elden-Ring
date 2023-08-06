import tkinter as tk
import random
import math
import xlrd


class Enemy:
    def __init__(self, canvas, name, x, y, difficulty, reward):
        self.canvas = canvas
        self.id = canvas.create_oval(x, y, x + ENEMY_SIZE, y + ENEMY_SIZE, outline=COLOR_ENEMY)
        self.name = name
        self.x = x
        self.y = y
        self.difficulty = difficulty
        self.reward = reward
        self.selected = False


class Ant:
    def __init__(self, canvas):
        self.canvas = canvas
        self.x = START_X
        self.y = START_Y
        self.id = self.canvas.create_oval(self.x - 5, self.y - 5, self.x + 5, self.y + 5, fill=COLOR_START)
        self.survivability = 10
        random.shuffle(enemies)
        self.dna = enemies.copy()
        self.fit = 0
        self.distance = 0
        self.boss_count = 0
        self.won = False

    def is_dead(self, enemy_difficulty):
        """Check if the ant is defeated by the enemy."""
        return self.survivability < enemy_difficulty * 0.7

    def draw_movement(self, enemy_x, enemy_y, is_dead):
        """Visualize the ant's movement."""
        color = COLOR_WIN if not is_dead else COLOR_DEAD
        line_color = COLOR_START if not is_dead else COLOR_DEAD

        self.id = self.canvas.create_oval(self.x, self.y, self.x + 5, self.y + 5, fill=color)
        self.canvas.create_line(self.x, self.y, enemy_x, enemy_y, fill=line_color, width=1)
        self.x = enemy_x
        self.y = enemy_y
        window.update()

    def movement(self, visualize=False):
        """Simulate the ant's movement through the enemies."""
        for i in range(len(enemies) - 1):
            enemy = self.dna[i]
            if visualize:
                if self.is_dead(enemy.difficulty):
                    self.draw_movement(enemy.x, enemy.y, True)
                    break
                elif enemy.name == "Fire Giant":
                    self.draw_movement(enemy.x, enemy.y, False)
                    break
                else:
                    self.draw_movement(enemy.x, enemy.y, False)
            else:
                if self.is_dead(enemy.difficulty):
                    self.boss_count = i + 1
                    break
                elif enemy.name == "Fire Giant":
                    self.won = True
                    self.boss_count = i
                    break

                if i == 0:
                    self.distance += int(compute_distance(enemy.x, enemy.y, self.x, self.y))
                else:
                    self.distance += int(compute_distance(enemy.x, enemy.y, self.dna[i-1].x, self.dna[i-1].y))

                if (enemy.difficulty / self.survivability) > 0.7:
                    self.survivability += enemy.reward


def compute_distance(x1, y1, x2, y2):
    """Compute the Euclidean distance between two points."""
    return math.hypot(x2 - x1, y2 - y1)


def calculate_fitness(ant):
    """Calculate the fitness of an ant."""
    ant.fit = int(ant.survivability - ant.boss_count) + (10 if ant.won else 0)


def select_fittest_ants():
    """Select the top 50% of ants based on their fitness."""
    global population
    population.sort(key=lambda a: a.fit, reverse=True)
    half_size = len(population) // 2
    del population[half_size:]


def perform_mutation(mutation_rate):
    """Mutate random ants in the population."""
    for _ in range(100):
        ant = random.choice(population)
        for _ in range(int(mutation_rate * len(enemies))):
            idx1, idx2 = random.sample(range(len(enemies)), 2)
            ant.dna[idx1], ant.dna[idx2] = ant.dna[idx2], ant.dna[idx1]


def uniform_crossover(parent1, parent2):
    """Perform uniform crossover between two parent ants."""
    child = Ant(parent1.canvas)
    child.dna = random.choices([parent1, parent2], k=len(enemies))

    return child


def reproduce():
    """Generate a new population of ants through crossover and mutation."""
    global population
    new_population = []

    # Clone the top 100 ants
    for i in range(100):
        ant = Ant(population[i].canvas)
        ant.dna = population[i].dna.copy()
        new_population.append(ant)

    # Mutation
    perform_mutation(0.1)

    # Crossover to fill the rest of the new population
    while len(new_population) < POPULATION_SIZE:
        parent1, parent2 = random.sample(population, 2)
        new_population.append(uniform_crossover(parent1, parent2))

    population = new_population.copy()


def iteration():
    """Perform one iteration of the genetic algorithm."""
    for ant in population:
        ant.movement(False)

    for ant in population:
        calculate_fitness(ant)

    select_fittest_ants()

    # Visualize the fittest ant's movement
    fittest_ant = population[0]
    fittest_ant.canvas.create_image(WIDTH / 2, HEIGHT / 2, image=bg)
    fittest_ant.canvas.pack()
    fittest_ant.movement(True)

    reproduce()


def main():
    global window, enemies, population

    window = tk.Tk()
    window.title("Genetic Algorithm Simulation")
    window.resizable(0, 0)
    window.wm_attributes("-topmost", 1)
    canvas = tk.Canvas(window, width=WIDTH, height=HEIGHT, bd=0, highlightthickness=0)
    canvas.create_image(WIDTH / 2, HEIGHT / 2, image=bg)
    canvas.pack()
    window.update()

    # Load enemy data from the Excel file
    loc = "bussy.xls"
    wb = xlrd.open_workbook(loc)
    sheet = wb.sheet_by_index(0)
    enemies = [
        Enemy(canvas, sheet.cell_value(i + 1, 0), sheet.cell_value(i + 1, 1) / 10, sheet.cell_value(i + 1, 2) / 10,
              sheet.cell_value(i + 1, 3), sheet.cell_value(i + 1, 4))
        for i in range(ENEMY_COUNT)
    ]

    # Initialize the population
    population = [Ant(canvas) for _ in range(POPULATION_SIZE)]

    # Run the genetic algorithm for a fixed number of generations
    for generation in range(MAX_GENERATIONS):
        print(f"Generation: {generation + 1}")
        iteration()

    # Print the sequence of enemies encountered by the fittest ant
    for enemy in population[0].dna:
        print(enemy.name, end=", ")
    print()
    population.clear()

    window.mainloop()


# Constants
WIDTH, HEIGHT = 1600, 900
ENEMY_SIZE = 5
ENEMY_COUNT = 190
POPULATION_SIZE = 1000
MAX_GENERATIONS = 1000
START_X, START_Y = 160, 410
COLOR_DEAD, COLOR_WIN, COLOR_START, COLOR_ENEMY = "red", "green", "blue", "white"
bg = tk.PhotoImage(file="Map-Elden-Ring.png").subsample(10, 10)

if __name__ == "__main__":
    main()
