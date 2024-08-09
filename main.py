# from hub import light_matrix, port, sound, motion_sensor
# import runloop, force_sensor, motor, color_sensor, distance_sensor, color
from enum import Enum
from typing import Tuple
import time


# to double check:
# RightMotor = port.A
# LeftMotor = port.C
# ColorSensor = port.D
# DistanceSensor = port.E
#
# # to fine tune:
#
# regular_white_max_reflected = 99
#
#
# # place on white tile, run fine tuning, wait for a couple seconds, see the value, add two to it, and put it here
#
# async def main():
#     light_matrix.show([0, 0, 0, 0, 0, 0, 100, 0, 100, 0, 0, 0, 100, 0, 0, 0, 100, 100, 100, 0, 0, 100, 0, 100, 0])
#     # motor.run(port.B, 100)
#     # motor.run(port.B, 100)
#
#
# def turn90(right: bool):
#     if right:
#         motor.run_for_degrees(LeftMotor, -130, 80)
#         motor.run_for_degrees(RightMotor, -130, 80)
#     else:
#         motor.run_for_degrees(LeftMotor, 130, 80)
#         motor.run_for_degrees(RightMotor, 130, 80)
#
#
# def forward():
#     motor.run_for_degrees(RightMotor, 600, 100)
#     motor.run_for_degrees(LeftMotor, -600, 100)
#
#
# def angle() -> float:
#     angles = motion_sensor.tilt_angles()
#     yaw = angles[0]
#     return yaw * 10
#     # TODO: check that this actually works
#
#
# def checked_forward():
#     forward()
#
#
# def process_square():
#     # fetch data
#     _color = color_sensor.color(ColorSensor)
#     _reflection = color_sensor.reflection(ColorSensor)
#     distance = distance_sensor.distance(DistanceSensor)
#     cell = Cell(0, 0, 0, 0, 0, True)
#     # Check the color of the square
#     if _color == 10:
#         if _reflection > regular_white_max_reflected:
#             # silver
#             print("silver")
#             cell.color = 2
#         else:
#             # white
#             print("white")
#             cell.color = 0
#
#     elif _color == 0:
#         # black
#         print("black")
#         cell.color = 1

class Wall(Enum):
    EMPTY = 0
    WALL = 1
    VICTIM = 2
    SOMETHING = 3


class Cell:
    color = 0
    northWall = Wall(0)
    southWall = Wall(0)
    eastWall = Wall(0)
    westWall = Wall(0)
    hasBeenFound = False

    def __init__(self, color: int, walls:[int], hasBeenFound: bool):
        self.color = color
        self.northWall = Wall(walls[0])
        self.eastWall = Wall(walls[1])
        self.southWall = Wall(walls[2])
        self.westWall = Wall(walls[3])
        self.hasBeenFound = hasBeenFound

    @staticmethod
    def default():
        return Cell(0, [0, 0, 0, 0], False)


class Path:
    length = 0
    start = Cell.default
    instructions = []
    cells = [()]
    currentCell = Cell.default()

    def append(self, direction: int, junction: bool):
        if junction:
            self.instructions.append("X" + str(direction))
        else:
            self.instructions.append(str(direction))
        if direction == 0:
            self.cells.append((int(self.cells[self.length][0]), int(self.cells[self.length][1]) - 1))
        if direction == 1:
            self.cells.append((int(self.cells[self.length][0]) + 1, int(self.cells[self.length][1])))
        if direction == 2:
            self.cells.append((int(self.cells[self.length][0]), int(self.cells[self.length][1]) + 1))
        if direction == 3:
            self.cells.append((int(self.cells[self.length][0]) - 1, int(self.cells[self.length][1])))
        self.length += 1
        self.currentCell = maze.getCell(self.cells[self.length][0], self.cells[self.length][1])

    def cull(self, _path):
        print("before cull: " + str(_path.instructions))
        indexOfLatestJunction = 0
        for _i in range(len(self.instructions)):
            v = len(self.instructions) - _i - 1
            print("variables. _i: " + str(_i) + ". v: " + str(v))
            if self.instructions[v][0] == "X":
                # we found him
                lastInstructions = list(self.instructions[v][1:])
                self.length = v  # ±1?
                self.instructions = self.instructions[:v]
                self.cells = self.cells[:v+1]
                self.currentCell = maze.getCell(int(self.cells[len(self.cells) - 1][0]), int(self.cells[len(self.cells) - 1][1]))

                options = Maze.getOptions(self.currentCell, _path)
                for h in lastInstructions:
                    if int(h) in options:
                        options.remove(int(h))
                print("after-cull options: " + str(options))
                _path.append(options[0], len(options) > 1)
                print("after cull: " + str(_path.instructions))
                return _path


class Maze:
    cells = [[Cell(0, [0, 0, 0, 0], True)]]
    # Note: x is horizontal value, starting at 0 from left, y is vertical value, starting from 0 at top.

    width: int = 1
    height: int = 1

    def expand(self, direction: int):
        if direction == 0:
            newRow = []
            for o in range(self.width):
                newRow.append(Cell.default())
            tempCells = self.cells
            self.cells = []
            self.cells.append(newRow)
            for o in range(self.height):
                self.cells.append(tempCells[o])
            self.height += 1
        elif direction == 1:
            for o in range(self.height):
                self.cells[o].append(Cell.default())
            self.width += 1
        elif direction == 2:
            newRow = []
            for o in range(self.width):
                newRow.append(Cell.default())
            self.cells.append(newRow)
            self.height += 1
        elif direction == 3:
            for o in range(self.height):
                tempRow = self.cells[o]
                self.cells[o] = []
                self.cells[o].append(Cell.default())
                for v in range(len(tempRow)):
                    self.cells[o].append(tempRow[v])
            self.width += 1

    def getCell(self, _x: int, _y: int) -> Cell:
        # print("getting cell. y val: " + str(_y) + ". x val: " + str(_x))
        return self.cells[_y][_x]

    def setCell(self, _x, _y, color: int, northWall: int, southWall: int, eastWall: int, westWall: int, hasBeenFound: bool):
        self.cells[_y][_x] = Cell(color, [northWall, southWall, eastWall, westWall], hasBeenFound)

    def setWall(self, cell_x: int, cell_y: int, wall: int, to_set: Wall):
        if wall == 0:
            self.cells[cell_y][cell_x].northWall = to_set
        if wall == 1:
            self.cells[cell_y][cell_x].eastWall = to_set
        if wall == 2:
            self.cells[cell_y][cell_x].southWall = to_set
        if wall == 3:
            self.cells[cell_y][cell_x].westWall = to_set

    def getSize(self) -> Tuple:
        return self.width, self.height

    def getOptions(self, coordinates: tuple, __path) -> list:
        if coordinates[0] > self.width or coordinates[1] > self.height or coordinates[0] < 0 or coordinates[1] < 0:
            return []
        cell = self.getCell(coordinates[0], coordinates[1])
        _options = []
        if __path is not None:
            print("checking: " + str(__path.cells[:len(__path.cells) - 1]) + " this is what checking for: " + str((int(__path.cells[len(__path.cells) - 1][0]), int(__path.cells[len(__path.cells) - 1][1]) - 1)))
            if cell.northWall == Wall.EMPTY and not __path.cells[:len(__path.cells) - 1].__contains__((__path.cells[len(__path.cells) - 1][0], int(__path.cells[len(__path.cells) - 1][1]) - 1)):
                if len(__path.instructions) > 0 and __path.instructions[len(__path.instructions) - 1] != "2" and __path.instructions[len(__path.instructions) - 1] != "X2":
                    _options.append(0)
                elif len(__path.instructions) == 0:
                    _options.append(0)
            if cell.southWall == Wall.EMPTY and not __path.cells[:len(__path.cells) - 1].__contains__((__path.cells[len(__path.cells) - 1][0], int(__path.cells[len(__path.cells) - 1][1]) + 1)):
                if len(__path.instructions) > 0 and __path.instructions[len(__path.instructions) - 1] != "0" and __path.instructions[len(__path.instructions) - 1] != "X0":
                    _options.append(2)
                elif len(__path.instructions) == 0:
                    _options.append(2)
            if cell.eastWall == Wall.EMPTY and not __path.cells[:len(__path.cells) - 1].__contains__((int(__path.cells[len(__path.cells) - 1][0]) + 1, __path.cells[len(__path.cells) - 1][1])):
                if len(__path.instructions) > 0 and __path.instructions[len(__path.instructions) - 1] != "3" and __path.instructions[len(__path.instructions) - 1] != "X3":
                    _options.append(1)
                elif len(__path.instructions) == 0:
                    _options.append(1)
            if cell.westWall == Wall.EMPTY and not __path.cells[:len(__path.cells) - 1].__contains__((int(__path.cells[len(__path.cells) - 1][0]) - 1, __path.cells[len(__path.cells) - 1][1])):
                if len(__path.instructions) > 0 and __path.instructions[len(__path.instructions) - 1] != "1" and __path.instructions[len(__path.instructions) - 1] != "X1":
                    _options.append(3)
                elif len(__path.instructions) == 0:
                    _options.append(3)

        else:
            if cell.northWall == Wall.EMPTY and self.height > coordinates[1] + 1:
                _options.append(0)
            if cell.southWall == Wall.EMPTY and self.height > coordinates[1] - 1:
                _options.append(2)
            if cell.eastWall == Wall.EMPTY and self.width > coordinates[0] + 1:
                _options.append(1)
            if cell.westWall == Wall.EMPTY and self.width > coordinates[0] - 1:
                _options.append(3)

            return _options

    def pathFind(self, start: tuple, end: tuple) -> Path:
        _path = Path()
        _path.cells[0] = start
        _path.currentCell = self.getCell(int(start[0]), int(start[1]))
        hasFoundPath = False

        # find a path. Logic: take the starting square. pick a random path going in the direction of the end, continue until a dead end or the end is found. When dead end found, delete path back until the last fork and take another option.
        iteration = 0
        while not hasFoundPath:
            print()
            iteration += 1
            # time.sleep(1)
            print("Iteration: " + str(iteration))
            print("Path: " + str(_path.instructions))
            if iteration > 100:
                print("No path found.")
                break
            currentCell = _path.cells[len(_path.cells) - 1]
            desiredDirection1 = 0  # --> the first direction we want to go. Will always be vertical, unless at the same y coord as the target.
            desiredDirection2 = 1  # --> 2nd priority. For example, if going up and right, will be right(1).

            print(_path.cells[:len(_path.cells) - 1])
            if _path.cells[:len(_path.cells) - 1].__contains__(_path.cells[len(_path.cells) - 1]):
                _path = _path.cull(_path)
                continue
            if int(end[1]) < int(currentCell[1]):
                # thing is above.
                if int(end[0]) > int(currentCell[0]):
                    pass
                else:
                    desiredDirection2 = 3
            elif int(end[1]) > int(currentCell[1]):
                # thing is below.
                desiredDirection1 = 2
                if int(end[0]) > int(currentCell[0]):
                    pass
                else:
                    desiredDirection2 = 3
            else:
                if int(end[0]) > int(currentCell[0]):
                    desiredDirection1 = 1
                else:
                    if int(end[0]) == int(currentCell[0]):
                        print("Pathfind complete.")
                        return _path
                    else:
                        desiredDirection1 = 3

            print("desired: " + str(desiredDirection1) + str(desiredDirection2))
            print("current cell: " + str([_path.currentCell.northWall, _path.currentCell.eastWall, _path.currentCell.southWall, _path.currentCell.westWall]))

            options = self.getOptions(_path.currentCell, _path)
            print("options:" + str(options))

            if options.__contains__(desiredDirection1) and len(options) > 1:
                # the _path can go multiple ways (note: its 1 because we (^)screened for where we came from already.)
                _path.append(desiredDirection1, True)
                print(_path.instructions)
                continue
            elif len(options) == 1:
                # we can only go one way. Doesn't matter whether it's desired or not, we be going in that direction.
                _path.append(options[0], False)
                print(_path.instructions)
                continue
            elif len(options) > 1:
                # we can't go straight there, and we have multiple options. Pick a different direction and go along the _path(2nd priority if possible).
                if options.__contains__(desiredDirection2):
                    _path.append(desiredDirection2, True)
                    print(_path.instructions)
                    continue
                else:
                    # this is my way of choosing a random leftover option. Neither desired path is available, so just go somewhere.
                    _path.append(options[0], True)
                    print(_path.instructions)
                    continue
            else:
                # no options. time to delete the _path until the last junction, then start again from there.
                _path = _path.cull(_path)
                continue

        return _path


def printMaze():
    for y in range(len(maze.cells)):
        _row = ""
        for x in range(len(maze.cells[0])):
            cell = maze.getCell(x, y)
            _row = _row + " " + str(
                [cell.northWall.value, cell.eastWall.value, cell.southWall.value, cell.westWall.value])
        print(_row)


maze = Maze()
location = (0, 0)

while True:
    # testing run loop: pycharm only.
    task = input("--> ").split()
    if task[0] == "getMaze":
        print("Width:", maze.width, "Height:", maze.height)
        # print("Raw Cells: " + str([[maze.cells[x]]]))
        print("Printing Maze...")
        printMaze()
    if task[0] == "defaultMaze":
        maze.cells = [
            [Cell(0, [1, 1, 0, 1], True), Cell(0, [1, 0, 0, 1], True), Cell(0, [1, 0, 0, 0], False), Cell(0, [1, 0, 1, 0], True), Cell(0, [1, 0, 0, 0], True), Cell(0, [1, 0, 0, 0], True), Cell(0, [1, 0, 0, 0], True), Cell(0, [1, 1, 0, 0], True)],
            [Cell(0, [0, 1, 0, 1], True), Cell(0, [0, 1, 1, 1], False), Cell(0, [0, 0, 1, 1], True), Cell(0, [1, 1, 0, 0], True), Cell(0, [0, 0, 0, 1], True), Cell(0, [0, 0, 0, 0], True), Cell(0, [1, 0, 1, 1], True), Cell(0, [0, 1, 0, 0], True)],
            [Cell(0, [0, 0, 0, 1], True), Cell(0, [1, 1, 1, 0], False), Cell(0, [1, 0, 1, 1], True), Cell(0, [0, 0, 1, 0], True), Cell(0, [0, 0, 1, 0], True), Cell(0, [0, 0, 1, 0], True), Cell(0, [1, 1, 0, 0], True), Cell(0, [0, 1, 0, 1], True)],
            [Cell(0, [0, 0, 0, 1], True), Cell(0, [1, 0, 0, 0], True), Cell(0, [1, 0, 0, 0], True), Cell(0, [1, 1, 0, 0], True), Cell(0, [1, 0, 0, 1], True), Cell(0, [1, 0, 0, 0], True), Cell(0, [1, 1, 0, 0], True), Cell(0, [0, 1, 0, 1], True)],
            [Cell(0, [0, 0, 1, 1], True), Cell(0, [0, 0, 1, 0], False), Cell(0, [0, 1, 1, 0], True), Cell(0, [0, 0, 1, 1], True), Cell(0, [0, 0, 1, 0], True), Cell(0, [0, 1, 1, 0], True), Cell(0, [0, 0, 1, 1], True), Cell(0, [0, 1, 1, 0], True)]

        ]
        maze.height = 8
        maze.width = 5
        print("Maze Updated")
    if task[0] == "newMaze":
        maze = Maze()
        print("Maze Reset")
    if task[0] == "buildMaze":
        for i in range(int(task[1])):
            maze.expand(0)
        for i in range(int(task[2])):
            maze.expand(1)
    if task[0] == "getCell":
        print(str(maze.getCell(int(task[1]), int(task[2]))))
    if task[0] == "setCell":
        maze.setCell(int(task[1]), int(task[2]), 0, int(task[3]), int(task[4]), int(task[5]), int(task[6]), True)
    if task[0] == "pathFind":
        print("Starting pathfind. Current Maze: ")
        printMaze()
        start = tuple(map(int, task[1]))
        end = tuple(map(int, task[2]))
        print(str(maze.pathFind(start, end).instructions))
        print("Pathfind Complete")
    if task[0] == "testCull":
        path = Path()
        path.cells[0] = (0, 10)
        for i in range(len(task) - 1):
            path.append(int(task[i + 1][0]), (len(task[i + 1]) > 1 and task[i + 1][1] == "X"))
        print("Instructions before: " + str(path.instructions) + ". cells: " + str(path.cells))
        print("cull: " + path.cull(path))
        print("Instructions after: " + str(path.instructions) + ". cells: " + str(path.cells))
    if task[0] == "doLoop":
        undiscovered = {}
        for row in range(len(maze.cells)):
            for column in range(len(maze.cells[row])):  # may need - 1
                if not maze.cells[row][column].hasBeenFound:
                    print("row: " + str(row), "col: " + str(column))
                    priority = 0
                    for i in maze.getOptions((column, row), None):
                        if i == 0:
                            if not maze.getCell(column, row - 1).hasBeenFound:
                                priority += 1
                        if i == 1:
                            if not maze.getCell(column + 1, row).hasBeenFound:
                                priority += 1
                        if i == 2:
                            if not maze.getCell(column, row + 1).hasBeenFound:
                                priority += 1
                        if i == 3:
                            if not maze.getCell(column - 1, row).hasBeenFound:
                                priority += 1
                    undiscovered[(row, column)] = (len(maze.pathFind(location, tuple(str(row) + str(column))).instructions), )
        

