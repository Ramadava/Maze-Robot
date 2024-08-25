# noinspection PyUnresolvedReferences
from hub import port, motion_sensor, button
# noinspection PyUnresolvedReferences
import motor, distance_sensor, color_sensor, runloop, force_sensor, time

# to double-check:
RightMotor = port.A
LeftMotor = port.C
ColorSensor = port.B
DistanceSensor = port.D
ForceSensor = port.F
VictimSensor = port.E  # TODO: double check this is correct

# to fine tune:

regular_white_max_reflected = 99  # place on white tile, run fine-tuning, wait for a couple seconds, see the value, add two to it, and put it here
forceSensorThreshold = 5  # TODO: Should be fine as is WAIT NO DOUBLE CHECK IT RAMEY PLEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAASE
distanceSensorTolerance = 10  # TODO: Set this as an actual value
pitchThreshold = 3  # TODO: fine tine this value. This is set to the max value the pitch gets to when the robot is flat.
normalCellColor = "white"  # make this the color of the floor


def setUpDirection(
        pastD: list) -> int:  # you can basically ignore this, but don't delete(used to average past directions for more reliable result)
    if len(pastD) == 0:
        return 0
    if len(pastD) > 5:
        pastD = pastD[(len(pastD) - 1):]
    forAVG = 0
    for i in pastD:
        forAVG += i
        print(round(forAVG / len(pastD)))
    return round(forAVG / len(pastD))


def Turn(right: bool):  # TODO: check this turns correctly, updates facing variable
    global facing, turning, direction
    turning = True
    direct = direction
    tempDir = 0
    checkDist()
    if right:
        while tempDir < 90:
            motor.run_for_time(LeftMotor, 5, -80)
            motor.run_for_time(RightMotor, 5, -80)
            tempDir = direction - direct + 5  # TODO: this may be wrong, double check NOTE: tempDir is the angle we've covered, direction is the direction we are facing, direct is the direction we started at
            direction = angle()
        if facing == 3:  # TODO: make sure this works right
            facing = 0
        else:
            facing += 1
    else:
        while tempDir > -90:
            motor.run_for_time(LeftMotor, 5, 80)
            motor.run_for_time(RightMotor, 5, 80)
            tempDir = direct - direction + 5  # this may be wrong
        if facing == 0:
            facing = 3
        else:
            facing -= 1
    turning = False
    checkDist()


def forward():  # fun maths to make it go a desired distance from just the acceleration known TODO: check it works
    global maze, location
    startTime = time.time()
    acceleration = motion_sensor.acceleration(False)[
        0]  # TODO: double check im getting the right one, also parameter might be wrong
    displacement = 0
    motor.stop(LeftMotor, stop=motor.BRAKE)  # TODO: make sure this works as expected
    motor.stop(RightMotor, stop=motor.BRAKE)
    velocity = 0
    degrees = 0
    while displacement < 29:
        color = color_sensor.color(ColorSensor)
        motor.run_for_degrees(RightMotor, 1,
                              100)  # TODO: make sure this goes forwards, not backwards. (and works as intended)
        motor.run_for_degrees(LeftMotor, 1, -100)
        velocity += (time.time() - startTime) * (acceleration * 1000 / 9.81)  # TODO: check this formula works properly
        displacement += velocity * (time.time() - startTime)
        degrees += 1
        if force_sensor.force(ForceSensor) > forceSensorThreshold:  # TODO: make this also check for black squares
            print("wall encountered")
            motor.run_for_degrees(RightMotor, degrees, -100)  # TODO: make sure this goes backwards, not forwards
            motor.run_for_degrees(LeftMotor, degrees, 100)
            cell = maze.getCell(location[0], location[1])
            if facing == 0:  # TODO: make sure this works (sets wall of the cells its tried to run into)
                upCell = maze.getCell(location[0], location[1] - 1)
                maze.setCell(location[0], location[1], cell.color, 2, cell.southWall, cell.eastWall, cell.westWall,
                             cell.hasBeenFound)
                maze.setCell(location[0], location[1] - 1, upCell.color, upCell.northWall, 2, upCell.eastWall,
                             upCell.westWall, upCell.hasBeenFound)
            if facing == 1:
                upCell = maze.getCell(location[0] + 1, location[1])
                maze.setCell(location[0], location[1], cell.color, cell.northWall, cell.southWall, 2, cell.westWall,
                             cell.hasBeenFound)
                maze.setCell(location[0], location[1] - 1, upCell.color, upCell.northWall, cell.southWall,
                             upCell.eastWall, 2, upCell.hasBeenFound)
            if facing == 2:
                upCell = maze.getCell(location[0], location[1] + 1)
                maze.setCell(location[0], location[1], cell.color, cell.northWall, 2, cell.eastWall, cell.westWall,
                             cell.hasBeenFound)
                maze.setCell(location[0], location[1] - 1, upCell.color, 2, cell.southWall, upCell.eastWall,
                             upCell.westWall, upCell.hasBeenFound)
            if facing == 3:
                upCell = maze.getCell(location[0] - 1, location[1])
                maze.setCell(location[0], location[1], cell.color, cell.northWall, cell.southWall, cell.eastWall, 2,
                             cell.hasBeenFound)
                maze.setCell(location[0], location[1] - 1, upCell.color, upCell.northWall, 2, upCell.eastWall,
                             upCell.westWall, upCell.hasBeenFound)
            return
        if color == 0:
            print("black cell encountered")
            motor.run_for_degrees(RightMotor, degrees, -100)  # TODO: make sure this goes backwards, not forwards
            motor.run_for_degrees(LeftMotor, degrees, 100)
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
    return yaw * 10
    # TODO: check that this actually works


def process_square():
    global maze, location, facing, turning
    _color = color_sensor.color(ColorSensor)
    _reflection = color_sensor.reflection(ColorSensor)

    cell = maze.getCell(location[0], location[1])
    if cell.hasBeenFound:
        return  # confirming we haven't already looked at this cell
    cell.hasBeenFound = True

    # Check the color of the square
    if _color == 10:
        if _reflection > regular_white_max_reflected:
            # silver
            cell.color = 2
        else:
            # white
            cell.color = 0
    elif _color == 0:
        # black
        cell.color = 1  # NOTE: not really sure why we need this, we will never be processing a black square, hopefully

    # look at walls
    walls = [cell.northWall, cell.eastWall, cell.southWall, cell.westWall]
    for i in range(len(walls)):
        if walls[i] == 2:
            continue
        else:
            if facing == i:
                checkWall()
            else:
                if facing == 3 and i == 0:
                    Turn(True)
                    checkWall()
                    continue
                elif facing == 0 and i == 3:
                    Turn(False)
                    checkWall()


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


class Maze:
    cells = [[Cell(0, [0, 0, 0, 0], True)]]
    # Note: x is horizontal value, starting at 0 from left, y is vertical value, starting from 0 at top.

    width: int = 1
    height: int = 1

    def expand(self, _direction: int):
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
                                                                                                          :len(
                                                                                                              __path.cells) - 1]:
            if len(__path.instructions) > 0 and __path.instructions[len(__path.instructions) - 1] != "2" and \
                    __path.instructions[len(__path.instructions) - 1] != "X2":
                if location[1] > 0 and maze.getCell(__path.cells[len(__path.cells) - 1][0],
                                                    __path.cells[len(__path.cells) - 1][1] - 1).color != 1:
                    _options.append(0)
                elif not location[1] > 0:
                    maze.expand(0)
                    _options.append(0)
            elif len(__path.instructions) == 0:
                if location[1] > 0 and maze.getCell(__path.cells[len(__path.cells) - 1][0],
                                                    __path.cells[len(__path.cells) - 1][1] - 1).color != 1:
                    _options.append(0)
                elif not location[1] > 0:
                    maze.expand(0)
                    _options.append(0)
        if __path.currentCell.southWall == 0 and not (__path.cells[len(__path.cells) - 1][0],
                                                      int(__path.cells[len(__path.cells) - 1][1]) + 1) in __path.cells[
                                                                                                          :len(
                                                                                                              __path.cells) - 1]:
            if len(__path.instructions) > 0 and __path.instructions[len(__path.instructions) - 1] != "0" and \
                    __path.instructions[len(__path.instructions) - 1] != "X0":
                if location[1] < maze.height - 1 and maze.getCell(__path.cells[len(__path.cells) - 1][0],
                                                                  __path.cells[len(__path.cells) - 1][
                                                                      1] + 1).color != 1:
                    _options.append(2)
                elif not location[1] < maze.height - 1:
                    maze.expand(2)
                    _options.append(2)
            elif len(__path.instructions) == 0:
                if location[1] < maze.height - 1 and maze.getCell(__path.cells[len(__path.cells) - 1][0],
                                                                  __path.cells[len(__path.cells) - 1][
                                                                      1] + 1).color != 1:
                    _options.append(2)
                elif not location[1] < maze.height - 1:
                    maze.expand(2)
                    _options.append(2)
        if __path.currentCell.eastWall == 0 and not (int(__path.cells[len(__path.cells) - 1][0]) + 1,
                                                     __path.cells[len(__path.cells) - 1][1]) in __path.cells[
                                                                                                :len(__path.cells) - 1]:
            if len(__path.instructions) > 0 and __path.instructions[len(__path.instructions) - 1] != "3" and \
                    __path.instructions[len(__path.instructions) - 1] != "X3":
                if location[0] < maze.width - 1 and maze.getCell(__path.cells[len(__path.cells) - 1][0] + 1,
                                                                 __path.cells[len(__path.cells) - 1][1]).color != 1:
                    _options.append(1)
                elif not location[0] < maze.width - 1:
                    maze.expand(1)
                    _options.append(1)
            elif len(__path.instructions) == 0:
                if location[0] < maze.width - 1 and maze.getCell(__path.cells[len(__path.cells) - 1][0] + 1,
                                                                 __path.cells[len(__path.cells) - 1][1]).color != 1:
                    _options.append(1)
                elif not location[0] < maze.width - 1:
                    maze.expand(1)
                    _options.append(1)
        if __path.currentCell.westWall == 0 and not (int(__path.cells[len(__path.cells) - 1][0]) - 1,
                                                     __path.cells[len(__path.cells) - 1][1]) in __path.cells[
                                                                                                :len(__path.cells) - 1]:
            if len(__path.instructions) > 0 and __path.instructions[len(__path.instructions) - 1] != "1" and \
                    __path.instructions[len(__path.instructions) - 1] != "X1":
                if location[0] > 0 and maze.getCell(__path.cells[len(__path.cells) - 1][0] - 1,
                                                    __path.cells[len(__path.cells) - 1][1]).color != 1:
                    _options.append(3)
                elif not location[0] > 0:
                    maze.expand(3)
                    _options.append(3)
            elif len(__path.instructions) == 0:
                if location[0] > 0 and maze.getCell(__path.cells[len(__path.cells) - 1][0] - 1,
                                                    __path.cells[len(__path.cells) - 1][1]).color != 1:
                    _options.append(3)
                elif not location[0] > 0:
                    maze.expand(3)
                    _options.append(3)

        return _options

    def pathFind(self, start: tuple, end: tuple) -> Path:
        path: Path = Path()
        path.cells.append(start)
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
            desiredDirection1 = 0  # --> the first direction we want to go. Will always be vertical, unless at the same y coord as the target.
            desiredDirection2 = 1  # --> 2nd priority. For example, if going up and right, will be right(1).

            currentLoc = (path.cells[len(path.cells) - 1][0], path.cells[len(path.cells) - 1][1])
            if path.cells[len(path.cells) - 1] in path.cells[:len(path.cells) - 1]:
                path.cull()
                continue
            if int(end[1]) < currentLoc[0]:
                # thing is above.
                if int(end[0]) > currentLoc[0]:
                    pass
                else:
                    desiredDirection2 = 3
            elif int(end[1]) > currentLoc[1]:
                # thing is below.
                desiredDirection1 = 2
                if int(end[0]) > currentLoc[0]:
                    pass
                else:
                    desiredDirection2 = 3
            else:
                if int(end[0]) > currentLoc[1]:
                    desiredDirection1 = 1
                else:
                    if int(end[0]) == currentLoc[0]:
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
    if _direction % 900 > 450:
        # turn left
        motor.run_for_degrees(RightMotor, 40, 50)
    else:
        # turn right
        motor.run_for_degrees(LeftMotor, 40, -50)
    print(_direction % 900)
    time.sleep(1)


def checkWall():
    def hi() -> bool:
        if force_sensor.force(ForceSensor) > (forceSensorThreshold * 10):
            return True

        return False

    iterations = 0
    while not hi():
        time.sleep(0.1)
        motor.run_for_degrees(LeftMotor, 100, -20)  # TODO: check this goes forward
        motor.run_for_degrees(RightMotor, 100, 20)
        iterations += 1
    for i in range(iterations):
        motor.run_for_degrees(LeftMotor, 100, 20)  # TODO: check this goes backward
        motor.run_for_degrees(RightMotor, 100, -20)
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
                maze.setCell(cords[0], cords[1], cell.color, 1, cell.southWall, cell.eastWall, cell.westWall, False)
                if heightVal + 1 > maze.height:  # extra cell above, we can set the south wall of that one while we're at it
                    maze.setCell(cords[0], cords[1] - 1, upCell.color, upCell.northWall, 1, upCell.eastWall,
                                 upCell.westWall,
                                 False)
        if facing == 1:
            cords = (location[0] + wallDist, location[1])  # coordinates for use in the maze.getCell func
            widthVal = location[0] + wallDist + 1  # regular x value, starting at 1 (useful for comparisons with maze.width)
            if widthVal > maze.width:  # maze needs expansion to fit the seen distance.
                for i in range(widthVal - maze.width):
                    maze.expand(1)
            cell = maze.getCell(cords[0], cords[1])
            rightCell = maze.getCell(cords[0] + 1, cords[1])
            if not cell.hasBeenFound:
                maze.setCell(cords[0], cords[1], cell.color, cell.northWall, cell.southWall, 1, cell.westWall, False)
                if widthVal + 1 <= maze.width:  # extra cell to the right, we can set the west wall of that one while we're at it
                    maze.setCell(cords[0], cords[1] - 1, rightCell.color, rightCell.northWall, rightCell.southWall,
                                 rightCell.eastWall, 1,
                                 False)
        if facing == 2:
            cords = (location[0], location[1] + wallDist)  # coordinates for use in the maze.getCell func
            heightVal = (maze.height - location[1]) - wallDist  # regular y value, starting at 1 (useful for comparisons with maze.height)
            if heightVal < 1:  # maze needs expansion to fit the seen distance.
                for i in range(-heightVal + 1):
                    maze.expand(2)
            cell = maze.getCell(cords[0], cords[1])
            downCell = maze.getCell(cords[0], cords[1] + 1)
            if not cell.hasBeenFound:
                maze.setCell(cords[0], cords[1], cell.color, cell.northWall, 1, cell.eastWall, cell.westWall, False)
                if heightVal - 1 >= 1:  # extra cell below, we can set the north wall of that one while we're at it
                    maze.setCell(cords[0], cords[1] + 1, downCell.color, 1, downCell.southWall, downCell.eastWall,
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
                maze.setCell(cords[0], cords[1], cell.color, cell.northWall, cell.southWall, cell.eastWall, 1, False)
                if widthVal - 1 >= 1:  # extra cell to the left, we can set the east wall of that one while we're at it
                    maze.setCell(cords[0], cords[1] - 1, leftCell.color, leftCell.northWall, leftCell.southWall, 1,
                                 leftCell.westWall,
                                 False)


# variables:
maze = Maze()
turning: bool = False
pastDirections = []
direction: float = setUpDirection(pastDirections)
facing: int = 0
location: tuple = (0, 0)
pitch = motion_sensor.tilt_angles()[1] / 10  # TODO: make sure we are checking for ramps in some kind of while loop


async def main():  # the main code loop
    global direction, facing, pitch
    time.sleep(0.5)
    direction = angle()
    facing = 0
    pitch = round(motion_sensor.tilt_angles()[1] / 10)
    checkDist()

    # find and go to next cell
    if len(maze.cells) == 1 and len(maze.cells[0]) == 1:
        # starting maze, haven't discovered anything yet
        process_square()
    undiscovereds = {}
    for row in range(len(maze.cells)):
        for col in range(len(maze.cells[row])):
            cell = maze.cells[row][col]
            if not cell.hasBeenFound:
                undiscovereds[cell] = len(maze.pathFind(location, (row, col)).instructions)
    currentTarget: tuple = ((0, 0), 200)
    for i in undiscovereds:
        if undiscovereds[i] < currentTarget[1]:
            currentTarget = (i, undiscovereds[i])
    pathToTarget = maze.pathFind(location, currentTarget)
    frstInst = pathToTarget.instructions[0]
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
            if undiscoveredWalls.__contains__(1):
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
            if undiscoveredWalls.__contains__(1):
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
            if undiscoveredWalls.__contains__(1):
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
            if undiscoveredWalls.__contains__(1):
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
    checkDist()
    pathToTarget.cut()


while True:
    runloop.run(main())