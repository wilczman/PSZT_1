    #
    # -funkcja mutacji (pobiera wektor, zwraca, zmutowany wektor)
    # -funkcja crossover(pobiera 2 wektory, zwraca połączenie)
    # -funkcja celu- liczącą długość trasy (pobiera wektor, zwraca długość trasy)
    # -init
    # -funkcja selekcji
    # -funkcja sukcesji

# example specimen == [A,G,F,D,E,H,B,C]

from math import sqrt
from random import randint, shuffle
from numpy import array, zeros, full, argpartition, Inf

def load():
    '''
    Wczytywanie danych
    :return:  Słownik współrzędnych punktów i ilość punktów w osobniku
    '''
    _points = {}
    with open("WE.txt") as file:
        for line in file.readlines():
            temp = line.split(' ')
            _points[temp[0]] = (int(temp[1]), int(temp[2]))
    return _points, len(_points.keys())

def transform_points_definition(points_arg):
    '''
    Funkcja "transformująca" słownikową definicję punktów na
    listy, aby umożliwić późniejsze wykorzystanie indeksów w listach
    zamiast poszukiwania elementów w słownikach
    (kolejność w listach jest deterministyczna, w słownikach niekoniecznie)
    :param points_arg: słownik punktów
    :return: lista nazw punktów z pliku wejściowego, lista punktów w postaci liczbowej oraz lista koorydnatów
    '''
    _points_symbolic = list()
    _points_indices = list()
    _coordinates = list()

    idx = 0
    for point, coordinates in points_arg.items():
        _points_symbolic.append(point)
        _points_indices.append(idx)
        idx = idx + 1
        _coordinates.append(coordinates)

    return _points_symbolic, _points_indices, _coordinates

def get_symbolic_representation(indices, symbolic_base):
    '''
    Funkcja zwracająca symboliczną reprezentację osobnika
    :param indices: indeksowa reprezentacja osobnika
    :param symbolic_base: bazowa lista punktów w formie symboli
    :return: osobnik w formie symbolicznej
    '''
    symbolic = list()

    for idx in indices:
        symbolic.append(symbolic_base[idx])

    return symbolic

def get_indices_representation(symbolic, symbolic_base):
    '''
    Funkcja zwracająca indeksową reprezentację osobnika
    :param indices: symboliczna reprezentacja osobnika
    :param symbolic_base: bazowa lista punktów w formie symboli
    :return: osobnik w formie indeksowej
    '''
    indices = list()

    for point in symbolic:
        indices.append(symbolic_base.index(point))

    return indices

def calculate_distances(points_arg, coordinates_arg):
    '''
    Funkcja wyznaczająca bezpośrednie odległości pomiędzy punktami
    :param points_arg: lista wszystkich punktów w postaci indeksów
    :param coordinates_arg: lista koordynatów punktów
    :return: macierz zawierająca odległości pomiędzy punktami
    '''
    size = len(points_arg)
    distances = zeros(shape=[size, size])

    for idy in points_arg:
        for idx in range(idy, size):
            if idx == idy:
                continue

            distances[idx, idy] = sqrt(
                (coordinates_arg[idx][0]-coordinates_arg[idy][0])**2 +
                (coordinates_arg[idx][1]-coordinates_arg[idy][1])**2
            )

            distances[idy, idx] = distances[idx, idy]

    return distances

def evaluate(specimen, distances):
    '''
    Funkcja celu
    :param specimen: osobnik w formie listy indeksów
    :param distances: macierz odległości punktów
    :return: długość trasy
    '''
    total = 0
    for idx in range(len(specimen)-1):
        total += distances[specimen[idx]][specimen[idx+1]]

    total += distances[specimen[0]][specimen[-1]]
    return total


def mutation(specimen, specimen_length_arg):
    '''
    Implementacja mutacji, losowanie dwóch współrzędnych i zamiana punktu między nimi
    :param specimen: osobnik w formie listy
    :param specimen_length_arg: wielkość osobnika
    :return: zmieniony osobnik w formie listy
    '''
    while True:
        (a, b) = (randint(0, specimen_length_arg-1), randint(0, specimen_length_arg-1))
        if a != b:
            break
    (specimen[a], specimen[b]) = (specimen[b], specimen[a])
    return specimen


def crossover(parent1, parent2, specimen_length_arg):
    '''
    implementacja krzyżowania dwupunktowego z uwzględnieniem braku możliwości powtórzeń
    :param parent1: rodzic 1
    :param parent2: rodzic 2
    :param specimen_length_arg: wielkość osobnika
    :return: zmieniony osobnik w formie listy
    '''
    # newborn = parent 1 + a piece from parent 2
    newborn = ['NULL' for i in range(0, specimen_length_arg)]
    while True:
        # (a, b) = (randint(0, specimen_length_arg - 1), randint(0, specimen_length_arg - 1))
        (a, b) = (2, 6)
        if specimen_length_arg > abs(a-b) > 1:
            print('crossover points: ', a, b)
            break
    if a < b:
        rest = [letter for letter in parent1 if letter not in parent2[a:b]]
        newborn[a:b] = parent2[a:b]
        for nr in list(range(0, a))+list(range(b, specimen_length_arg)):
            newborn[nr] = rest.pop(0)
    else:
        rest = [letter for letter in parent1 if letter not in parent2[:b] + parent2[a:]]
        newborn[a:] = parent2[a:]
        newborn[:b] = parent2[:b]
        for nr in list(range(a, specimen_length_arg))+list(range(0, b)):
            newborn[nr] = rest.pop(0)
    return newborn


def init_population(specimen_length, population_size):
    '''
    Funkcja generująca losową, początkową populację
    :param specimen_length: wielkość osobnika
    :param population_size: wielkość populacji
    :return: początkowa populacja
    '''
    population = list()
    base_specimen = list(range(0, specimen_length))
    for _ in range(population_size):
        specimen = base_specimen[:]
        shuffle(specimen)
        population.append(specimen)

    return population

def find_n_smallest(values, n):
    '''
    Funkcja zwracająca indeksy n najmniejszych wartości z wektora values
    :param values: wektor wejściowy numpy.array
    :param n: ilość najmniejszych wartości z values, których indeksy chcemy dostać
    :return: wektor indeksów najmniejszych n wartości
    '''
    return argpartition(values, n)[:n]

def find_n_greatest(values, n):
    '''
    Funkcja zwracająca indeksy n największych wartości z wektora values
    :param values: wektor wejściowy numpy.array
    :param n: ilość największych wartości z values, których indeksy chcemy dostać
    :return: wektor indeksów największych n wartości
    '''
    return argpartition(values, -n)[-n:]

def elite_select(old_population, newborns, num_best_left, distances):
    '''
    Funkcja dokonująca selekcji elitarnej
    :param old_population: populacja stworzona w poprzedniej iteracji
    :param newborns: nowe osobniki stworzone w obecnej iteracji poprzez krzyżowanie i mutację
    :param num_best_left: liczba najlepszych osobników z old_population, które zostanie zachowana
    :param distances: macierz zawierająca odległości między punktami
    :return: nową populację po selekcji elitarnej
    '''
    old_population_evaluation = full(shape=[len(old_population),], fill_value=Inf)
    newborns_evaluation = full(shape=[len(newborns),], fill_value=Inf)

    for idx, specimen in enumerate(old_population):
        old_population_evaluation[idx] = evaluate(specimen, distances)

    for idx, specimen in enumerate(newborns):
        newborns_evaluation[idx] = evaluate(specimen, distances)

    best_old_population_indices = find_n_smallest(old_population_evaluation, num_best_left)
    best_newborns_indices = find_n_smallest(newborns_evaluation, len(old_population)-num_best_left)

    return [old_population[idx] for idx in best_old_population_indices] + [newborns[idx] for idx in best_newborns_indices]


if __name__ == "__main__":
    (points, specimen_length) = load()
    p_s, p_i, crd = transform_points_definition(points)
    print(p_s, p_i)
    distances_mtrx = calculate_distances(p_i, crd)
    print(evaluate([0, 1, 2, 3, 4, 5, 6, 7], distances_mtrx))
    default_specimen = [0, 1, 2, 3, 4, 5, 6, 7]
    # print(points)
    # print('Specimen length: ', specimen_length)
    print('Default route length: ', evaluate(default_specimen, distances_mtrx))
    print('Mutation: ', mutation(default_specimen, specimen_length))
    # # print('Mutated specimen route length: ', evaluate(default_specimen, points))
    # # print(evaluate(['H', 'D', 'H', 'D', 'H', 'D', 'H', 'D'], points))
    spec_1 = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    print(get_indices_representation(spec_1, p_s))
    spec_2 = ['D', 'H', 'F', 'A', 'B', 'C', 'E', 'G']
    print(get_indices_representation(spec_2, p_s))
    # print(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'])
    # print(['D', 'H', 'F', 'A', 'B', 'C', 'E', 'G'])
    print(crossover(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'],
                    ['D', 'H', 'F', 'A', 'B', 'C', 'E', 'G'], specimen_length))

    old_population = init_population(specimen_length, 10)
    new_population = init_population(specimen_length, 10)

    print(elite_select(old_population, new_population, 3, distances_mtrx))

