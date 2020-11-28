    #
    # -funkcja mutacji (pobiera wektor, zwraca, zmutowany wektor)
    # -funkcja crossover(pobiera 2 wektory, zwraca połączenie)
    # -funkcja celu- liczącą długość trasy (pobiera wektor, zwraca długość trasy)
    # -init
    # -funkcja selekcji
    # -funkcja sukcesji

# example specimen == [A,G,F,D,E,H,B,C]

from math import sqrt
from random import randint


def load():
    _points = {}
    with open("WE.txt") as file:
        for line in file.readlines():
            temp = line.split(' ')
            _points[temp[0]] = (int(temp[1]), int(temp[2]))
    return _points, len(_points.keys())


def evaluate(specimen, points_arg):
    total = 0
    for nr in range(len(specimen)-1):
        total += sqrt(
            (points_arg[specimen[nr+1]][0]-points_arg[specimen[nr]][0])**2 +
            (points_arg[specimen[nr+1]][1]-points_arg[specimen[nr]][1])**2
        )
    return total


def mutation(specimen, specimen_length_arg):
    while True:
        (a, b) = (randint(0, specimen_length_arg-1), randint(0, specimen_length_arg-1))
        if a != b:
            break
    (specimen[a], specimen[b]) = (specimen[b], specimen[a])
    return specimen


def crossover(parent1, parent2, specimen_length_arg):
    # newborn = parent 1 + a piece from parent 2
    while True:
        (a, b) = (randint(0, specimen_length_arg - 1), randint(0, specimen_length_arg - 1))
        if specimen_length_arg > abs(a-b) > 1:
            print('crossover points: ', a, b)
            break
    if a < b:
        newborn = ['NULL' for i in range(0, specimen_length_arg)]
        newborn[a:b] = parent2[a:b]
        for nr in list(range(0, a))+list(range(b, specimen_length_arg)):
            if parent1[nr] not in parent2[a:b]:
                newborn[nr] = parent1[nr]
            else:
                newborn[nr] = parent2[nr]
    else:
        newborn = ['NULL' for i in range(0, specimen_length_arg)]
        newborn[a:] = parent2[a:]
        newborn[:b] = parent2[:b]
        for nr in list(range(a, specimen_length_arg))+list(range(0, b)):
            print(nr)
            if parent1[nr] not in parent2[0:b]+parent2[a:]:
                newborn[nr] = parent1[nr]
            else:
                newborn[nr] = parent2[nr]
    return newborn, a, b

def init_population():
    pass


if __name__ == "__main__":
    (points, specimen_length) = load()
    # default_specimen = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    # print(points)
    # print('Specimen length: ', specimen_length)
    # print('Default route length: ', evaluate(default_specimen, points))
    # print('Mutation: ', mutation(default_specimen, specimen_length))
    # print('Mutated specimen route length: ', evaluate(default_specimen, points))
    # print(evaluate(['H', 'D', 'H', 'D', 'H', 'D', 'H', 'D'], points))
    print(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'])
    print(['D', 'H', 'F', 'A', 'B', 'C', 'E', 'G'])
    print(crossover(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'],
                    ['D', 'H', 'F', 'A', 'B', 'C', 'E', 'G'], specimen_length)
         )

