"""
Filename: battleship.py
Author Name: Jack Williams
Purpose: This program simulates a one-sided game of battleship. The board is
set up through an input file describing each ship's type and location; once
validated, the board is generated with this information. Guesses are made
through another input file, and the results of each move are output to the
user.
CSC 120 FA23 001
"""

import sys

class GridPos:
    """The GridPos class represents a single point on the battleship grid.
    
    The constructor accepts and x and y coordinates, as well as a Ship object
    representing the type of ship occupying the grid.
    
    The guessed attribute is a bool saying if this GridPos has been guessed or
    not; it is set to False by default, and can be set to True through the
    set_guessed() method."""

    def __init__(self, x, y, ship):
        self._x = int(x)
        self._y = int(y)
        self._ship_type = ship
        self._guessed = False
    
    def x(self):
        return self._x
    
    def y(self):
        return self._y
    
    def ship_type(self):
        return self._ship_type
    
    def guessed(self):
        return self._guessed
    
    def set_guessed(self):
        """Sets the guessed attribute to True.
        
        Parameters: None.
        
        Returns: None."""

        self._guessed = True
    
    def __str__(self):
        return f"{self._ship_type} {self._x} {self._y}"
    
    def __eq__(self, other):
        """Compares the x and y coordinates of two GridPos objects and returns
        True if they match.
        
        Parameters:
            other: A GridPos object to compare to.
        
        Returns: A bool matching if the two objects have the same coords."""
        return self._x == other.x() and self._y == other.y()

class Board:
    """The Board class represents a 10x10 battleship board. Each cell is a
    GridPos object.
    
    The constructor takes no arguments, and initializes both the empty board
    and an empty dict of Ship objects. (These are added through the
    add_validate_ship() method.)
    
    The process_guess() method takes a guess line from the guess file, and both
    alters the board and outputs accordingly to the results."""

    def __init__(self):
        self._board = self.gen_board()
        self._ships = {}
    
    def board(self):
        return self._board
    
    def ships(self):
        return self._ships
    
    def gen_board(self):
        """Initializes the 10x10 board of GridPos objects.
        
        Parameters: None.
        
        Returns: The 2D array representing the board."""

        board = []
        for y in range(10):
            board.append([])

            for x in range(10):
                board[-1].append(GridPos(x, y, None))
        
        return board
    
    def add_validate_ship(self, ship_line):
        """Creates a Ship object from the ship line, ensures no overlap, and
        adds it to the grid.
        
        Parameters:
            ship_line: A line of ship specs from the input file.
        
        Returns: None."""

        # Create the ship and ensure no overlap:
        ship = Ship(ship_line)
        self.ship_no_overlap(ship, ship_line)

        # Add ship to local ships dict, then to board itself:
        self._ships[ship_line[0]] = ship

        for grid_pos in ship.grid_poses():
            self._board[grid_pos.y()][grid_pos.x()] = grid_pos
    
    def process_guess(self, guess):
        """Takes a guess line from the input file and processes it; outputs an
        appropriate result, and alters the base board accordingly.
        
        Parameters:
            guess: The line of a guess from the input file.
        
        Returns: None."""

        # If guess is out of range, skip:
        if not validate_guess(guess):
            return
        
        guess_x_y = guess.split()
        guess_x, guess_y = int(guess_x_y[0]), int(guess_x_y[1])
        guessed = self._board[guess_y][guess_x]  # the guessed spot on board

        if guessed.ship_type() == None:  # if miss
            if not guessed.guessed():
                print("miss")
                guessed.set_guessed()
            else:
                print("miss (again)")
        else:  # if hit
            self.process_hit(guessed)

    def process_hit(self, guessed):
        """Processes a successful hit, including if a ship is sunk or if the
        game ends. Called through the process_guess() method.
        
        Parameters:
            guessed: A GridPos object representing the guessed point.
        
        Returns: None."""

        if guessed.guessed():  # duplicate hit
            print("hit (again)")
        else:
            ship = guessed.ship_type()
            ship.hit_cell()

            if ship.unhit_cells() == 0:  # if ship sunk
                print(f"{ship} sunk")
            else:  # if ship not sunk
                print("hit")
                guessed.set_guessed()

        # If every ship is now sunk, end the game:
        for board_ship in self._ships.values():
            if board_ship.unhit_cells() > 0:
                return
        
        print("all ships sunk: game over")
        sys.exit(0)

    def ship_no_overlap(self, ship, ship_line):
        """Determines if an added ship has any overlap, terminating if so.
        
        Parameters:
            ship: The Ship object to add.
            ship_line: The input line representing the possibly erroneous ship.
        
        Returns: None."""

        for grid_pos in ship.grid_poses():
            this_grid_pos = self._board[grid_pos.y()][grid_pos.x()]
            if this_grid_pos.ship_type() != None:
                print("ERROR: overlapping ship: " + ship_line)
                sys.exit(0)
    
    def __str__(self):
        board_str = ""

        for row_i in range(len(self._board)-1, -1, -1):
            row = self._board[row_i]
            
            board_str += "["
            for grid_pos in row:
                board_str += f"({str(grid_pos)}) "
            board_str += "]\n"
        
        return board_str

class Ship:
    """The Ship class represents a ship on the battleship board. The ship is of
    one of five types of varying sizes.
    
    The constructor accepts a line from the input file, and initializes the
    ship's type, size, occupied grid positions, and amount of unhit cells.
    
    The constructor calls the validate() method, which ensures a ship is within
    bounds, either straight horizontal or vertical, and of a size appropriate
    to its type."""
    
    def __init__(self, ship_line):
        ship_specs = ship_line.split()

        self._type = ship_specs[0]
        self._grid_poses = self.gen_grid_poses(ship_specs[1:])
        self._size = len(self._grid_poses)
        self._unhit_cells = self._size

        self.validate(ship_line)
    
    def type(self):
        return self._type
    
    def grid_poses(self):
        return self._grid_poses
    
    def size(self):
        return self._size
    
    def unhit_cells(self):
        return self._unhit_cells
    
    def hit_cell(self):
        """Hits one of the ship's cells, decrementing its unhit cells by 1.
        
        Parameters: None.
        
        Returns: None."""

        self._unhit_cells -= 1
    
    def gen_grid_poses(self, x_y_specs):
        """Based on x and y starting and ending coordinates, create and return
        a list of GridPos objects representing the ship's occupied area.
        
        Parameters:
            x_y_specs: A 4-element array with values x1, y1, x2, y2 in order.
        
        Returns: The generated list of GridPos objects."""

        # Depending on if vertical or horizontal, send to appropriate method:
        if x_y_specs[0] == x_y_specs[2]:
            return self.gen_vert(x_y_specs)
        else:
            return self.gen_hori(x_y_specs)
    
    def gen_vert(self, x_y_specs):
        """With a vertical ship, generate and return the GridPos list.
        
        Parameters:
            x_y_specs: A 4-element array with values x1, y1, x2, y2 in order.
        
        Returns: The generated list of GridPos objects."""

        # Access the x value, and the lesser and greater y values:
        x, y1, y2 = x_y_specs[0], min(int(x_y_specs[1]), int(x_y_specs[3])), \
            max(int(x_y_specs[1]), int(x_y_specs[3]))
        
        grid_poses = []

        for y_i in range(y1, y2 + 1):
            grid_poses.append(GridPos(x, y_i, self))
        
        return grid_poses
    
    def gen_hori(self, x_y_specs):
        """With a horizontal ship, generate and return the GridPos list.
        
        Parameters:
            x_y_specs: A 4-element array with values x1, y1, x2, y2 in order.
        
        Returns: The generated list of GridPos objects."""

        # Access the lesser and greater x values, and the y value:
        x1, x2, y = min(int(x_y_specs[0]), int(x_y_specs[2])), \
            max(int(x_y_specs[0]), int(x_y_specs[2])), x_y_specs[1]
        
        grid_poses = []

        for x_i in range(x1, x2 + 1):
            grid_poses.append(GridPos(x_i, y, self))

        return grid_poses
    
    def validate(self, ship_line):
        """Validate that the ship is in bounds, is strictly horizontal or
        vertical, and is of the right size for its type.
        
        Parameters:
            ship_line: The line of input representing the ship.
        
        Returns: None."""

        self.ship_on_board(ship_line)
        self.ship_hor_or_vert(ship_line)
        self.validate_type(ship_line)

    def ship_on_board(self, ship_line):
        """Validates that the ship is within bounds, terminating if not.
        
        Parameters:
            ship_line: The line of input representing the ship.
        
        Returns: None."""

        ship_specs = ship_line.split()

        for x_or_y in ship_specs[1:]:
            if int(x_or_y) < 0 or int(x_or_y) >= 10:
                print("ERROR: ship out-of-bounds: " + ship_line)
                sys.exit(0)

    def ship_hor_or_vert(self, ship_line):
        """Validates that the ship is horizontal or vertical, terminating if
        not.
        
        Parameters:
            ship_line: The line of input representing the ship.
        
        Returns: None."""

        ship_specs = ship_line.split()

        if ship_specs[1] != ship_specs[3] and ship_specs[2] != ship_specs[4]:
            print("ERROR: ship not horizontal or vertical: " + ship_line)
            sys.exit(0)
    
    def validate_type(self, ship_line):
        """Validates that the ship is the right size for its type, terminating
        if not.
        
        Parameters:
            ship_line: The line of input representing the ship.
        
        Returns: None."""

        if (self._type == "A" and self._size != 5) or \
           (self._type == "B" and self._size != 4) or \
           (self._type == "S" and self._size != 3) or \
           (self._type == "D" and self._size != 3) or \
           (self._type == "P" and self._size != 2):
            print("ERROR: incorrect ship size: " + ship_line)
            sys.exit(0)
    
    def __str__(self):
        return self._type

def main():
    # Read ship placement file and generate board:
    placement_f = input()
    board = gen_board(placement_f)

    # Read guess file and process guesses:
    guess_f = input()
    process_guesses(board, guess_f)

def gen_board(placement_f):
    """Generates tbe game board, adding each ship from the file to it.
    
    Parameters:
        placement_f: A filename representing ship placements.
    
    Returns: The generated Board object."""

    board = Board()

    file = open(placement_f)
    ship_lines = file.readlines()

    # Validate that the fleet is of the right size and types:
    validate_fleet(ship_lines)

    for ship_line in ship_lines:
        board.add_validate_ship(ship_line)
    
    file.close()
    return board

def process_guesses(board, guess_f):
    """Reads guesses from a file, processing and outputting for each.
    
    Parameters:
        board: The Board object representing the game board.
        guess_f: A filename representing guesses.
    
    Returns: None."""

    file = open(guess_f)
    guesses = file.readlines()

    for guess in guesses:
        guess = guess.strip()

        if guess == "":
            continue

        board.process_guess(guess)
    
    file.close()

def validate_fleet(ship_lines):
    """Validate that the fleet is 5 ships of the correct types, terminating if
    not.
    
    Parameters:
        ship_lines: A list of strings, each representing a ship line.
    
    Returns: None."""

    ship_types = []

    for ship_line in ship_lines:
        if ship_line[0] in ship_types:
            print("ERROR: fleet composition incorrect")
            sys.exit(0)
        ship_types.append(ship_line[0])

    if len(ship_types) != 5:
        print("ERROR: fleet composition incorrect")
        sys.exit(0)

def validate_guess(guess):
    """Validates a guess is within range, returning False if not.
    
    Parameters:
        guess: A string representing a guess.
    
    Returns: False if the guess is illegal, True otherwise."""

    guess_x_y = guess.split()
    guess_x, guess_y = int(guess_x_y[0]), int(guess_x_y[1])

    if guess_x < 0 or guess_x >= 10 or \
       guess_y < 0 or guess_y >= 10:
        print("illegal guess")
        return False
    
    return True

main()
