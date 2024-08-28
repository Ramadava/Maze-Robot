from hub import port, motion_sensor, sound
import motor, distance_sensor, color_sensor, runloop, force_sensor, time, motor_pair, color

# to double-check:
RightMotor = port.A
LeftMotor = port.C
ColorSensor = port.B
DistanceSensor = port.D
ForceSensor = port.F
VictimSensor = port.E  # TODO: double check this is correct
motor_pair.pair(motor_pair.PAIR_1, LeftMotor, RightMotor)

# to fine tune:

regular_white_max_reflected = 99  # place on white tile, run fine-tuning, wait for a couple seconds, see the value, add two to it, and put it here
forceSensorThreshold = 457
distanceSensorTolerance = 10  # TODO: Set this as an actual value
pitchThreshold = 3  # TODO: fine tine this value. This is set to the max value the pitch gets to when the robot is flat.
normalCellColor = 10  # make this the _color of the floor


def setUpDirection(
        pastD: list) -> int:  # you can basically ignore this, but don't delete(used to average past directions for more reliable result)
    if len(pastD) == 0:
        return 0
    if len(pastD) > 5:
        pastD = pastD[(len(pastD) - 1):]
    forAVG = 0
    for i in pastD:
        forAVG += i
    return round(forAVG / len(pastD))


def angle_difference(direct, current):
    diff = current - direct
    if diff > 180:
        diff -= 360
    elif diff < -180:
        diff += 360
    return abs(diff)


def Turn(right: bool):
    global facing, turning, direction
    turning = True
    direct = direction  # Save the starting direction
    tempDir = 0

    # checkDist()

    if right:
        while tempDir < 90:
            motor_pair.move_for_degrees(motor_pair.PAIR_1, 5, 100, velocity=80)
            direction = angle()
            tempDir = angle_difference(direct, direction)
        facing = (facing + 1) % 4  # TODO: double check this is right. Rotate right updates the facing direction
    else:
        while tempDir < 90:
            motor_pair.move_for_degrees(motor_pair.PAIR_1, 5, 100, velocity=-80)
            direction = angle()
            tempDir = angle_difference(direct, direction)
        facing = (facing - 1) % 4  # TODO: double check this is right. Rotate left updates the facing direction
        if facing < 0:
            facing = 3

    turning = False
    # checkDist()


def forward():  # fun maths to make it go a desired distance from just the acceleration known TODO: check it works
    global maze, location
    motor.stop(LeftMotor, stop=motor.BRAKE)
    motor.stop(RightMotor, stop=motor.BRAKE)
    # correct(facing)
    for i in range(60):
        _color = color_sensor.color(ColorSensor)
        motor.run_for_degrees(RightMotor, 20,
                              100)  # TODO: make sure this goes forwards, not backwards. (and works as intended)
        motor.run_for_degrees(LeftMotor, 20, -100)
        if force_sensor.raw(ForceSensor) > forceSensorThreshold:  # TODO: make it differentiate obstacles and walls
            print("wall encountered")
            motor.run_for_degrees(RightMotor, (i - 1) * 20, -100)
            motor.run_for_degrees(LeftMotor, (i - 1) * 20, 100)
            cell = maze.getCell(location[0], location[1])
            if facing == 0:  # TODO: make sure this works (sets wall of the cells its tried to run into)
                upCell = maze.getCell(location[0], location[1] - 1)
                maze.setCell(location[0], location[1], cell._color, 2, cell.southWall, cell.eastWall, cell.westWall,
                             cell.hasBeenFound)
                maze.setCell(location[0], location[1] - 1, upCell._color, upCell.northWall, 2, upCell.eastWall,
                             upCell.westWall, upCell.hasBeenFound)
            if facing == 1:
                upCell = maze.getCell(location[0] + 1, location[1])
                maze.setCell(location[0], location[1], cell._color, cell.northWall, cell.southWall, 2, cell.westWall,
                             cell.hasBeenFound)
                maze.setCell(location[0], location[1] - 1, upCell._color, upCell.northWall, cell.southWall,
                             upCell.eastWall, 2, upCell.hasBeenFound)
            if facing == 2:
                upCell = maze.getCell(location[0], location[1] + 1)
                maze.setCell(location[0], location[1], cell._color, cell.northWall, 2, cell.eastWall, cell.westWall,
                             cell.hasBeenFound)
                maze.setCell(location[0], location[1] - 1, upCell._color, 2, cell.southWall, upCell.eastWall,
                             upCell.westWall, upCell.hasBeenFound)
            if facing == 3:
                upCell = maze.getCell(location[0] - 1, location[1])
                maze.setCell(location[0], location[1], cell._color, cell.northWall, cell.southWall, cell.eastWall, 2,
                             cell.hasBeenFound)
                maze.setCell(location[0], location[1] - 1, upCell._color, upCell.northWall, 2, upCell.eastWall,
                             upCell.westWall, upCell.hasBeenFound)
            return
        if _color == 0:
            print("black cell encountered")
            motor.run_for_degrees(RightMotor, (i - 1) * 20, -100)  # TODO: make sure this goes backwards, not forwards
            motor.run_for_degrees(LeftMotor, (i - 1) * 20, 100)
            if facing == 0:
                cell = maze.getCell(location[0], location[1] - 1)
                maze.setCell(location[0], location[1] - 1, 0, cell.northWall, cell.southWall, cell.eastWall,
                             cell.westWall, True)
            if facing == 1:
                cell = maze.getCell(location[0] + 1, location[1])
                maze.setCell(location[0] + 1, location[1], 0, cell.northWall, cell.southWall, cell.eastWall,
                             cell.westWall, True)
            if facing == 2:
                cell = maze.getCell(location[0], location[1] + 1)
                maze.setCell(location[0], location[1] + 1, 0, cell.northWall, cell.southWall, cell.eastWall,
                             cell.westWall, True)
            if facing == 3:
                cell = maze.getCell(location[0] - 1, location[1])
                maze.setCell(location[0] - 1, location[1], 0, cell.northWall, cell.southWall, cell.eastWall,
                             cell.westWall, True)
            return
    if facing == 0:
        location = (location[0], location[1] - 1)
    elif facing == 1:
        location = (location[0] + 1, location[1])
    elif facing == 2:
        location = (location[0], location[1] + 1)
    else:
        location = (location[0] - 1, location[1])
    return


def angle() -> float:
    angles = motion_sensor.tilt_angles()
    yaw = angles[0]
    return round(yaw / 10)


def process_square():  # TODO: make it look for _colored victims as it does this
    global maze, location, facing, turning, direction
    __color = color_sensor.color(ColorSensor)
    _reflection = color_sensor.reflection(ColorSensor)

    cell = maze.getCell(location[0], location[1])
    if cell.hasBeenFound:
        print("cell already processed")
        return  # confirming we haven't already looked at this cell
    cell.hasBeenFound = True

    # Check the _color of the square
    if __color == 10:
        if _reflection > regular_white_max_reflected:
            # silver
            print("cell is silver")
            cell._color = 2
        else:
            # white
            print("cell is white")
            cell._color = 0
    elif __color == 0:
        # black
        print("cell is black")
        cell._color = 1  # NOTE: not really sure why we need this, we will never be processing a black square, hopefully.
    maze.setCell(location[0], location[1], cell._color, cell.northWall, cell.southWall, cell.eastWall, cell.westWall,
                 cell.hasBeenFound)
    # looking now at the walls
    walls = [cell.northWall, cell.eastWall, cell.southWall, cell.westWall]
    for i in range(len(walls)):
        if walls[i] == 2:
            print("know this wall already")
            continue  # don't need to recheck if we already know for certain
        else:
            if facing == i:  # we are facing in the direction of the wall
                print("facing wall already.")
                checkWall()
            else:
                if facing == 3 and i == 0:
                    print("wall to the 0, we facing 3")
                    Turn(True)
                    checkWall()
                elif facing == 0 and i == 3:
                    print("wall to the 3, we facing 0")
                    Turn(False)
                    checkWall()
                elif facing > i:
                    print("turn to left")
                    while facing > i:
                        Turn(False)
                        checkWall()
                else:
                    print("turn to right")
                    while facing < i:
                        print("turning right nwo")
                        Turn(True)
                        checkWall()
        print("facing: " + str(facing))


class Cell:
    _color = 0
    northWall = 0  # 0 = no wall, 1 = probably wall (from distance sensor), 2 = wall
    southWall = 0
    eastWall = 0
    westWall = 0
    hasBeenFound = False

    def __init__(self, _color: int, walls: list[int], hasBeenFound: bool):
        self._color = _color
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
    start = Cell.default()
    instructions = []
    cells = []
    currentCell = Cell.default()

    def append(self, _direction: int, junction: bool):
        if junction:
            self.instructions.append("X" + str(_direction))
        else:
            self.instructions.append(str(_direction))
        if _direction == 0:
            self.cells.append((int(self.cells[self.length][0]), int(self.cells[self.length][1]) - 1))
        if _direction == 1:
            self.cells.append((int(self.cells[self.length][0]) + 1, int(self.cells[self.length][1])))
        if _direction == 2:
            self.cells.append((int(self.cells[self.length][0]), int(self.cells[self.length][1]) + 1))
        if _direction == 3:
            self.cells.append((int(self.cells[self.length][0]) - 1, int(self.cells[self.length][1])))
        self.length += 1
        self.currentCell = maze.getCell(self.cells[self.length][0], self.cells[self.length][1])

    def cull(self):
        for _i in range(len(self.instructions)):
            v = len(self.instructions) - _i - 1
            if self.instructions[v][0] == "X":
                # we found him
                lastInstructions = list(self.instructions[v][1:])
                self.length = v  # ±1?
                self.instructions = self.instructions[:v]
                self.cells = self.cells[:v + 1]
                self.currentCell = maze.getCell(int(self.cells[len(self.cells) - 1][0]),
                                                int(self.cells[len(self.cells) - 1][1]))

                options = maze.getOptions(self)
                for h in lastInstructions:
                    if int(h) in options:
                        options.remove(int(h))
                self.append(options[0], len(options) > 1)
                break

    def cut(self):
        self.length -= 1
        self.cells = self.cells[1:]
        self.instructions = self.instructions[1:]
        self.currentCell = maze.getCell(location[0], location[1])

    def updateCells(self, _direction):
        for i in range(len(self.cells)):
            if _direction == 0:
                self.cells[i] = self.cells[i][0], self.cells[i][1] + 1
            elif _direction == 3:
                self.cells[i] = self.cells[i][0] + 1, self.cells[i][1]


class Maze:
    cells = [[Cell(0, [0, 0, 0, 0], False)]]
    # Note: x is horizontal value, starting at 0 from left, y is vertical value, starting from 0 at top.

    width: int = 1
    height: int = 1

    def expand(self, _direction: int):  # TODO: check that
        global start, location
        if _direction == 0:
            newRow = []
            for o in range(self.width):
                newRow.append(Cell.default())
            tempCells = self.cells
            self.cells = []
            self.cells.append(newRow)
            for o in range(self.height):
                self.cells.append(tempCells[o])
            self.height += 1
            start = (start[0], start[1] + 1)
            location = (location[0], location[1] + 1)
        elif _direction == 1:
            for o in range(self.height):
                self.cells[o].append(Cell.default())
            self.width += 1
        elif _direction == 2:
            newRow = []
            for o in range(self.width):
                newRow.append(Cell.default())
            self.cells.append(newRow)
            self.height += 1
        elif _direction == 3:
            for o in range(self.height):
                tempRow = self.cells[o]
                self.cells[o] = []
                self.cells[o].append(Cell.default())
                for v in range(len(tempRow)):
                    self.cells[o].append(tempRow[v])
            self.width += 1
            start = (start[0] + 1, start[1])
            location = (location[0] + 1, location[1])

    def getCell(self, _x: int, _y: int) -> Cell:
        # print("getting cell. y val: " + str(_y) + ". x val: " + str(_x))
        return self.cells[_y][_x]  # TODO: error here

    def setCell(self, _x, _y, _color: int, northWall: int, southWall: int, eastWall: int, westWall: int,
                hasBeenFound: bool):
        self.cells[_y][_x] = Cell(_color, [northWall, southWall, eastWall, westWall], hasBeenFound)

    def getSize(self):
        return self.width, self.height

    @staticmethod
    def getOptions(__path: Path) -> list:
        _options = []
        location = __path.cells[len(__path.cells) - 1]
        if __path.currentCell.northWall == 0 and not (__path.cells[len(__path.cells) - 1][0],
                                                      int(__path.cells[len(__path.cells) - 1][1]) - 1) in __path.cells[
                                                                                                          :len(__path.cells) - 1]:
            if len(__path.instructions) > 0 and __path.instructions[len(__path.instructions) - 1] != "2" and \
                    __path.instructions[len(__path.instructions) - 1] != "X2":
                if location[1] > 0 and maze.getCell(__path.cells[len(__path.cells) - 1][0],
                                                    __path.cells[len(__path.cells) - 1][1] - 1)._color != 1:
                    _options.append(0)
            elif len(__path.instructions) == 0:
                if location[1] > 0 and maze.getCell(__path.cells[len(__path.cells) - 1][0],
                                                    __path.cells[len(__path.cells) - 1][1] - 1)._color != 1:
                    _options.append(0)
        if __path.currentCell.southWall == 0 and not (__path.cells[len(__path.cells) - 1][0],
                                                      int(__path.cells[len(__path.cells) - 1][1]) + 1) in __path.cells[
                                                                                                          :len(__path.cells) - 1]:
            if len(__path.instructions) > 0 and __path.instructions[len(__path.instructions) - 1] != "0" and \
                    __path.instructions[len(__path.instructions) - 1] != "X0":
                if location[1] < maze.height - 1 and maze.getCell(__path.cells[len(__path.cells) - 1][0],
                                                                  __path.cells[len(__path.cells) - 1][
                                                                      1] + 1)._color != 1:
                    _options.append(2)
            elif len(__path.instructions) == 0:
                if location[1] < maze.height - 1 and maze.getCell(__path.cells[len(__path.cells) - 1][0],
                                                                  __path.cells[len(__path.cells) - 1][
                                                                      1] + 1)._color != 1:
                    _options.append(2)
        if __path.currentCell.eastWall == 0 and not (int(__path.cells[len(__path.cells) - 1][0]) + 1,
                                                     __path.cells[len(__path.cells) - 1][1]) in __path.cells[
                                                                                                :len(__path.cells) - 1]:
            if len(__path.instructions) > 0 and __path.instructions[len(__path.instructions) - 1] != "3" and \
                    __path.instructions[len(__path.instructions) - 1] != "X3":
                if location[0] < maze.width - 1 and maze.getCell(__path.cells[len(__path.cells) - 1][0] + 1,
                                                                 __path.cells[len(__path.cells) - 1][1])._color != 1:
                    _options.append(1)
            elif len(__path.instructions) == 0:
                if location[0] < maze.width - 1 and maze.getCell(__path.cells[len(__path.cells) - 1][0] + 1,
                                                                 __path.cells[len(__path.cells) - 1][1])._color != 1:
                    _options.append(1)
        if __path.currentCell.westWall == 0 and not (int(__path.cells[len(__path.cells) - 1][0]) - 1,
                                                     __path.cells[len(__path.cells) - 1][1]) in __path.cells[
                                                                                                :len(__path.cells) - 1]:
            if len(__path.instructions) > 0 and __path.instructions[len(__path.instructions) - 1] != "1" and \
                    __path.instructions[len(__path.instructions) - 1] != "X1":
                coords = (__path.cells[len(__path.cells) - 1][0] - 1, __path.cells[len(__path.cells) - 1][1])
                if location[0] > 0 and maze.getCell(__path.cells[len(__path.cells) - 1][0] - 1,
                                                    __path.cells[len(__path.cells) - 1][1])._color != 1:
                    _options.append(3)
            elif len(__path.instructions) == 0:
                if location[0] > 0 and maze.getCell(__path.cells[len(__path.cells) - 1][0] - 1,
                                                    __path.cells[len(__path.cells) - 1][1])._color != 1:
                    _options.append(3)
        return _options

    def pathFind(self, _start: tuple, end: tuple) -> Path:
        path: Path = Path()
        path.cells = [_start]
        path.currentCell = self.getCell(int(_start[0]), int(_start[1]))
        hasFoundPath = False
        path.instructions = []
        # find a path. Logic: take the starting square. pick a random path going in the direction of the end, continue until a dead end or the end is found. When dead end found, delete path back until the last fork and take another option.
        iteration = 0
        print("starting pathfind. start: " + str(_start) + ". end: " + str(end))
        while not hasFoundPath:
            iteration += 1
            # time.sleep(1)
            if iteration > 200:
                print("No path found.")
                break
            # print(str(path.cells))
            desiredDirection1 = 0  # --> the first direction we want to go. Will always be vertical, unless at the same y coord as the target.
            desiredDirection2 = 1  # --> 2nd priority. For example, if going up and right, will be right(1).

            currentLoc = (path.cells[len(path.cells) - 1][0], path.cells[len(path.cells) - 1][1])
            if path.cells[len(path.cells) - 1] in path.cells[:len(path.cells) - 1]:
                path.cull()
                continue
            if currentLoc[1] > int(end[1]):
                # thing is above.
                if int(end[0]) > currentLoc[0]:
                    pass
                else:
                    desiredDirection2 = 3
            elif currentLoc[1] < int(end[1]):
                # thing is below.
                desiredDirection1 = 2
                if int(end[0]) > currentLoc[0]:
                    pass
                else:
                    desiredDirection2 = 3
            else:
                if int(end[0]) > currentLoc[0]:
                    desiredDirection1 = 1
                else:
                    if int(end[0]) == currentLoc[0] and int(end[1]) == currentLoc[1]:
                        print("Pathfind complete. Path: " + str(path.instructions))
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
                path.cull()
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


def correct(_direction: int):
    motor.stop(RightMotor)
    motor.stop(LeftMotor)
    direction = angle()
    if facing == 0:
        if direction < 0:
            # turn left
            while direction < 0:
                motor_pair.move_for_degrees(motor_pair.PAIR_1, 10, -100, velocity=100)
                direction = angle()
        if direction > 0:
            # turn left
            while direction > 0:
                motor_pair.move_for_degrees(motor_pair.PAIR_1, 10, 100, velocity=100)
                direction = angle()
    elif facing == 1:
        if direction < -90 or direction > 90:
            # turn left
            while direction < -90 or direction > 90:
                motor_pair.move_for_degrees(motor_pair.PAIR_1, 10, -100, velocity=100)
                direction = angle()
        if direction > -90 and direction < 90:
            # turn left
            while direction > -90 and direction < 90:
                motor_pair.move_for_degrees(motor_pair.PAIR_1, 10, 100, velocity=100)
                direction = angle()
    elif facing == 2:
        if direction < 0:
            # turn left
            while direction < 0:
                motor_pair.move_for_degrees(motor_pair.PAIR_1, 10, 100, velocity=100)
                direction = angle()
        if direction > 0:
            # turn left
            while direction < 0:
                motor_pair.move_for_degrees(motor_pair.PAIR_1, 10, -100, velocity=100)
                direction = angle()

    print(_direction % 900)
    time.sleep(1)


def checkWall():
    def hi() -> bool:
        if force_sensor.raw(ForceSensor) > 457:
            cell = maze.getCell(location[0], location[1])
            _color = color_sensor.color(VictimSensor)
            if _color != 7 and _color != -1:
                # victim!!
                motor_pair.stop(motor_pair.PAIR_1)
                sound.beep(600)
                time.sleep(5)
            if facing == 0:
                maze.setCell(location[0], location[1], cell._color, 2, cell.southWall, cell.eastWall, cell.westWall,
                             cell.hasBeenFound)
                if location[1] > 0:
                    cell = maze.getCell(location[0], location[1] - 1)
                    maze.setCell(location[0], location[1] - 1, cell._color, cell.northWall, 1, cell.eastWall,
                                 cell.westWall, cell.hasBeenFound)
            if facing == 1:
                maze.setCell(location[0], location[1], cell._color, cell.northWall, cell.southWall, 2, cell.westWall,
                             cell.hasBeenFound)
                if maze.width > location[0] + 1:
                    cell = maze.getCell(location[0] + 1, location[1])
                    maze.setCell(location[0] + 1, location[1], cell._color, cell.northWall, cell.southWall, 1,
                                 cell.westWall, cell.hasBeenFound)
            if facing == 2:
                maze.setCell(location[0], location[1], cell._color, cell.northWall, 2, cell.eastWall, cell.westWall,
                             cell.hasBeenFound)
                if maze.height > location[1] + 1:
                    cell = maze.getCell(location[0], location[1] + 1)
                    maze.setCell(location[0], location[1] + 1, cell._color, 1, cell.southWall, cell.eastWall,
                                 cell.westWall, cell.hasBeenFound)
            if facing == 3:
                maze.setCell(location[0], location[1], cell._color, cell.northWall, cell.southWall, cell.eastWall, 2,
                             cell.hasBeenFound)
                if location[0] > 0:
                    cell = maze.getCell(location[0] - 1, location[1])
                    maze.setCell(location[0] - 1, location[1], cell._color, cell.northWall, cell.southWall, 1,
                                 cell.westWall, cell.hasBeenFound)
            return True
        return False

    iterations = 0
    while not hi():
        time.sleep(0.1)
        motor_pair.move_for_degrees(motor_pair.PAIR_1, 20, 0,
                                    velocity=100)  # TODO: check this works with force sensor in the middle
        iterations += 1
        if color_sensor.color(ColorSensor) == 0:
            print("black!!!")
            motor_pair.move_for_degrees(motor_pair.PAIR_1, 250, 0, velocity=-100)
            break
        if iterations > 10:
            for i in range(iterations):
                motor_pair.move_for_degrees(motor_pair.PAIR_1, 20, 0, velocity=-100)
            return

    if hi():
        motor_pair.move_for_degrees(motor_pair.PAIR_1, 200, 0, velocity=-100)
    time.sleep(2)
    return


def checkDist():
    global maze
    if turning or pitch > pitchThreshold:  # TODO: add to this as more things become relevant
        return
    dist = float(distance_sensor.distance(DistanceSensor) / 10) - 17  # TODO: adjust this value
    if dist != -1 and dist % 30 < distanceSensorTolerance:
        wallDist = round(dist / 30)
        if facing == 0:
            cords = (location[0], location[1] - wallDist)  # coordinates for use in the maze.getCell func
            heightVal = (maze.height - location[
                1]) + wallDist  # regular y value, starting at 1 (useful for comparisons with maze.height)
            if heightVal > maze.height:  # maze needs expansion to fit the seen distance.
                for i in range(heightVal - maze.height):
                    maze.expand(0)
            cell = maze.getCell(cords[0], cords[1])
            upCell = maze.getCell(cords[0], cords[1] - 1)
            if not cell.hasBeenFound:
                maze.setCell(cords[0], cords[1], cell._color, 1, cell.southWall, cell.eastWall, cell.westWall, False)
                if heightVal + 1 > maze.height:  # extra cell above, we can set the south wall of that one while we're at it
                    maze.setCell(cords[0], cords[1] - 1, upCell._color, upCell.northWall, 1, upCell.eastWall,
                                 upCell.westWall, False)
        if facing == 1:
            cords = (location[0] + wallDist, location[1])  # coordinates for use in the maze.getCell func
            widthVal = location[
                           0] + wallDist + 1  # regular x value, starting at 1 (useful for comparisons with maze.width)
            if widthVal > maze.width:  # maze needs expansion to fit the seen distance.
                for i in range(widthVal - maze.width):
                    maze.expand(1)
            cell = maze.getCell(cords[0], cords[1])
            rightCell = maze.getCell(cords[0] + 1, cords[1])
            if not cell.hasBeenFound:
                maze.setCell(cords[0], cords[1], cell._color, cell.northWall, cell.southWall, 1, cell.westWall, False)
                if widthVal + 1 <= maze.width:  # extra cell to the right, we can set the west wall of that one while we're at it
                    maze.setCell(cords[0], cords[1] - 1, rightCell._color, rightCell.northWall, rightCell.southWall,
                                 rightCell.eastWall, 1,
                                 False)
        if facing == 2:
            cords = (location[0], location[1] + wallDist)  # coordinates for use in the maze.getCell func
            heightVal = (maze.height - location[
                1]) - wallDist  # regular y value, starting at 1 (useful for comparisons with maze.height)
            if heightVal < 1:  # maze needs expansion to fit the seen distance.
                for i in range(-heightVal + 1):
                    maze.expand(2)
            cell = maze.getCell(cords[0], cords[1])
            downCell = maze.getCell(cords[0], cords[1] + 1)
            if not cell.hasBeenFound:
                maze.setCell(cords[0], cords[1], cell._color, cell.northWall, 1, cell.eastWall, cell.westWall, False)
                if heightVal - 1 >= 1:  # extra cell below, we can set the north wall of that one while we're at it
                    maze.setCell(cords[0], cords[1] + 1, downCell._color, 1, downCell.southWall, downCell.eastWall,
                                 downCell.westWall,
                                 False)
        if facing == 3:
            cords = (location[0] - wallDist, location[1])  # coordinates for use in the maze.getCell func
            widthVal = location[
                           0] - wallDist + 1  # regular x value, starting at 1 (useful for comparisons with maze.width)
            if widthVal < 1:  # maze needs expansion to fit the seen distance.
                for i in range(-widthVal + 1):
                    maze.expand(3)
            cell = maze.getCell(cords[0], cords[1])
            leftCell = maze.getCell(cords[0] - 1, cords[1])
            if not cell.hasBeenFound:
                maze.setCell(cords[0], cords[1], cell._color, cell.northWall, cell.southWall, cell.eastWall, 1, False)
                if widthVal - 1 >= 1:  # extra cell to the left, we can set the east wall of that one while we're at it
                    maze.setCell(cords[0], cords[1] - 1, leftCell._color, leftCell.northWall, leftCell.southWall, 1,
                                 leftCell.westWall,
                                 False)


# variables:
maze = Maze()
turning: bool = False
pastDirections = []
direction: float = setUpDirection(pastDirections)
facing: int = 0
location: tuple = (0, 0)
start: tuple = (0, 0)
pitch = motion_sensor.tilt_angles()[1] / 10  # TODO: make sure we are checking for ramps in some kind of while loop
startTime = time.time()


async def main():  # the main code loop
    global direction, facing, pitch
    print("main loop starting.")
    time.sleep(0.5)
    direction = angle()
    pitch = round(motion_sensor.tilt_angles()[1] / 10)
    # checkDist()

    # find and go to next cell
    process_square()
    printMaze()
    undiscovereds = {}
    for row in range(len(maze.cells)):
        for col in range(len(maze.cells[row])):
            cell = maze.cells[row][col]
            if not cell.hasBeenFound:
                undiscovereds[(col, row)] = len(maze.pathFind(location, (col, row)).instructions)
    currentTarget: tuple = ((0, 0), 200)
    print(undiscovereds)
    if len(undiscovereds) == 0:
        print("maze before: ")
        printMaze()
        # we know everything in the known maze. this means the whole maze is currently a rectangle(we can scan the edges) exclusively
        for i in range(maze.width):  # searching top row
            cell = maze.getCell(i, 0)
            if cell._color is not 1 and cell.northWall is not 2:
                print("loc: " + str(location) + ". end coords: " + str((i, 0)))
                maze.expand(0)
                undiscovereds[(0, i)] = len(maze.pathFind(location, (i, 0)).instructions)
                print("maze expanded upwards!")
                print("new location: " + str(location) + ". new start: " + str(start))
                break
        for i in range(maze.width):  # searching bottom row
            cell = maze.getCell(i, len(maze.cells) - 1)
            if cell._color is not 1 and cell.southWall is not 2:
                maze.expand(2)
                print("starting downwards check. maze: ")
                printMaze()
                undiscovereds[(i, maze.height - 1)] = len(maze.pathFind(location, (i, maze.height - 1)).instructions)
                print("maze expanded down!")
                print("new location: " + str(location) + ". new start: " + str(start))
                break
        for i in range(maze.height):  # searching left column (going down)
            cell = maze.getCell(0, i)
            if cell._color is not 1 and cell.westWall is not 2:
                maze.expand(3)
                print("starting leftwards check. maze: ")
                printMaze()
                undiscovereds[(0, i)] = len(maze.pathFind(location, (0, i)).instructions)
                print("maze expanded left!")
                print("new location: " + str(location) + ". new start: " + str(start))
                break
        for i in range(maze.height):  # searching right column (going down)
            cell = maze.getCell(maze.width - 1, i)
            if cell._color is not 1 and cell.eastWall is not 2:
                maze.expand(1)
                print("starting rightwards check. maze: ")
                printMaze()
                undiscovereds[(maze.width - 1, i)] = len(maze.pathFind(location, (maze.width - 1, i)).instructions)
                print("maze expanded right!")
                print("new location: " + str(location) + ". new start: " + str(start))
                break

    for i in undiscovereds:
        if undiscovereds[i] < currentTarget[1]:
            currentTarget = (i, undiscovereds[i])
    if currentTarget == ((0, 0), 200):  # all tiles have been discovered (with time to spare), go back to start
        __path = maze.pathFind(location, start)
        goBackToStartAndReport(__path)
        return

    pathToTarget = maze.pathFind(location, currentTarget[0])
    frstInst = pathToTarget.instructions[0]  # error here
    if frstInst[0] == "0" or (frstInst[0] == "X" and frstInst[1] == "0"):
        # go up
        undiscoveredWalls = []

        if maze.getCell(location[0], location[1]).northWall == 1 or maze.getCell(location[0],
                                                                                 location[1]).northWall == 0:
            undiscoveredWalls.append(0)
        if maze.getCell(location[0], location[1]).eastWall == 1 or maze.getCell(location[0], location[1]).eastWall == 0:
            undiscoveredWalls.append(1)
        if maze.getCell(location[0], location[1]).southWall == 1 or maze.getCell(location[0],
                                                                                 location[1]).southWall == 0:
            undiscoveredWalls.append(2)
        if maze.getCell(location[0], location[1]).westWall == 1 or maze.getCell(location[0], location[1]).westWall == 0:
            undiscoveredWalls.append(3)

        if facing == 1:
            Turn(False)
        elif facing == 2:
            if 1 in undiscoveredWalls:
                Turn(False)
                Turn(False)
            else:
                Turn(True)
                Turn(True)
        elif facing == 3:
            Turn(True)
    elif frstInst[0] == "1" or (frstInst[0] == "X" and frstInst[1] == "1"):
        # go right
        undiscoveredWalls = []

        if maze.getCell(location[0], location[1]).northWall == 1 or maze.getCell(location[0],
                                                                                 location[1]).northWall == 0:
            undiscoveredWalls.append(0)
        if maze.getCell(location[0], location[1]).eastWall == 1 or maze.getCell(location[0], location[1]).eastWall == 0:
            undiscoveredWalls.append(1)
        if maze.getCell(location[0], location[1]).southWall == 1 or maze.getCell(location[0],
                                                                                 location[1]).southWall == 0:
            undiscoveredWalls.append(2)
        if maze.getCell(location[0], location[1]).westWall == 1 or maze.getCell(location[0], location[1]).westWall == 0:
            undiscoveredWalls.append(3)

        if facing == 2:
            Turn(False)
        elif facing == 3:
            if 1 in undiscoveredWalls:
                Turn(False)
                Turn(False)
            else:
                Turn(True)
                Turn(True)
        elif facing == 0:
            Turn(True)
    elif frstInst[0] == "2" or (frstInst[0] == "X" and frstInst[1] == "2"):
        # go down
        undiscoveredWalls = []

        if maze.getCell(location[0], location[1]).northWall == 1 or maze.getCell(location[0],
                                                                                 location[1]).northWall == 0:
            undiscoveredWalls.append(0)
        if maze.getCell(location[0], location[1]).eastWall == 1 or maze.getCell(location[0], location[1]).eastWall == 0:
            undiscoveredWalls.append(1)
        if maze.getCell(location[0], location[1]).southWall == 1 or maze.getCell(location[0],
                                                                                 location[1]).southWall == 0:
            undiscoveredWalls.append(2)
        if maze.getCell(location[0], location[1]).westWall == 1 or maze.getCell(location[0], location[1]).westWall == 0:
            undiscoveredWalls.append(3)

        if facing == 3:
            Turn(False)
        elif facing == 0:
            if 1 in undiscoveredWalls:
                Turn(False)
                Turn(False)
            else:
                Turn(True)
                Turn(True)
        elif facing == 1:
            Turn(True)
    elif frstInst[0] == "3" or (frstInst[0] == "X" and frstInst[1] == "3"):
        # go left
        undiscoveredWalls = []

        if maze.getCell(location[0], location[1]).northWall == 1 or maze.getCell(location[0],
                                                                                 location[1]).northWall == 0:
            undiscoveredWalls.append(0)
        if maze.getCell(location[0], location[1]).eastWall == 1 or maze.getCell(location[0], location[1]).eastWall == 0:
            undiscoveredWalls.append(1)
        if maze.getCell(location[0], location[1]).southWall == 1 or maze.getCell(location[0],
                                                                                 location[1]).southWall == 0:
            undiscoveredWalls.append(2)
        if maze.getCell(location[0], location[1]).westWall == 1 or maze.getCell(location[0], location[1]).westWall == 0:
            undiscoveredWalls.append(3)

        if facing == 0:
            Turn(False)
        elif facing == 1:
            if 1 in undiscoveredWalls:
                Turn(False)
                checkWall()  # TODO: make sure it waits for this (should be fine)
                Turn(False)
            else:
                Turn(True)
                checkWall()
                Turn(True)
        elif facing == 2:
            Turn(True)

    forward()  # this marks the point where the robot physically enters a new cell
    print("WE MADE IT FORWARD!!!!")
    time.sleep(0.5)
    print()
    # checkDist()


def goBackToStartAndReport(_path: Path):  # TODO: check it works
    for i in _path.instructions:
        instruction = i[0]
        if instruction == 'X':
            instruction = i[1]

        if facing == 3 and i == 0:
            Turn(True)
        elif facing == 0 and i == 3:
            Turn(False)
        elif facing > i:
            while facing > i:
                Turn(False)
        else:
            while facing < i:
                Turn(True)
        forward()
    # we are now back the starting square, hopefully
    sound.beep(262, 300)
    sound.beep(330, 300)
    sound.beep(329, 300)
    sound.beep(523, 600)


maze.setCell(0, 0, 0, 0, 2, 2, 2, True)
while True:
    pathBackToStart = maze.pathFind(location, start)
    timeForInstruction = 3
    if time.time() - startTime > (
            240 - (timeForInstruction * len(pathBackToStart.instructions))):  # TODO: check it works
        goBackToStartAndReport(pathBackToStart)
        break
    else:
        pastDirections.append(direction)  # TODO: check this works properly
        runloop.run(main())
        print("location: " + str(location))
        print("maze: ")
        printMaze()