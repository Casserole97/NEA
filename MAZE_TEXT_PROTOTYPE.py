from random import choice, random

#Basic class that acts as a coordinate on a map.
#Only needed for other classes to inherit from.
class Tile():
    def __init__(self, row, col):
        self.row = row
        self.col = col

    #Return row and column.
    def GetPos(self):
        return self.row, self.col

#A tile that cannot be walked through.
class Wall(Tile):
    def __init__(self, row, col):
        super().__init__(row, col)
        self.type = "WALL"

#A tile that can be walked through. It acts as the nodes of a graph.
class Cell(Tile):
    def __init__(self, row, col):
        super().__init__(row, col)
        self.type = "CELL"
        self.visited = False

    #Return a boolean.
    def IsVisited(self):
        return self.visited
    
    #Change the visited status.
    def Visit(self):
        self.visited = True

#The passage class is used to indiciate a connection between cells.
#Can be walked through.
#Can be described as the edges between nodes.
#(A passage must be used instead of cells when connecting them for several reasons)
class Passage(Tile):
    def __init__(self, row, col):
        super().__init__(row, col)
        self.type = "PASSAGE"

#The grid class is basically a two dimensional array with special methods.
#Each space will hold either a wall, a cell, or a passage.
class Grid():
    def __init__(self, vertical_cells, horizontal_cells):
        self.MAX_ROW = vertical_cells*2+1
        self.MAX_COL = horizontal_cells*2+1
        #Initialize a blank grid of walls and cells.
        self.grid = [[self.__GenerateCellorWall(row, col) for col in range(0, self.MAX_COL)] for row in range(0, self.MAX_ROW)]
    
    #Method used in the init of the grid.
    def __GenerateCellorWall(self, row, col):
        if row % 2 != 0 and col % 2 != 0:
            return Cell(row, col)
        else:
            return Wall(row, col)
    
    #Displays the maze in a textual form.
    def DisplayMaze(self):
        for row in self.grid:
            print()
            for tile in row:
                if tile.type == "WALL":
                    print('H ', end='')
                else:
                    print('  ', end='')
    
    #Return the tile on that row and column.
    def Tile(self, row, col):
        return self.grid[row][col]
    
    #Returns a list of adjacent unvisited neighbours of a cell.
    def GetUnvisitedNeighbours(self, cell):
        unvisited_neighbours = []
        row, col = cell.GetPos()
        N = -2
        E = 2
        S = 2
        W = -2
        try:
            if not self.Tile(row+N, col).IsVisited():
                unvisited_neighbours.append(self.Tile(row+N, col))
        except:
            pass
        try:
            if not self.Tile(row, col+E).IsVisited():
                unvisited_neighbours.append(self.Tile(row, col+E))
        except:
            pass
        try:
            if not self.Tile(row+S, col).IsVisited():
                unvisited_neighbours.append(self.Tile(row+S, col))
        except:
            pass
        try:
            if not self.Tile(row, col+W).IsVisited():
                unvisited_neighbours.append(self.Tile(row, col+W))
        except:
            pass
        return unvisited_neighbours
    
    #Changes the wall between two cells to a passage.
    def CarvePassage(self, cell1, cell2):
        row = (cell1.row + cell2.row) // 2
        col = (cell1.col + cell2.col) // 2
        self.grid[row][col] = Passage(row, col)
    
    #Recursive backtracker algorithm.
    def RecursiveBacktracker(self, cell, loop_chance):
        neighbours = self.GetUnvisitedNeighbours(cell)
        cell.Visit()
        while len(neighbours) != 0:
            next_cell = choice(neighbours)
            neighbours.remove(next_cell)
            if not next_cell.IsVisited(): 
                self.CarvePassage(cell, next_cell)
            elif random() < loop_chance:
                self.CarvePassage(cell, next_cell)
            self.RecursiveBacktracker(next_cell, loop_chance)

maze1 = Grid(12, 12)
maze1.RecursiveBacktracker(maze1.Tile(1, 1), 0.1)
maze1.DisplayMaze()