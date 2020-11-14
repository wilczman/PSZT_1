

def load():
    points = {}
    with open("WE.txt") as file:
        for line in file.readlines():
            temp = line.split(' ')
            points[temp[0]] = (int(temp[1]), int(temp[2]))
