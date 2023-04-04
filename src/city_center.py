

from random import randint
from constants import Constants
from graph import Graph


class CityCenter():
    
    '''
    This class represents the area in which the vehicles move.
    In this class a city block is represented as a list with four 
    binary values. If the observed value is 1, the block has road access
    on this side. The value at index 0 stands for the right side,
    index 1 stands for the top side and so on. The only unavailable
    block is a block with three zeros and only a single one, if this
    existed, it would look like a dead end road piece. For further 
    information, check 'self.set_options' and 'self.options'.
    '''
    
    def __init__(self, dimensions):
        self.dimensions = dimensions
        # Initialize every possible block variation.
        self.set_options()
        # Form the city layout with the blocks.
        self.set_blocks()
        # Define the maximum vehicle occupation.
        self.set_maximum()
        # A graph to resemble the road structure.
        self.graph = Graph(self.blocks)
        # These will get updated as vehicles enter the map, check 
        # 'self.update' and 'self.add_vehicle' for further information.
        # 'self.availabe' and 'self.cooldown' will complement each other.
        self.vehicles = []
        self.available = []
        self.cooldown = dict()
        # Set all the locations where the 
        # map can be entered and exited.
        self.set_borders() 
        
    def get_vehicles(self): return self.vehicles    
        
    def get_dimensions(self): return self.dimensions
    
    def get_block(self, x, y):
        # Returns the identifier for the block at indexes x, y.
        return self.blocks[x][y]
    
    def is_overheated(self):
        # When this returns True, the city isn't physically full, but
        # each point of entry is cooling down. This means that a new 
        # vehicle can not be spawned yet.
        return len(self.available) == 0
    
    def is_at_full_capacity(self, rush_hour):
        # The intended limit for the vehicle capacity for this CityCenter
        # has been reached. Check 'self.set_maximum' for further information.
        return len(self.get_vehicles()) == self.get_maximum(rush_hour)
    
    def update(self):
        # This method is not called when the simulation is paused.
        
        done = []
        
        # Keep every relevant vehicle moving,
        # remove all the irrelevant ones.
        for vehicle in self.get_vehicles():
            if not vehicle.is_done():
                vehicle.drive()
            else:
                # If we get here, this vehicle has reached it's
                # goal and is no longer needed for the simulation.
                done.append(vehicle)
                
        if len(done): self.remove_vehicles(done)
        
        def decrease_cooldown():
            # Decrease the cool down time for each value in 'self.cooldown'. Entry locations
            # at these indexes are prohibited for as long as they have cool down. The key is
            # the prohibited index and the value is the remaining cool down time. 
            
            ok = []
            for index in self.cooldown.keys():
                time = self.cooldown[index]
                self.cooldown[index] = time-Constants.TIME_STEP
                if self.cooldown[index] <= 0:
                    ok.append(index)
            
            for index in ok:
                del self.cooldown[index]
                self.available.append(index)
            
        decrease_cooldown()
                
        # Every VehicleGraphicsModel-object representing a Vehicle-
        # object in 'done' will get removed from the GUI's graphics scene.
        return done
    
    def get_maximum(self, rush_hour):
        # Return the maximum amount of vehicles the city can hold at once.
        
        # In rush hour-mode the city can hold 
        # 'self.maximum' amount of vehicles.
        if rush_hour:
            return self.maximum
        
        # In casual mode the absolute limit can't be reached.
        entry_count = len(self.entry_points)
        subtraction = int(entry_count/4)
        
        return self.maximum - subtraction
    
    def remove_vehicles(self, done):
        # Remove every vehicle in 'done' and care of the radars of all the
        # remaining vehicles. This method can also be called by the GUI.
        
        for vehicle in done:
            self.get_vehicles().remove(vehicle)
            
        for vehicle in self.get_vehicles():
            for removed in done:
                vehicle.get_radar().remove_target(removed)
    
    def add_vehicle(self, added_vehicle):
        # This method adds a new new vehicle on the map. Before the vehicle can 
        # be spawned, it's path must be defined. The path's start and end locations 
        # determine the vehicle's spawn and goal. All the possible locations exist 
        # in 'self.entry_points' and in 'self.exit_points'. 'self.available' and 
        # 'self.cooldown' tell which of them can be used at the moment.
                                        
        ok_indexes = self.available
        limit = len(self.entry_points)-1
        
        OK = False
        while not OK:
            # Choose the vehicle entry location by random.
            index1 = randint(0, limit)
            # The index must be in 'self.available'.
            if index1 in ok_indexes:
                OK = True

        entry = self.entry_points[index1]
        
        OK = False
        while not OK:
            # Choose the goal randomly, but aim for a different side on the map.
            index2 = randint(index1+int(0.25*limit), index1+int(0.75*limit))
            if index2 > limit:
                index2 -= limit
            # The vehicle can not enter and exit the map at the same location.
            if index1 != index2:
                OK = True
            
        goal = self.exit_points[index2]

        # Let the vehicle's Pathh-object decide the route between these locations.
        # Some exits might be unavailable to certain entry points though, depends on 
        # the layout. If 'functioning' equals True, 'added_vehicle' has a functioning path.
        functioning = added_vehicle.get_path().generate_path(self.graph, self.blocks, entry, goal)
        
        while not functioning:
            # Hold on to the same entry and find a goal location 
            # that enables a functioning path between these two.
            
            OK = False
            while not OK:
                # The path generation failed on the 
                # first try, make the requirements easier.
                index2 = randint(0, limit)
                if index2 > limit:
                    index2 -= limit
                if index1 != index2:
                    OK = True
                    
            goal = self.exit_points[index2]
            
            # Try as many times as it takes.
            functioning = added_vehicle.get_path().generate_path(self.graph, self.blocks, entry, goal)
                   
        # 5 seconds of cool down for the chosen entry.
        self.cooldown[index1] = 5000
        
        # Remove the entry from 'self.available' for the time being.
        self.available.remove(index1)
        
        for vehicle in self.get_vehicles():
            # Update every vehicle's radar of surrounding
            # vehicles, including the freshly added one.
            vehicle.get_radar().add_target(added_vehicle)
            added_vehicle.get_radar().add_target(vehicle)
        
        self.vehicles.append(added_vehicle)
        
        # Now that everything is taken care of, spawn 'added_vehicle'
        # on the map. The GUI will take care of the graphics.
        added_vehicle.spawn()
    
    def set_options(self):
        self.options = [None]*12
        # These represent all the 
        # possible city block variations.
        self.options[0] = [0,0,0,0]
        self.options[1] = [1,0,1,0]
        self.options[2] = [0,1,0,1]
        self.options[3] = [1,1,0,0]
        self.options[4] = [0,1,1,0]
        self.options[5] = [0,0,1,1]
        self.options[6] = [1,0,0,1]
        self.options[7] = [1,1,1,0]
        self.options[8] = [0,1,1,1]
        self.options[9] = [1,0,1,1]
        self.options[10] = [1,1,0,1]
        self.options[11] = [1,1,1,1]
        
    def calculate_weight(self, block):
        # A blocks weight is defined by how many accessible sides it has.
        weight = 0
        for i in block:
            if i == 1:
                weight += 1
        return weight
        
    def check_adjacent(self, block, index):
        # This method is helps to determine which blocks can be placed next to the current one.
        if block == [None]: return None
        elif block[index] == 1: return 1
        else: return 0
        
    def on_the_edge(self, i, j):
        # Returns True if the block at indexes i, j is on the edge of the map.
        if i == 0: return True
        elif i == self.get_dimensions()-1: return True
        elif j == 0: return True
        elif j == self.get_dimensions()-1: return True
        else: return False

    def find_suitable(self, conditions):
        # This method chooses and returns a suitable block for the current situation.
        # If there are more than one suitable block, the block is chosen randomly from these.
        
        suitables = self.options[:]
        unsuitables = []
        
        # 12 elements in 'self.options'
        for i in range(12):
            # 4 values in a block
            for j in range(4):
                # 0 and 1 are the conditions
                if conditions[j] == 0:
                    if self.options[i][j] != 0:
                        if not self.options[i] in unsuitables:
                            unsuitables.append(self.options[i])
                elif conditions[j] == 1:
                    if self.options[i][j] != 1:
                        if not self.options[i] in unsuitables:
                            unsuitables.append(self.options[i])
        
        for block in unsuitables:
            suitables.remove(block)
        
        if len(suitables) == 0: return None
        
        index = randint(0, len(suitables)-1)
        chosen = suitables[index]
        
        return chosen
        
    def set_blocks(self):
        
        limit = self.get_dimensions()

        # Initialize the blocks.
        self.blocks = []
        for i in range(limit):
            self.blocks.append([])
            for j in range(limit):
                self.blocks[i].append([None])
                
        # Set the bottom and top rows first.
        for i in range(limit):
            for j in range(limit):
                if j == 0:
                    if i%2: self.blocks[i][j] = [0,1,0,1]
                    else: self.blocks[i][j] = [0,0,0,0]
                    if i == limit-1: self.blocks[i][j] = [0,0,0,0]
                elif j == limit-1 and limit%2:
                    if i%2: self.blocks[i][j] = [0,1,0,1]
                    else: self.blocks[i][j] = [0,0,0,0]
                    if i == 0 or i == limit-1: self.blocks[i][j] = [0,0,0,0]
                elif j == limit-1 and not limit%2:
                    if not i%2: self.blocks[i][j] = [0,1,0,1]
                    else: self.blocks[i][j] = [0,0,0,0]
                    if i == 0 or i == limit-1: self.blocks[i][j] = [0,0,0,0]   
                                                       
        # Set the left-most and right-most columns.      
        for i in range(limit):
            for j in range(1, limit-1):
                if i == 0 and not limit%2:
                    if not j%2: self.blocks[i][j] = [1,0,1,0]
                    else: self.blocks[i][j] = [0,0,0,0]
                elif i == 0 and limit%2:
                    if j%2: self.blocks[i][j] = [1,0,1,0]
                    else: self.blocks[i][j] = [0,0,0,0]
                elif i == limit-1:
                    if j%2: self.blocks[i][j] = [1,0,1,0]
                    else: self.blocks[i][j] = [0,0,0,0]      
        
        # Set four connecting pieces near the corners.
        if limit >= 6 and limit%2:
            self.blocks[1][1] = [0,1,1,1]
            self.blocks[limit-2][1] = [1,1,1,0]
            self.blocks[1][limit-2] = [1,0,1,1]
            self.blocks[limit-2][limit-2] = [1,1,0,1]      
        elif limit >= 6:
            self.blocks[1][2] = [0,1,1,1]
            self.blocks[limit-3][1] = [1,1,1,0]
            self.blocks[2][limit-2] = [1,0,1,1]
            self.blocks[limit-2][limit-3] = [1,1,0,1]
        
        # Set a few centerpieces next.
        if limit == 4:
            # No randomness in a 4x4 layout.
            self.blocks[1][1] = [0,1,0,1]
            self.blocks[1][2] = [1,1,1,0]
            self.blocks[2][1] = [1,0,0,1]
            self.blocks[2][2] = [0,1,1,1]
        elif limit == 5:
            self.blocks[2][2] = [1,0,1,1]
            self.blocks[3][2] = [0,1,1,0]
            self.blocks[2][3] = [1,1,0,0]
        elif limit == 6:
            self.blocks[2][2] = [1,1,0,0]
            self.blocks[2][3] = [0,0,0,0]
            self.blocks[3][2] = [1,0,1,1]
            self.blocks[3][3] = [0,1,0,1]
        elif limit == 7:
            self.blocks[2][2] = [1,0,1,1]
            self.blocks[2][4] = [1,1,1,1]
            self.blocks[4][2] = [1,1,1,1]
            self.blocks[4][4] = [1,1,1,0]
            self.blocks[3][2] = [1,0,1,0]
            self.blocks[3][4] = [1,0,1,0]
            self.blocks[2][3] = [0,1,0,1]
            self.blocks[4][3] = [0,1,0,1]
            self.blocks[3][3] = [0,0,0,0]
            self.blocks[1][4] = [1,1,0,0]
            self.blocks[4][5] = [0,0,0,0]
            self.blocks[3][5] = [0,0,1,1]
        elif limit == 8:
            self.blocks[1][1] = [1,1,0,0]
            self.blocks[1][2] = [1,0,1,1]
            self.blocks[2][1] = [1,0,1,1]
            self.blocks[2][2] = [0,1,1,0]
            self.blocks[5][2] = [0,0,0,0]
            self.blocks[2][5] = [0,0,0,0]
            self.blocks[3][3] = [1,0,0,1]
            self.blocks[4][3] = [1,1,1,1]
            self.blocks[3][4] = [0,1,1,0]
            self.blocks[4][4] = [0,1,0,1]
            self.blocks[2][4] = [1,0,1,0]
            self.blocks[2][3] = [0,0,0,0]
            self.blocks[4][2] = [0,1,0,1]
            self.blocks[3][2] = [0,0,0,0]
            self.blocks[6][4] = [0,1,0,1]
        elif limit == 9:
            self.blocks[3][3] = [0,0,0,0]
            self.blocks[4][3] = [0,1,0,1]
            self.blocks[5][3] = [0,0,0,0]
            self.blocks[3][4] = [1,0,1,0]
            self.blocks[4][4] = [1,1,1,1]
            self.blocks[5][4] = [1,0,1,0]
            self.blocks[3][5] = [0,0,0,0]
            self.blocks[4][5] = [0,1,0,1]
            self.blocks[5][5] = [0,0,0,0]
            self.blocks[2][1] = [0,0,0,0]
            self.blocks[7][2] = [0,0,0,0]
            self.blocks[1][6] = [0,0,0,0]
            self.blocks[6][7] = [0,1,1,0]
            self.blocks[7][6] = [0,0,1,1]
            self.blocks[7][5] = [1,1,1,0]
            self.blocks[7][4] = [0,1,0,1]
            self.blocks[2][3] = [0,1,0,1]
            
        # Set the missing pieces, this is partially random.
        for i in range(1,limit-1):
            for j in range(1,limit-1):
                if self.blocks[i][j] == [None]:                    
                    # The requirement can be 1, 0 or None, depends on the adjacent block and its observed side.                    
                    right_requirement = self.check_adjacent(self.blocks[i+1][j], 2)
                    above_requirement = self.check_adjacent(self.blocks[i][j-1], 3)
                    left_requirement = self.check_adjacent(self.blocks[i-1][j], 0)
                    below_requirement = self.check_adjacent(self.blocks[i][j+1], 1)
                    new = self.find_suitable([right_requirement,above_requirement,left_requirement,below_requirement])
                    if new == None:
                        self.set_blocks()
                    else: self.blocks[i][j] = new
        
        # If there are dead loops, make a new one.
        self.check_for_dead_loops()
                
    def check_for_dead_loops(self):
        # This method finds if there are any "dead" loops in the city layout.
        # A dead loop is a loop that starts from an intersection and ends at the same
        # intersection without having another intersection-piece in between.
        
        limit = self.get_dimensions()
        visited = []
        
        for i in range(limit):
            visited.append([])
            for j in range(limit):
                # Lawn and edge pieces are automatically visited.
                if self.calculate_weight(self.get_block(i,j)) == 0 or self.on_the_edge(i,j):
                    visited[i].append(True)
                else: visited[i].append(False)
        
        self.dead = False
        
        for i in range(1, limit-1):
            for j in range(1, limit-1):
                if visited[i][j] == False:
                    self.DFS(visited, i, j, None, None, None)      
        
        if self.dead:
            # Let's try again, this happens rarely.
            self.set_blocks()

    def DFS(self, visited, i, j, i_start, j_start, previous):
        # This recursive algorithm goes through the blocks in depth-first search
        # order. When we arrive to an unvisited intersection, after marking it visited, we 
        # first try the block on the right, if we have access to it. Next we try the one above,
        # the one on the left and the one below respectively. The previous parameter tells
        # the direction the current block was entered from (0, 1, 3, 3), this way we don't 
        # start to backtrack. This method is called from 'self.check_dead_loops()'.
        
        visited[i][j] = True
        
        # If this is an intersection block we start looking for dead loops from here.
        # If we find an intersection block in the observed chain of blocks, we can safely say
        # that no dead loops start from the the previous observation point (if there was one).
        if self.calculate_weight(self.get_block(i, j)) > 2:
            i_start, j_start = i, j
            
        # Try moving right.
        if self.blocks[i][j][0] == 1 and not previous == 0:
            if visited[i+1][j] == True:
                if i+1 == i_start and j == j_start: self.dead = True
            else: self.DFS(visited, i+1, j, i_start, j_start, 2)
        # Try moving up.
        if self.blocks[i][j][1] == 1 and not previous == 1:
            if visited[i][j-1] == True:
                if i == i_start and j-1 == j_start: self.dead = True
            else: self.DFS(visited, i, j-1, i_start, j_start, 3)
        # Try moving left.
        if self.blocks[i][j][2] == 1 and not previous == 2:
            if visited[i-1][j] == True:
                if i-1 == i_start and j == j_start: self.dead = True
            else: self.DFS(visited, i-1, j, i_start, j_start, 0)
        # Try moving down.
        if self.blocks[i][j][3] == 1 and not previous == 3:
            if visited[i][j+1] == True:
                if i == i_start and j+1 == j_start: self.dead = True
            else: self.DFS(visited, i, j+1, i_start, j_start, 1)
            
    def set_maximum(self):
        # The maximum vehicle occupation is directly proportional
        # to the city dimensions, e.g. the length of the map edge.
        # If the length is odd, growing it by one doesn't add any
        # locations of entry, therefore layouts with even dimensions
        # have proportionally smaller limit for vehicle occupation.

        dim = self.get_dimensions()
        add = False
        
        if not dim%2:
            dim -= 1
            add = True
        
        self.maximum = 2*dim
        
        if add: self.maximum += 1
        
        if dim <= 5:
            # The smallest layouts (3x3 and 4x4)
            # have only one entry on each side.
            self.maximum -= 2

    def set_borders(self):
        # Mark all the coordinates where the map can be entered and exited.
        # List also their indexes as the first value, in 'self.available' this will
        # be needed later on when entry points with certain indexes are cooling down.
        
        x = Constants.BLOCK_SIZE
        r = Constants.PATH_RADIUS
        limit = self.get_dimensions()
        
        self.entry_points = []
        self.exit_points = []
        
        for vertex in self.graph.get_vertices():
            
            # The vertex itself tells the coordinates.
            i, j = int(vertex[0]), int(vertex[1])

            if i == 0:
                # Left side
                self.entry_points.append([])
                self.entry_points[-1].append(0)
                self.entry_points[-1].append(j*x + x/2 + r)
                self.exit_points.append([])
                self.exit_points[-1].append(0)
                self.exit_points[-1].append(j*x + x/2 - r)
            elif j == 0:
                # Top side
                self.entry_points.append([])
                self.entry_points[-1].append(i*x + x/2 - r)
                self.entry_points[-1].append(0)
                self.exit_points.append([])
                self.exit_points[-1].append(i*x + x/2 + r)
                self.exit_points[-1].append(0)
            elif i == limit-1:
                # Right side
                self.entry_points.append([])
                self.entry_points[-1].append(limit*x)
                self.entry_points[-1].append(j*x + x/2 - r)
                self.exit_points.append([])
                self.exit_points[-1].append(limit*x)
                self.exit_points[-1].append(j*x + x/2 + r)
            elif j == limit-1:
                # Bottom side
                self.entry_points.append([])
                self.entry_points[-1].append(i*x + x/2 + r)
                self.entry_points[-1].append(limit*x)
                self.exit_points.append([])
                self.exit_points[-1].append(i*x + x/2 - r)  
                self.exit_points[-1].append(limit*x)
        
        # List 'self.available' will quickly tell the indexes of currently 
        # accessible entries. As a vehicle uses a certain location to enter 
        # the map, this can not be used immediately again, otherwise vehicles 
        # might collide right as they spawn.
        for index in range(len(self.entry_points)):
            self.available.append(index)
            
    def reset(self):
        # This is called when a new simulation is 
        # started but the same layout is kept. The 
        # GUI will take care of the expired graphics.
        
        self.vehicles = []
        self.available = []
        self.cooldown = dict()
        
        for index in range(len(self.entry_points)):
            self.available.append(index)

        
        
        