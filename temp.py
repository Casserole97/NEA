numpad1 = [[1, 2, 3],
           [4, 5, 6],
           [7, 8, 9]]

numpad2 = [[1, 4, 7],
           [2, 5, 8],
           [3, 6, 9]]

# def oddoreven(x, y):
#     if x % 2 != 0 and y % 2 != 0:
#         return 0
#     else:
#         return 1

# maze = [[oddoreven(x, y) for x in range(0, 5)] for y in range(0, 5)]

def display_numpad1():
    for row in numpad1:
        for col in row:
            print(str(col)+' ', end='')
        print()

def display_numpad2():
    for y in range(3):
        for x in range(3):
            print(str(numpad2[x][y])+' ', end='')
        print()

x, y = 0, 2
print(numpad1[y][x])
print(numpad2[x][y])

print("Numpad1:")
display_numpad1()

print("Numpad2:")
display_numpad2()