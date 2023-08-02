import tkinter as tk
import random
import math
import xlrd

window = tk.Tk()
bg = tk.PhotoImage(file="Map-Elden-Ring.png")
bg = bg.subsample(10, 10)

width = bg.width()
height = bg.height()
enemy_size = 5
enemy_nr = 190
densitate_populatie = 1000
enemyes = []
population = []
color_dead = "red"
color_win = "green"
color_start = "blue"
color_enemy = "white"


def calc_dis(x1, y1, x2, y2):
    distance = math.hypot(x2 - x1, y2 - y1)
    return distance


class Enemy:
    def __init__(self, canvas, nume, pos_x, pos_y, dificulty, reward):
        self.canvas = canvas
        self.id = canvas.create_oval(pos_x, pos_y, pos_x + enemy_size, pos_y + enemy_size, outline=color_enemy)
        self.nume = nume
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.dificulty = dificulty
        self.reward = reward
        self.selected = 0


class Ant:
    def __init__(self, canvas):
        self.canvas = canvas
        self.x = 160
        self.y = 410
        self.id = self.canvas.create_oval(self.x - 5, self.y - 5, self.x + 5, self.y + 5, fill=color_start)
        self.survivability = 10
        random.shuffle(enemyes)
        self.dna = enemyes.copy()
        self.fit = 0
        self.dis = 0
        self.bosses = 0
        self.won = False

    def draw_movement(self, en_x, en_y, is_ded):
        if is_ded:
            self.id = self.canvas.create_oval(self.x, self.y, self.x + 5, self.y + 5, fill=color_win)
            self.canvas.create_line(self.x, self.y, en_x, en_y, fill=color_dead, width=1)
            self.id = self.canvas.create_oval(en_x, en_y, en_x + 5, en_y + 5, fill=color_dead)
        else:
            self.id = self.canvas.create_oval(self.x, self.y, self.x + 5, self.y + 5, fill=color_win)
            self.canvas.create_line(self.x, self.y, en_x, en_y, fill=color_start, width=1)
        self.x = en_x
        self.y = en_y
        window.update()

    def movement(self, draw):
        for i in range(enemy_nr-1):
            if draw:
                if self.is_dead(self.dna[i].dificulty):
                    self.draw_movement(self.dna[i].pos_x, self.dna[i].pos_y, True)
                    window.update()
                    break
                elif self.dna[i].nume == "Fire Giant":
                    self.draw_movement(self.dna[i].pos_x, self.dna[i].pos_y, False)
                    window.update()
                    break
                else:
                    self.draw_movement(self.dna[i].pos_x, self.dna[i].pos_y, False)
            else:
                if self.is_dead(self.dna[i].dificulty):
                    self.bosses = i + 1
                    break
                elif self.dna[i].nume == "Fire Giant":
                    self.won = True
                    self.bosses = i
                    break

                if i == 0:
                    self.dis += int(calc_dis(self.dna[i].pos_x, self.dna[i].pos_y, self.x, self.y))
                else:
                    self.dis += int(calc_dis(self.dna[i].pos_x, self.dna[i].pos_y,
                                             self.dna[i-1].pos_x, self.dna[i-1].pos_y))

                if (self.dna[i].dificulty / self.survivability) > 0.7:
                    self.survivability += self.dna[i].reward

    def is_dead(self, en_d):
        # daca ant-ul are survivabilitatea mai mare sau egala cu inamicul il invinge si merge mai departe
        if self.survivability < en_d * 0.7:
            return True
        else:
            return False


def fitness(ant):
    if not ant.dis:
        ant.fit = 0
    else:
        ant.fit = int(ant.survivability - ant.bosses)

        if ant.won:
            ant.fit += 10


def selection():
    global population
    population.sort(key=lambda a: a.fit, reverse=True)
    print("Fitness: ", population[0].fit, "Survivability: ", population[0].survivability,
          "Bosses: ", population[0].bosses, "Distance: ", population[0].dis)
    i = 0
    for ant in population:
        i += 1
        if i > densitate_populatie//2:
            population.remove(ant)


def uniform_crossover(parinte1, parinte2):
    copil = Ant(parinte1.canvas)
    new_dna = parinte1.dna.copy()
    start = random.randint(0, enemy_nr - 1)
    stop = random.randint(0, enemy_nr - 1)
    if start > stop:
        start, stop = stop, start

    for i in range(start, stop):
        dna_p1 = parinte1.dna[i]
        parinte1.dna[i].selectat = 1
        j = parinte2.dna.index(dna_p1)
        parinte2.dna[j].selectat = 1

    for i in range(stop, enemy_nr):
        dna_p2 = parinte2.dna[i]
        parinte2.dna[i].selectat = 1
        new_dna[i] = dna_p2
        j = parinte1.dna.index(dna_p2)
        parinte1.dna[j].selectat = 1

    j = 0
    for i in range(stop):
        dna_p2 = parinte2.dna[i]
        if dna_p2.selected == 0:
            new_dna[j] = dna_p2
            j += 1
            dna_p2.selectat = 1

    copil.dna.clear()
    copil.dna = new_dna.copy()

    for i in range(enemy_nr):
        copil.dna[i].selectat = 0
    return copil


def mutation(mutation_procent):
    for i in range(100):
        ant = population[random.randint(100, len(population)-1)]
        for j in range(int(mutation_procent * enemy_nr / 100)):
            dna1 = int(random.randint(0, enemy_nr-1))
            dna2 = int(random.randint(0, enemy_nr-1))
            ant.dna[dna1], ant.dna[dna2] = ant.dna[dna2], ant.dna[dna1]


def reproduction():
    global population
    new_population = []

    for i in range(100):
        ant = Ant(population[i].canvas)
        ant.dna = population[i].dna.copy()
        new_population.append(ant)

    mutation(10)

    while len(new_population) != densitate_populatie:
        parinte1 = population[0]
        population.remove(parinte1)
        parinte2 = population[random.randint(0, len(population)-1)]
        population.remove(parinte2)

        new_population.append(uniform_crossover(parinte1, parinte2))
        new_population.append(uniform_crossover(parinte1, parinte2))
        new_population.append(uniform_crossover(parinte2, parinte1))
        new_population.append(uniform_crossover(parinte2, parinte1))

    population.clear()
    population = new_population.copy()


def iteratie():
    for ant in population:
        ant.movement(False)

    for ant in population:
        fitness(ant)

    selection()

    population[0].canvas.create_image(width / 2, height / 2, image=bg)
    population[0].canvas.pack()
    population[0].movement(True)
    window.update()

    reproduction()


def main():
    window.title("Algoritm genetic")
    window.resizable(0, 0)
    window.wm_attributes("-topmost", 1)
    canvas = tk.Canvas(window, width=width, height=height, bd=0, highlightthickness=0)
    canvas.create_image(width/2, height/2, image=bg)
    canvas.pack()
    window.update()

    loc = "bussy.xls"
    wb = xlrd.open_workbook(loc)
    sheet = wb.sheet_by_index(0)

    # initializam inamicii
    for i in range(enemy_nr):
        new_enemy = Enemy(canvas, sheet.cell_value(i+1, 0), sheet.cell_value(i+1, 1)/10, sheet.cell_value(i+1, 2)/10,
                          sheet.cell_value(i+1, 3), sheet.cell_value(i+1, 4))
        enemyes.append(new_enemy)

    # initializam populatia
    for i in range(densitate_populatie):
        new_ant = Ant(canvas)
        population.append(new_ant)

    for i in range(1000):
        print("Generatie: ", i + 1)
        iteratie()

    for enemy in population[0].dna:
        print(enemy.nume, end=", ")
    print("\n")
    population.clear()


main()
