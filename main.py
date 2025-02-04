    #
    # -funkcja mutacji (pobiera wektor, zwraca, zmutowany wektor)
    # -funkcja crossover(pobiera 2 wektory, zwraca połączenie)
    # -funkcja celu- liczącą długość trasy (pobiera wektor, zwraca długość trasy)
    # -init
    # -funkcja selekcji
    # -funkcja sukcesji

# example specimen == [A,G,F,D,E,H,B,C]

import datetime
from math import sqrt
from random import randint, shuffle, sample, random
from numpy import array, zeros, full, argpartition, Inf, insert, mean, std, concatenate, linspace
import plotly.express as px
import plotly.graph_objects as go

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
    :return: bazowa lista nazw punktów (służąca później do "translacji") z pliku wejściowego oraz lista koorydnatów
    '''
    points_num = len(points_arg)
    _points_symbolic = [None] * points_num
    _coordinates = [None] * points_num

    idx = 0
    for point, coordinates in points_arg.items():
        _points_symbolic[idx] = point
        _coordinates[idx] = coordinates
        idx = idx + 1

    return _points_symbolic, _coordinates


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


def calculate_distances(coordinates_arg):
    '''
    Funkcja wyznaczająca bezpośrednie odległości pomiędzy punktami
    :param coordinates_arg: lista koordynatów punktów
    :return: macierz zawierająca odległości pomiędzy punktami
    '''
    size = len(coordinates_arg)
    distances = zeros(shape=[size, size])

    for idy in range(size):
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


def mutation(specimen):
    '''
    Implementacja mutacji, losowanie dwóch współrzędnych i zamiana punktu między nimi
    :param specimen: osobnik w formie listy
    :return: zmieniony osobnik w formie listy
    '''
    specimen_length = len(specimen)
    while True:
        (a, b) = (randint(0, specimen_length-1), randint(0, specimen_length-1))
        if a < b:
            break
    specimen[a:b] = specimen[a:b][::-1]
    return specimen


def crossover(parent1, parent2):
    '''
    implementacja krzyżowania dwupunktowego z uwzględnieniem braku możliwości powtórzeń
    :param parent1: rodzic 1
    :param parent2: rodzic 2
    :return: zmieniony osobnik w formie listy
    '''
    # newborn = parent 1 + a piece from parent 2
    specimen_length = len(parent1)
    newborn = ['NULL' for i in range(0, specimen_length)]
    while True:
        (a, b) = (randint(0, specimen_length - 1), randint(0, specimen_length - 1))
        # (a, b) = (2, 6)
        if specimen_length > abs(a-b) > 1:
            break
    if a < b:
        rest = [letter for letter in parent1 if letter not in parent2[a:b]]
        newborn[a:b] = parent2[a:b]
        for nr in list(range(0, a)) + list(range(b, specimen_length)):
            newborn[nr] = rest.pop(0)
    else:
        rest = [letter for letter in parent1 if letter not in parent2[:b] + parent2[a:]]
        newborn[a:] = parent2[a:]
        newborn[:b] = parent2[:b]
        for nr in range(b, a):
            newborn[nr] = rest.pop(0)
    return newborn


def init_population(specimen_length, population_size):
    '''
    Funkcja generująca losową, początkową populację
    :param specimen_length: wielkość osobnika
    :param population_size: wielkość populacji
    :return: początkowa populacja
    '''
    population = [None] * population_size
    base_specimen = list(range(0, specimen_length))
    for idx in range(population_size):
        specimen = base_specimen[:]
        shuffle(specimen)
        population[idx] = specimen

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


def tournament_selection(population, tournament_size, distances):
    '''
    Funkcja dokonująca selekcji turniejowej
    Z populacji wyciągane są osobniki (w liczbie równej wielkości turnieju) i porównywane są ich funkcje celu (długości cyklu)
    zachowany zostaje ten z mniejszą długością.
    Powtarzane do momentu wyczerpania populacji
    :param population: obecna populacja
    :param tournament_size: wielkość turnieju
    :param distances: macierz odległości pomiędzy punktami
    :return: populacja po selekcji turniejowej
    '''
    _population = population[:] # tworzenie kopii populacji, ponieważ w poniższej pętli usuwany są z niej elementy
    tournament_iterations = int(len(population) / tournament_size)
    new_population = [None] * tournament_iterations

    for idx in range(tournament_iterations):
        competing_specimens = sample(list(enumerate(_population)), k=tournament_size)
        indices_to_delete = [None] * tournament_size
        # print(f"Competing specimens: {competing_specimens}")

        best_value = Inf
        best_index = None

        iter = 0
        for specimen in competing_specimens:
            indices_to_delete[iter] = specimen[0]
            iter = iter + 1

            path_evaluation = evaluate(specimen[1], distances)
            # print(f"Specimen: {_population[specimen[0]]} evaluation: {path_evaluation}")
            if path_evaluation < best_value:
                best_value = path_evaluation
                best_index = specimen[0]

        # print(f"Tournament won by: {_population[best_index]}")

        new_population[idx] = _population[best_index]

        for idx in sorted(indices_to_delete, reverse=True):
            del _population[idx]

    return new_population


def elite_succesion(old_population, newborns, num_best_left, distances):
    '''
    Funkcja dokonująca sukcesji elitarnej
    :param old_population: populacja stworzona w poprzedniej iteracji
    :param newborns: nowe osobniki stworzone w obecnej iteracji poprzez krzyżowanie i mutację
    :param num_best_left: liczba najlepszych osobników z old_population, które zostanie zachowana
    :param distances: macierz zawierająca odległości między punktami
    :return: nowa populacja po sukcesji elitarnej
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


def calculate_best_in_population(population, distances):
    '''
    Funkcja zwracająca najlepiej przystosowanego osobnika (najkrótszy cykl) w populacji
    :param population: lista zawierająca całą populację
    :param distances: macierz odległości między punktami
    :return: najkrótszy cykl i jego długość
    '''
    best_specimen = None
    best_value = Inf

    for specimen in population:
        specimen_value = evaluate(specimen, distances)
        if specimen_value < best_value:
            best_specimen = specimen
            best_value = specimen_value

    return best_specimen, best_value


def should_terminate_execution(population, experiment_information, iterations_count_threshold, distances):
    '''
    Funkcja warunkująca koniec wykonywania algorytmu. Sprawdza czy najlepiej przystosowany osobnik
    nowej populacji pokrywa się z dotychczasowym najlepszym osobnikiem.
    Jeśli taka sytuacja powtarza się przez X generacji, algorytm kończy działanie.
    :param population: lista zawierająca całą populację
    :param experiment_information: słownik przechowujący informacje o wykonywującym się algorytmie
    :param iterations_count_threshold: próg X ilości generacji bez poprawy populacji
    :param distances: macierz odległości między punktami
    :return: Boolowska wartość określająca czy działanie algorytmu ma zostać zatrzymane
    '''
    if not experiment_information["current_best"]:
        experiment_information["current_best"], experiment_information["current_best_value"] = calculate_best_in_population(population, distances)
        experiment_information["best_values_array_repeated"] = insert(
                                                        experiment_information["best_values_array_repeated"],
                                                        experiment_information["best_values_array_repeated"].size,
                                                        experiment_information["current_best_value"]
                                                    )
        experiment_information["best_values_array"] = insert(
                                                        experiment_information["best_values_array"],
                                                        experiment_information["best_values_array"].size,
                                                        experiment_information["current_best_value"]
                                                    )
        return False
    else:
        best_in_population, best_value_in_population = calculate_best_in_population(population, distances)
        experiment_information["best_values_array_repeated"] = insert(
                                                            experiment_information["best_values_array_repeated"],
                                                            experiment_information["best_values_array_repeated"].size,
                                                            best_value_in_population
                                                        )
        if best_value_in_population == experiment_information["current_best_value"]:
            experiment_information["iterations_without_change"] = experiment_information["iterations_without_change"] + 1
            if experiment_information["iterations_without_change"] > iterations_count_threshold:
                return True
            else:
                return False
        else:
            # print(f"Best has changed, new best: {best_value_in_population}")
            experiment_information["iterations_without_change"] = 0
            experiment_information["current_best"] = best_in_population
            experiment_information["current_best_value"] = best_value_in_population
            experiment_information["best_values_array"] = insert(
                                                        experiment_information["best_values_array"],
                                                        experiment_information["best_values_array"].size,
                                                        best_value_in_population
                                                    )
            return False


def genetic_operations(specimens, population_size, mutation_probability):
    '''
    Funkcja wykonująca operacje genetyczne na określonych osobnikach
    :param specimens: osobniki, na których będzie dokonywane krzyżowanie i mutacja
    :param population_size: wielkość populacji określona przez warunki początkowe
    :return: nowo stworzone osobniki
    '''
    newborns = [None] * population_size

    for idx in range(population_size):
        [parent_A, parent_B] = sample(specimens, k=2)
        _specimen = crossover(parent_A, parent_B)
        if random() < mutation_probability:
            _specimen = mutation(_specimen)
        newborns[idx] = _specimen

    return newborns
    

def experiment(
    points,
    population_size=500,
    elite_size_percent=15,
    mutation_probability=0.8,
    tournament_size=3,
    iteration_count_end=100,
    plot_best_values=None,
    plot_best_values_repeated=None,
):
    '''
    Funkcja wykonująca cały eksperyment algorytmu ewolucyjnego dla zadanych parametrów
    :param points: słownik punktów i ich koordynatów
    :param population_size: ilość osobników w populacji
    :param elite_size_percent: Ilość najlepszych osobników ze starej populacji przechodzącej do następnej. Domyślna wartość: 30% populacji
    :param mutation_probability: prawdopodobieństwo wystąpienia mutacji, domyślnie 1/10
    :param iteration_count_end: ilość iteracji bez zmiany najlepiej przystosowanego osobnika do zakończenia algorytmu
    :param tournament_size: Wielkość turnieju (liczba porównywanych ze sobą osobników) podczas selekcji turniejowej. Domyślna wartość: 2
    :param iteration_count_end: ilość iteracji bez zmiany najlepiej przystosowanego osobnika do zakończenia algorytmu
    :return: wartość najkrótszego cyklu, osobnik który wygrał, 
        ilość generacji (bez uwzględniania generacji, w których najlepszy osobnik pozostawał bez mian) 
        oraz ilość generacji (z uwzględnieniem wszystkich generacji)
    '''

    elite_size = int(population_size * elite_size_percent/100)
    
    specimen_length = len(points)
    symbolic_points_base, coordinates_list = transform_points_definition(points)
    distances_mtrx = calculate_distances(coordinates_list)

    experiment_information = {
        "current_best": None,
        "current_best_value": Inf,
        "iterations_without_change": 0,
        "best_values_array": array([]),
        "best_values_array_repeated": array([])
    }

    population = init_population(specimen_length, population_size)

    while not should_terminate_execution(population, experiment_information, iteration_count_end, distances_mtrx):
        population_after_selection = tournament_selection(population, tournament_size, distances_mtrx)
        newborns = genetic_operations(population_after_selection, population_size, mutation_probability)
        population = elite_succesion(population, newborns, elite_size, distances_mtrx)

    best_path = experiment_information["current_best"]
    best_value = experiment_information["current_best_value"]
    generations_num = experiment_information["best_values_array"].size
    generations_num_repeated = experiment_information["best_values_array_repeated"].size
    print(f"Najkrótszy cykl zwrócony przez algorytm: {specimen_normalization(get_symbolic_representation(best_path, symbolic_points_base))} " + 
        f"o długości: {best_value}, znaleziony w {generations_num} generacji ({generations_num_repeated} z powtórzeniami)")

    if plot_best_values_repeated:
        plot_best_values_repeated.add_trace(go.Scatter(
                                                    x=list(range(generations_num_repeated)),
                                                    y=experiment_information["best_values_array_repeated"],
                                                    mode='lines', name=""))

    return best_value, specimen_normalization(get_symbolic_representation(best_path, symbolic_points_base)), generations_num, generations_num_repeated


def specimen_normalization(specimen):
    '''
    Przesunięcie w osobniku, żeby zaczynał się od A
    :param specimen:
    :return:
    '''
    _specimen = specimen
    for iteration in range(0, _specimen.index('A')): # A na początek
        _specimen = _specimen[1:] + [_specimen[0]]
    if _specimen[-1] > _specimen[1]: # upewnienie się że cykl będzie zawsze w tą[osamą stronę szedł (kierunek zgodny z alfabetem)
        _specimen = [_specimen[0]] + _specimen[1:][::-1]
    return _specimen


def get_std_bounds(std_values, mean_values):
    y_upper = mean_values + std_values
    y_lower = mean_values - std_values
    return concatenate([y_upper, y_lower[::-1]])


def investigate_population_size(start, end, step_arg, points):
    population_sizes = list(range(start, end, step_arg))
    experiments_per_size = 10
    mean_values = zeros(shape=[len(population_sizes), ])
    std_values = zeros(shape=[len(population_sizes), ])
    min_values = zeros(shape=[len(population_sizes), ])
    max_values = zeros(shape=[len(population_sizes), ])

    generations_mean = zeros(shape=[len(population_sizes), ])
    generations_values = zeros(shape=[len(population_sizes), ])

    for idx, _population_size in enumerate(population_sizes):
        paths_values = zeros(shape=[experiments_per_size,])
        generations = zeros(shape=[experiments_per_size,])
        print(_population_size)
        for expr in range(experiments_per_size):
            expr_result = experiment(points,
                                    population_size=_population_size)
            paths_values[expr] = expr_result[0]
            generations[expr] = expr_result[3]
        
        mean_values[idx] = mean(paths_values)
        std_values[idx] = std(paths_values)
        min_values[idx] = min(paths_values)
        max_values[idx] = max(paths_values)

        generations_mean[idx] = mean(generations)
        generations_values[idx] = std(generations)

    # wyniki w postaci wykresów
    fig = go.Figure([
        go.Scatter(
            x=population_sizes,
            y=mean_values,
            line=dict(color='rgb(227, 51, 39)'),
            mode='lines',
            showlegend=False
        ),
        go.Scatter(
            x=population_sizes+population_sizes[::-1],
            y=concatenate([max_values, min_values[::-1]]),#get_std_bounds(std_values, mean_values),#
            fill='toself',
            fillcolor='rgba(227, 51, 39, 0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            hoverinfo="skip",
            showlegend=False
        )
    ])
    fig.update_layout(
        xaxis_title='Liczba osobników w pokoleniu',
        yaxis_title='Najkrótszy cykl',
        title='Zależność długości najlepszego cyklu od liczebności populacji'
    )
    fig.write_image(f"ppl_size_{start}_{end}_{step_arg}.jpg")
    print(mean_values, std_values)

def investigate_tournament_size(start, end, step_arg, points):
    tournament_sizes = list(range(start, end, step_arg))
    experiments_per_size = 10
    mean_values = zeros(shape=[len(tournament_sizes), ])
    std_values = zeros(shape=[len(tournament_sizes), ])
    min_values = zeros(shape=[len(tournament_sizes), ])
    max_values = zeros(shape=[len(tournament_sizes), ])

    generations_mean = zeros(shape=[len(tournament_sizes), ])
    generations_values = zeros(shape=[len(tournament_sizes), ])

    for idx, _tournament_size in enumerate(tournament_sizes):
        paths_values = zeros(shape=[experiments_per_size, ])
        generations = zeros(shape=[experiments_per_size, ])
        print(_tournament_size)
        for expr in range(experiments_per_size):
            expr_result = experiment(points,
                                     tournament_size=_tournament_size)
            paths_values[expr] = expr_result[0]
            generations[expr] = expr_result[3]

        mean_values[idx] = mean(paths_values)
        std_values[idx] = std(paths_values)
        min_values[idx] = min(paths_values)
        max_values[idx] = max(paths_values)

        generations_mean[idx] = mean(generations)
        generations_values[idx] = std(generations)

    # wyniki w postaci wykresów
    fig = go.Figure([
        go.Scatter(
            x=tournament_sizes,
            y=mean_values,
            line=dict(color='rgb(227, 51, 39)'),
            mode='lines',
            showlegend=False
        ),
        go.Scatter(
            x=tournament_sizes + tournament_sizes[::-1],
            y=concatenate([max_values, min_values[::-1]]),#get_std_bounds(std_values, mean_values),
            fill='toself',
            fillcolor='rgba(227, 51, 39, 0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            hoverinfo="skip",
            showlegend=False
        )
    ])
    fig.update_layout(
        xaxis_title='Liczba osobników uczestniczących w turnieju',
        yaxis_title='Najkrótszy cykl',
        title='Zależność długości najlepszego cyklu od wielkości turnieju'
    )
    fig.write_image(f"trnmt_size_{start}_{end}_{step_arg}.jpg")
    print(mean_values, std_values)

def investigate_elitarism(start, end, step_arg, points):
    elite_sizes = list(range(start, end, step_arg))
    experiments_per_size = 10
    mean_values = zeros(shape=[len(elite_sizes), ])
    std_values = zeros(shape=[len(elite_sizes), ])
    min_values = zeros(shape=[len(elite_sizes), ])
    max_values = zeros(shape=[len(elite_sizes), ])

    generations_mean = zeros(shape=[len(elite_sizes), ])
    generations_values = zeros(shape=[len(elite_sizes), ])

    for idx, _elite_size in enumerate(elite_sizes):
        paths_values = zeros(shape=[experiments_per_size,])
        generations = zeros(shape=[experiments_per_size,])
        print(_elite_size)
        for expr in range(experiments_per_size):
            expr_result = experiment(points,
                                    # population_size=600,
                                    elite_size_percent=_elite_size)
            paths_values[expr] = expr_result[0]
            generations[expr] = expr_result[3]
        
        mean_values[idx] = mean(paths_values)
        std_values[idx] = std(paths_values)
        min_values[idx] = min(paths_values)
        max_values[idx] = max(paths_values)

        generations_mean[idx] = mean(generations)
        generations_values[idx] = std(generations)

    # wyniki w postaci wykresów
    fig = go.Figure([
        go.Scatter(
            x=elite_sizes,
            y=mean_values,
            line=dict(color='rgb(50, 168, 82)'),
            mode='lines',
            showlegend=False
        ),
        go.Scatter(
            x=elite_sizes+elite_sizes[::-1],
            y=concatenate([max_values, min_values[::-1]]),#get_std_bounds(std_values, mean_values),
            fill='toself',
            fillcolor='rgba(50, 168, 82, 0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            hoverinfo="skip",
            showlegend=False
        )
    ])
    fig.update_layout(
        xaxis_title='Najkrótszy cykl',
        yaxis_title='Rozmiar elity',
        title='Zależność długości najkrótszego cyklu od rozmiaru elity'
    )
    fig.write_image(f"elite_size_{start}_{end}_{step_arg}.jpg")
    print(mean_values, std_values)


def investigate_mutation(start, end, step_arg, points):
    mutation_probabilites = list(linspace(start, end, num=int((end-start)/step_arg + 1)))
    print(mutation_probabilites)
    experiments_per_size = 10
    mean_values = zeros(shape=[len(mutation_probabilites), ])
    std_values = zeros(shape=[len(mutation_probabilites), ])
    min_values = zeros(shape=[len(mutation_probabilites), ])
    max_values = zeros(shape=[len(mutation_probabilites), ])

    generations_mean = zeros(shape=[len(mutation_probabilites), ])
    generations_values = zeros(shape=[len(mutation_probabilites), ])

    for idx, _mutation_probability in enumerate(mutation_probabilites):
        paths_values = zeros(shape=[experiments_per_size,])
        generations = zeros(shape=[experiments_per_size,])
        print( _mutation_probability)
        for expr in range(experiments_per_size):
            expr_result = experiment(points,
                                    # population_size=300,
                                    # elite_size=90,
                                    mutation_probability=_mutation_probability)
            paths_values[expr] = expr_result[0]
            generations[expr] = expr_result[3]
        
        mean_values[idx] = mean(paths_values)
        std_values[idx] = std(paths_values)
        min_values[idx] = min(paths_values)
        max_values[idx] = max(paths_values)

        generations_mean[idx] = mean(generations)
        generations_values[idx] = std(generations)

    # wyniki w postaci wykresów
    fig = go.Figure([
        go.Scatter(
            x=mutation_probabilites,
            y=mean_values,
            line=dict(color='rgb(64, 0, 224)'),
            mode='lines',
            showlegend=False
        ),
        go.Scatter(
            x=mutation_probabilites+mutation_probabilites[::-1],
            y=concatenate([max_values, min_values[::-1]]),#get_std_bounds(std_values, mean_values),
            fill='toself',
            fillcolor='rgba(64, 0, 224, 0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            hoverinfo="skip",
            showlegend=False
        )
    ])
    fig.update_layout(
        xaxis_title='Prawdopodobieństwo mutacji',
        yaxis_title='Najkrótszy cykl',
        title='Zależność długości najkrótszego cyklu zwracanego przez algorytm, \nw funkcji prawdopodobieństwa mutacji'
    )
    fig.write_image(f"probability_{start}_{end}_{step_arg}.jpg")
    print(mean_values, std_values)

def investigate_iteration_count_end(start, end, step_arg, points):
    iteration_count_end = list(linspace(start, end, num=int((end - start) / step_arg + 1)))
    print(iteration_count_end)
    experiments_per_size = 10
    mean_values = zeros(shape=[len(iteration_count_end), ])
    std_values = zeros(shape=[len(iteration_count_end), ])
    min_values = zeros(shape=[len(iteration_count_end), ])
    max_values = zeros(shape=[len(iteration_count_end), ])

    generations_mean = zeros(shape=[len(iteration_count_end), ])
    generations_values = zeros(shape=[len(iteration_count_end), ])

    for idx, _iteration_count_end in enumerate(iteration_count_end):
        paths_values = zeros(shape=[experiments_per_size, ])
        generations = zeros(shape=[experiments_per_size, ])
        print(_iteration_count_end)
        for expr in range(experiments_per_size):
            expr_result = experiment(points,
                                     # population_size=300,
                                     # elite_size=90,
                                     iteration_count_end=_iteration_count_end)
            paths_values[expr] = expr_result[0]
            generations[expr] = expr_result[3]

        mean_values[idx] = mean(paths_values)
        std_values[idx] = std(paths_values)
        min_values[idx] = min(paths_values)
        max_values[idx] = max(paths_values)

        generations_mean[idx] = mean(generations)
        generations_values[idx] = std(generations)

    # wyniki w postaci wykresów
    fig = go.Figure([
        go.Scatter(
            x=iteration_count_end,
            y=mean_values,
            line=dict(color='rgb(64, 0, 224)'),
            mode='lines',
            showlegend=False
        ),
        go.Scatter(
            x=iteration_count_end + iteration_count_end[::-1],
            y=concatenate([max_values, min_values[::-1]]),  # get_std_bounds(std_values, mean_values),
            fill='toself',
            fillcolor='rgba(64, 0, 224, 0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            hoverinfo="skip",
            showlegend=False
        )
    ])
    fig.update_layout(
        xaxis_title='Liczba iteracji bez zmian po której kończymy eksperyment',
        yaxis_title='Najkrótszy cykl',
        title='Zależność długości cyklu od warunku stopu'
    )
    fig.write_image(f"iteration_count_end_{start}_{end}_{step_arg}.jpg")
    print(mean_values, std_values)

def run_experiment_with_time_markers():
    experiments_num = 10
    values = zeros(shape=[experiments_num, ])
    generations = zeros(shape=[experiments_num, ])
    time = [None] * experiments_num

    for idx in range(experiments_num):
        time_start = datetime.datetime.now()
        expr_result = experiment(points,
                                population_size=700,
                                elite_size_percent=15, 
                                iteration_count_end=200)
        time_stop = datetime.datetime.now()
        values[idx] = expr_result[0]
        generations[idx] = expr_result[3]
        time[idx] = (time_stop - time_start).total_seconds()

    print(f"Długości cykli: {values}\nŚrednia długość cyklu: {mean(values)}")
    print(f"Liczba generacji: {generations}\nŚrednia liczba generacji: {mean(generations)}")
    print(f"Czasy wykonania: {time}\nŚrednie czasy wykonań: {mean(time)}")


if __name__ == "__main__":
    (points, specimen_length) = load()
    plot = go.Figure()
    najlepsze = []

    # uruchamiane na wartościach domyślnych, ustawionych w funkcji def experiment
    # investigate_population_size(start=10, end=2011, step_arg=50, points=points)
    # investigate_tournament_size(start=2, end=10, step_arg=1, points=points)
    # investigate_elitarism(start=1, end=100, step_arg=9, points=points)
    # investigate_mutation(start=0.01, end=1.01, step_arg=0.05, points=points)
    investigate_iteration_count_end(start=10, end=510, step_arg=50, points=points)

    # experiment(points,
    #             population_size=200,
    #             elite_size_percent=20,
    #             tournament_size=3,
    #             iteration_count_end=400,
    #             mutation_probability=0.75,
    #             plot_best_values_repeated=plot)

    # run_experiment_with_time_markers()