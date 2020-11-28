    #
    # -funkcja mutacji (pobiera wektor, zwraca, zmutowany wektor)
    # -funkcja crossover(pobiera 2 wektory, zwraca połączenie)
    # -funkcja celu- liczącą długość trasy (pobiera wektor, zwraca długość trasy)
    # -init
    # -funkcja selekcji
    # -funkcja sukcesji

# example specimen == [A,G,F,D,E,H,B,C]

from math import sqrt

global points


def load():
    global points
    points = {}
    with open("WE.txt") as file:
        for line in file.readlines():
            temp = line.split(' ')
            points[temp[0]] = (int(temp[1]), int(temp[2]))
    return points


def evaluate(specimen):
    global points
    total = 0
    for nr in range(len(specimen)-1):
        total += sqrt(
            (points[specimen[nr+1]][0]-points[specimen[nr]][0])**2 +
            (points[specimen[nr+1]][1]-points[specimen[nr]][1])**2
        )
    return total


def init_population():
    pass


def mutation(specime):
    pass


if __name__ == "__main__":
    points = load()
    print(points)
    print(evaluate(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']))
    print(evaluate(['H', 'D', 'H', 'D', 'H', 'D', 'H', 'D']))
