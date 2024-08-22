from hub import port, motion_sensor, button
import motor, distance_sensor, color_sensor, runloop
import time, math

# to double check:
RightMotor = port.A
LeftMotor = port.C
ColorSensor = port.D
DistanceSensor = port.E

# to fine tune:

regular_white_max_reflected = 99


# place on white tile, run fine tuning, wait for a couple seconds, see the value, add two to it, and put it here


def setUpDirection(pastD: list) -> int:
    if len(pastD) == 0:
        return 0
    if len(pastD) > 5:
        pastD = pastD[(len(pastD) - 1):]
    forAVG = 0
    for i in pastD:
        forAVG += i
        print(round(forAVG / len(pastD)))
    return round(forAVG / len(pastD))


def Turn(right: bool):
    global direction, facing
    if right:
        motor.run_for_degrees(LeftMotor, -130, 80)
        motor.run_for_degrees(RightMotor, -130, 80)
    else:
        motor.run_for_degrees(LeftMotor, 130, 80)
        motor.run_for_degrees(RightMotor, 130, 80)


def forward():
    motor.run_for_degrees(RightMotor, 600, 100)
    motor.run_for_degrees(LeftMotor, -600, 100)


def angle() -> float:
    angles = motion_sensor.tilt_angles()
    yaw = angles[0]
    return yaw * 10
    # TODO: check that this actually works


def checked_forward():
    forward()


def process_square():
    # fetch data
    _color = color_sensor.color(ColorSensor)
    _reflection = color_sensor.reflection(ColorSensor)
    distance = distance_sensor.distance(DistanceSensor)
    cell = Cell.default()
    cell.hasBeenFound = True
    # Check the color of the square
    if _color == 10:
        if _reflection > regular_white_max_reflected:
            # silver
            print("silver")
            cell.color = 2
        else:
            # white
            print("white")
            cell.color = 0

    elif _color == 0:
        # black
        print("black")
        cell.color = 1


class Cell:
    color = 0
    northWall = 0  # 0 = no wall, 1 = probably wall, 2 = wall
    southWall = 0
    eastWall = 0
    westWall = 0
    hasBeenFound = False

    def __init__(self, color: int, walls: list[int], hasBeenFound: bool):
        self.color = color
        self.northWall = walls[0]
        self.eastWall = walls[1]
        self.southWall = walls[2]
        self.westWall = walls[3]
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
        indexOfLatestJunction = 0
        for _i in range(len(_path.instructions)):
            v = len(self.instructions) - _i - 1
            if self.instructions[v][0] == "X":
                # we found him
                lastInstructions = list(self.instructions[v][1:])
                self.length = v  # ±1?
                self.instructions = self.instructions[:v]
                self.cells = self.cells[:v + 1]
                self.currentCell = maze.getCell(int(self.cells[len(self.cells) - 1][0]),
                                                int(self.cells[len(self.cells) - 1][1]))

                options = Maze.getOptions(_path)
                for h in lastInstructions:
                    if int(h) in options:
                        options.remove(int(h))
                _path.append(options[0], len(options) > 1)
                break
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

    def setCell(self, _x, _y, color: int, northWall: int, southWall: int, eastWall: int, westWall: int,
                hasBeenFound: bool):
        self.cells[_y][_x] = Cell(color, [northWall, southWall, eastWall, westWall], hasBeenFound)

    def getSize(self):
        return self.width, self.height

    @staticmethod
    def getOptions(__path: Path) -> list:
        _options = []
        if __path.currentCell.northWall == 0 and not (__path.cells[len(__path.cells) - 1][0],
                                                      int(__path.cells[len(__path.cells) - 1][1]) - 1) in __path.cells[
                                                                                                          :len(__path.cells) - 1]:
            if len(__path.instructions) > 0 and __path.instructions[len(__path.instructions) - 1] != "2" and \
                    __path.instructions[len(__path.instructions) - 1] != "X2":
                _options.append(0)
            elif len(__path.instructions) == 0:
                _options.append(0)
        if __path.currentCell.southWall == 0 and not (__path.cells[len(__path.cells) - 1][0],
                                                      int(__path.cells[len(__path.cells) - 1][1]) + 1) in __path.cells[
                                                                                                          :len(__path.cells) - 1]:
            if len(__path.instructions) > 0 and __path.instructions[len(__path.instructions) - 1] != "0" and \
                    __path.instructions[len(__path.instructions) - 1] != "X0":
                _options.append(2)
            elif len(__path.instructions) == 0:
                _options.append(2)
        if __path.currentCell.eastWall == 0 and not (int(__path.cells[len(__path.cells) - 1][0]) + 1,
                                                     __path.cells[len(__path.cells) - 1][1]) in __path.cells[
                                                                                                :len(__path.cells) - 1]:
            if len(__path.instructions) > 0 and __path.instructions[len(__path.instructions) - 1] != "3" and \
                    __path.instructions[len(__path.instructions) - 1] != "X3":
                _options.append(1)
            elif len(__path.instructions) == 0:
                _options.append(1)
        if __path.currentCell.westWall == 0 and not (int(__path.cells[len(__path.cells) - 1][0]) - 1,
                                                     __path.cells[len(__path.cells) - 1][1]) in __path.cells[
                                                                                                :len(__path.cells) - 1]:
            if len(__path.instructions) > 0 and __path.instructions[len(__path.instructions) - 1] != "1" and \
                    __path.instructions[len(__path.instructions) - 1] != "X1":
                _options.append(3)
            elif len(__path.instructions) == 0:
                _options.append(3)

        return _options

    def pathFind(self, start: tuple, end: tuple) -> Path:
        path: Path = Path()
        path.cells[0] = start
        path.currentCell = self.getCell(int(start[0]), int(start[1]))
        hasFoundPath = False

        # find a path. Logic: take the starting square. pick a random path going in the direction of the end, continue until a dead end or the end is found. When dead end found, delete path back until the last fork and take another option.
        iteration = 0
        while not hasFoundPath:
            iteration += 1
            # time.sleep(1)
            if iteration > 200:
                print("No path found.")
                break
            print(str(path.cells))
            currentCell = path.cells[len(path.cells) - 1]
            desiredDirection1 = 0  # --> the first direction we want to go. Will always be vertical, unless at the same y coord as the target.
            desiredDirection2 = 1  # --> 2nd priority. For example, if going up and right, will be right(1).

            if path.cells[len(path.cells) - 1] in path.cells[:len(path.cells) - 1]:
                _path = path.cull(path)
                continue
            if int(end[1]) < int(currentCell[0]):
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
                if int(end[0]) > int(currentCell[1]):
                    desiredDirection1 = 1
                else:
                    if int(end[0]) == int(currentCell[0]):
                        print("Pathfind complete.")
                        return path
                    else:
                        desiredDirection1 = 3
            options = self.getOptions(path)

            if desiredDirection1 in options and len(options) > 1:
                # the _path can go multiple ways (note: its 1 because we (^)screened for where we came from already.)
                path.append(desiredDirection1, True)
                continue
            elif len(options) == 1:
                # we can only go one way. Doesn't matter whether it's desired or not, we be going in that direction.
                path.append(options[0], False)
                continue
            elif len(options) > 1:
                # we can't go straight there, and we have multiple options. Pick a different direction and go along the _path(2nd priority if possible).
                if desiredDirection2 in options:
                    path.append(desiredDirection2, True)
                    continue
                else:
                    # this is my way of choosing a random leftover option. Neither desired path is available, so just go somewhere.
                    path.append(options[0], True)
                    continue
            else:
                # no options. time to delete the _path until the last junction, then start again from there.
                path = path.cull(path)
                continue

        return path


def printMaze():
    for y in range(len(maze.cells)):
        _row = ""
        for x in range(len(maze.cells[0])):
            cell = maze.getCell(x, y)
            _row = _row + " " + str(
                [cell.northWall, cell.eastWall, cell.southWall, cell.westWall])
        print(_row)


def correct(direction: int):
    motor.stop(RightMotor)
    motor.stop(LeftMotor)
    if direction % 900 > 450:
        # turn left
        motor.run_for_degrees(RightMotor, 40, 50)
    else:
        # turn right
        motor.run_for_degrees(LeftMotor, 40, -50)
    print(direction % 900)
    time.sleep(1)


# variables:
maze = Maze()
iteration = 0
turning = False
pastDirections = []
direction = setUpDirection(pastDirections)
location: tuple = (0, 0)


async def main():
    global iteration, task, maze
    time.sleep(0.5)
    direction = round(motion_sensor.tilt_angles()[0] / 10)
    facing = 0
    pitch = round(motion_sensor.tilt_angles()[1] / 10)

    # find and go to next cell
    if len(maze.cells) == 1 and len(maze.cells[0]) == 1:
        # starting maze, havent discovered anything yet
        process_square()
    undiscovereds = {}
    for row in range(len(maze.cells)):
        for col in range(len(maze.cells[row])):
            cell = maze.cells[row][col]
            if not cell.hasBeenFound:
                undiscovereds[cell] = len(maze.pathFind((location), (row, col)).instructions)
    currentTarget: tuple = ((0, 0), 200)
    for i in undiscovereds:
        if undiscovereds[i] < currentTarget[1]:
            currentTarget = (i, undiscovereds[i])
    pathToTarget =


while True:
    runloop.run(main())