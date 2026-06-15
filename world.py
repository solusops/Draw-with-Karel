# world.py
# This module manages the state of the Karel world grid.

class World:
    def __init__(self, initial_grid_size=3):
        # How many cells are visible horizontally and vertically
        self.grid_size = initial_grid_size
        
        # The logical grid size used for simulation (allows us to zoom in/out without breaking loops)
        self.logical_grid_cols = initial_grid_size
        self.logical_grid_rows = initial_grid_size
        
        # A dictionary to store Karels. 
        # The key is a tuple (column, row).
        # The value is a dictionary: {"direction": "East", "color": "Red"}
        self.karels = {}
    
    def add_karel(self, col, row, direction, color):
        """Places a new Karel at the given column and row."""
        self.karels[(col, row)] = {"direction": direction, "color": color}
        
    def remove_karel(self, col, row):
        """Removes a Karel from the given column and row if one exists."""
        if (col, row) in self.karels:
            del self.karels[(col, row)]
            
    def get_karel(self, col, row):
        """Returns the Karel dictionary at (col, row), or None if empty."""
        if (col, row) in self.karels:
            return self.karels[(col, row)]
        return None

    def clear(self):
        """Removes all Karels from the world."""
        self.karels.clear()

    def zoom_in(self):
        """Decreases the number of visible cells, making everything look bigger."""
        if self.grid_size > 1:
            self.grid_size -= 1

    def zoom_out(self):
        """Increases the number of visible cells, making everything look smaller."""
        if self.grid_size < 50:
            self.grid_size += 1

    def sync_logical_grid(self, cols, rows):
        """
        Synchronizes the logical simulation boundary with the current visible grid size.
        This is typically called when the simulation is stopped/reset.
        """
        self.logical_grid_cols = cols
        self.logical_grid_rows = rows
