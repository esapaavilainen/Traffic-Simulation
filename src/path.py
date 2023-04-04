
from constants import Constants
import math

class Pathh():
    
    '''
    This class represents a single vehicle's route across
    the map. Once a vehicle is constructed, it's path
    initially has an empty list of coordinates. The path is
    generated right after the spawn and goal locations are
    determined by the CityCenter-object. 'seld.generate_path'
    is called by the CityCenter-object and will do the
    calculations with the help of Dijkstra's algorithm
    regarding the path. However, if a path can not be
    generated due to an unaccessible goal location (from
    the spawn), 'self.generate_path' is given a new goal. 
    This keeps on going until a functioning path is formed.
    A vehicle's path is fixed once it has been successfully
    created on can be set visible by clicking  on the respective
    vehicle. The  length of 'self.coordinates' is equal to the
    amount of blocks the vehicle is supposed to cross plus two.
    One set of coordinates is added at the start and one at the 
    end, since the vehicle is spawned outside the map and will
    eventually exit it as well. 'self.update' is called every
    time the vehicle has progressed enough on the path, check
    'Vehicle.update_path_progress' for further information.
    '''
    
    def __init__(self, vehicle_type):
        # This many coordinate pairs for one normal-sized map piece.
        self.count = 20
        # This many coordinates pairs for one short curve.
        self.decreased_count = 12
        self.size = Constants.BLOCK_SIZE
        self.set_radius(vehicle_type)
        # This will be a 3-dimensional list.
        self.coordinates = []
        self.progress = 0
        self.sub_progress = 0
        
    def get_spawn(self):
        # Returns the 3-term spawn point, e.g. the x-
        #coordinate, the y-coordinate and the initial direction.
        return self.spawn
        
    def get_coordinates(self):
        # Return the 3-dimensional list of all the coordinates.
        return self.coordinates
    
    def get_progress(self):
        # 'self.progress' will define which indexes from 'self.coordinates'
        # are considered relevant to the vehicle. 'self.sub_progress' in it's
        # turn tells which coordinate pairs from the relevant list of coordinates
        # have been passed and can therefore be ignored.
        return self.progress, self.sub_progress
    
    def update(self, next_piece=False):
        # This method is regularly called by the respective Vehicle-object.
        # When 'next_piece' equals True, the vehicle has moved enough for a new path
        # piece to become relevant and for the previously first one to become irrelevant.
        self.sub_progress += 1
        if next_piece:
            self.progress += 1
            self.sub_progress = 0        
    
    def set_radius(self, vehicle_type):
        # This must be done since some vehicles are larger than others.
        # A larger vehicle is given less room to move around the path's
        # center-axis, therefore the path radius will be smaller.
        if vehicle_type == Constants.SEDAN: coefficient = 0.30
        elif vehicle_type == Constants.MINI_VAN: coefficient = 0.28
        else: coefficient = 0.25
        self.radius = coefficient*Constants.PATH_RADIUS

    def set_spawn(self, entry):
        # Set the path's first piece and define the spawn point.
        x, y = entry[0], entry[1]
        outside = self.size/2
        size = self.size
        
        if x == 0:
            self.set_line([x-size, y//size*size], (1, -1))
            x -= outside
            rotation = 0
            previous_direction = 2
        elif y == 0:
            self.set_line([x//size*size, y-size], (-1, -1))
            y -= outside
            rotation = 270
            previous_direction = 1
        elif x > y:
            self.set_line([x, y//size*size], (-1, 1))
            x += outside
            rotation = 180
            previous_direction = 0
        else:
            self.set_line([x//size*size, y], (1, 1))
            y += outside
            rotation = 90
            previous_direction = 3
            
        # 'self.spawn' will tell the exact location the vehicle is placed in as it spawns on the map.
        # The value at index 2 will tell the desired rotation as the initial velocity is defined.
        self.spawn = [x, y, rotation]
        
        return previous_direction
    
    def set_final(self, goal):
        # Set the final two pieces and define the goal coordinates.
        x, y = goal[0], goal[1]
        outside = self.size
        size = self.size
        
        if x == 0:
            self.set_line([x, y//size*size], (-1, 1))
            self.set_line([x-size, y//size*size], (-1, 1))
            x -= outside
        elif y == 0:
            self.set_line([x//size*size, y], (1, 1))
            self.set_line([x//size*size, y-size], (1, 1))
            y -= outside
        elif x > y:
            self.set_line([x-size, y//size*size], (1, -1))
            self.set_line([x, y//size*size], (1, -1))
            x += outside
        else:
            self.set_line([x//size*size, y-size], (-1, -1))
            self.set_line([x//size*size, y], (-1, -1))
            y += outside
            
        self.goal = [x, y]
    
    def generate_path(self, graph, city_blocks, entry, goal):
        # This method is responsible for creating the shortest path between entry and goal.
        
        # Form vertices source and target with the help of coordinates entry and goal.
        # Entry and goal are the exact coordinates the vehicle is supposed to enter/exit the city.
        x = self.size
        source = [int(entry[0]/x), int(entry[1]/x)]
        target = [int(goal[0]/x), int(goal[1]/x)]
        upper_limit = len(city_blocks)-1
        for i in range(2):
            if source[i] > upper_limit: source[i] -= 1
            if target[i] > upper_limit: target[i] -= 1
        source = str(source[0]) + str(source[1])
        target = str(target[0]) + str(target[1])
    
        dist = dict()
        prev = dict()

        def Dijkstra():
            # This is Dijkstra's algorithm for finding the minimum path from source to target.
            vertices = graph.get_vertices()[:] # example: ['01', '10', '11', '12', '21'] 
            adjacency = graph.get_adjacency() # example: {'01': [('11', 1, 0)], '11': [('21', 1, 0), ('01', 1, 2)]}
    
            # Initially, every unexplored vertex has an infinite distance. If a vertex is left 
            # unexplored we can easily tell this from whether distance is infinite or not. 
            for vertex in vertices:
                dist[vertex] = math.inf
                prev[vertex] = 'undefined'
                
            # We start from vertex source.
            dist[source] = 0
            
            while vertices != []:
                
                # Choose the vertex with the smallest distance.
                distance = math.inf
                for vertex in vertices:
                    if dist[vertex] < distance:
                        distance = dist[vertex]
                        chosen_vertex = vertex
                        
                # If we have to break the loop, it means that the city layout has isolated road
                # pieces and that all reachable vertices (from source) have already been visited.
                if distance == math.inf: break
    
                vertices.remove(chosen_vertex)
                
                # Enough is done.
                #if chosen_vertex == target: break
                
                adj = adjacency[chosen_vertex] # example: [('21', 1, 0), ('10', 1, 1), ('01', 1, 2)]
                
                # In an adjacency tuple, the first value represents the neighboring vertex, 
                # the second it's distance and the third one it's direction from chosen_vertex.  
                for tuple in adj:
                    neighbor = tuple[0]
                    # If this vertex is not in vertices anymore, it's not taken to account.
                    if neighbor in vertices:
                        edge_length = tuple[1]
                        alt = dist[chosen_vertex] + edge_length
                        # The smallest possible alternative is saved.
                        if alt < dist[neighbor]:
                            dist[neighbor] = alt
                            prev[neighbor] = chosen_vertex
                        
        Dijkstra()

        if dist[target] == math.inf:
            # This means that we have failed at generating the path. If we failed, it's all right, 
            # since it was bound to happen anyway. By returning False we let the CityCenter-object
            # know that we need new coordinates for source and target, the graph remains unchanged.
            return False
        
        def set_pieces(target):
            # Build the path one piece at a time.

            # The first piece
            previous_direction = self.set_spawn(entry)

            path_vertices = []
            while target != 'undefined':
                path_vertices.append(target)
                target = prev[target]
            # Now we will have all the necessary
            # vertices listed from start to finish.
            path_vertices.reverse()
            
            # Dictionary 'dire' will tell which direction
            # we must travel from each vertex on the path.
            dire = dict()
            adjacency = graph.get_adjacency()
            limit = len(path_vertices)-1
            for index in range(limit):
                vertex = path_vertices[index]
                next_vertex = path_vertices[index+1]
                neighbors = adjacency[vertex]
                for neighbor in neighbors:
                    # This is the neighbor whose direction we want to save.
                    if neighbor[0] == next_vertex:
                        dire[vertex] = neighbor[2]
                        break
            dire[path_vertices[-1]] = 'final'  
            
            x = self.size
            
            while True:
                
                loc = path_vertices.pop(0)
                i, j = int(loc[0]), int(loc[1])
                direction = dire[loc]

                if direction == 'final': break
                
                def set_piece(direction, previous_direction, i ,j):
                    # Set the correct path piece for given parameters.
                    
                    sub = direction - previous_direction
                    
                    if abs(sub) == 3: sub = -sub
    
                    if abs(sub) == 2:
                        # Directions remain unchanged.
                        if direction == 0: ctuple = (1, -1)
                        elif direction == 1: ctuple = (1, 1)
                        elif direction == 2: ctuple = (-1, 1)
                        else: ctuple = (-1, -1)
                        self.set_line([i*x, j*x], ctuple)
                    elif sub > 0:
                        # Right turn
                        if direction == 0:
                            ctuple = (1, -1)
                            previous_direction = 2
                        elif direction == 1:
                            ctuple = (1, 1)
                            previous_direction = 3
                        elif direction == 2:
                            ctuple = (-1, 1)
                            previous_direction = 0
                        else:
                            ctuple = (-1, -1)
                            previous_direction = 1
                        self.set_curve_2([i*x, j*x], ctuple)
                    else:
                        # Left turn
                        if direction == 0:
                            ctuple = (1, 1)
                            previous_direction = 2
                        elif direction == 1:
                            ctuple = (-1, 1)
                            previous_direction = 3
                        elif direction == 2:
                            ctuple = (-1, -1)
                            previous_direction = 0
                        else:
                            ctuple = (1, -1)
                            previous_direction = 1
                        self.set_curve_1([i*x, j*x], ctuple)
                    
                    return previous_direction
                
                previous_direction = set_piece(direction, previous_direction, i ,j)
                    
                if direction == 0: i += 1
                elif direction == 1: j -= 1
                elif direction == 2: i -= 1
                else: j += 1
                loc = str(i)+str(j)
                
                while not loc in path_vertices:
                    # Define direction with the help of 'city_blocks'.
                    
                    block = city_blocks[i][j]
                    for index in range(4):
                        if block[index] == 1 and not index == previous_direction:
                            direction = index
                            previous_direction = set_piece(direction, previous_direction, i ,j)
                            break
                        
                    if direction == 0: i += 1
                    elif direction == 1: j -= 1
                    elif direction == 2: i -= 1
                    else: j += 1
                    
                    loc = str(i)+str(j)
            
            # Last two pieces
            self.set_final(goal)
        
        set_pieces(target)

        # This will tell the biggest allowed index in self.coordinates.
        self.limit = len(self.get_coordinates())-1

        # Path generated successfully.
        return True
        
    def set_line(self, attach_point, ctuple):
        # This method creates a straight line of coordinates.
        
        x_0 = attach_point[0]
        y_0 = attach_point[1]
        points = []
        reverse = False
        
        if ctuple == (1, 1):
            x_step = 0
            y_step = self.size/self.count
            x_0 += 11.0/16.0*self.size
            reverse = True
        elif ctuple == (-1, 1):
            x_step = self.size/self.count
            y_step = 0
            y_0 += 5.0/16.0*self.size
            reverse = True
        elif ctuple == (-1, -1):
            x_step = 0
            y_step = self.size/self.count
            x_0 += 5.0/16.0*self.size
        else:
            x_step = self.size/self.count
            y_step = 0
            y_0 += 11.0/16.0*self.size

        for i in range(self.count):
            points.append([])
            points[i].append(x_0+i*x_step)
            points[i].append(y_0+i*y_step)
        
        # In 2/4 cases reversing must be done so that the list index grows as we move along the path.
        # If we reverse the order, we must also take care that no "holes" are left in the path. A hole
        # is an unnecessarily large gap between two coordinate pairs. We don't want to leave two 
        # identical coordinates in the path either.
        if reverse:
            if ctuple == (1, 1):
                points.append([])
                points[-1].append(x_0)
                points[-1].append(y_0+self.size)
                points.reverse()
                points.pop(-1)
            elif ctuple == (-1, 1):
                points.append([])
                points[-1].append(x_0+self.size)
                points[-1].append(y_0)
                points.reverse()
                points.pop(-1)
        
        self.coordinates.append(points)
    
    def set_curve_1(self, attach_point, ctuple):
        # This method creates a set of coordinates resembling
        # a quarter of a big circle, a wide left turn.
        
        r = 11.0/16.0*self.size
        step = 90.0/self.count
        x_0 = attach_point[0]
        y_0 = attach_point[1]
        points = []
        offset = self.size
        
        if ctuple == (1, 1):
            angle = 180
            x_0 += offset
        elif ctuple == (-1, 1):
            angle = 270
        elif ctuple == (-1, -1):
            angle = 0
            y_0 += offset
        else:
            angle = 90
            x_0 += offset
            y_0 += offset
        
        for i in range(self.count):
            points.append([])
            points[i].append(x_0+r*math.cos(math.radians(angle+i*step)))
            points[i].append(y_0-r*math.sin(math.radians(angle+i*step)))

        self.coordinates.append(points)
            
    def set_curve_2(self, attach_point, ctuple):
        # Similar to the one above but the circle radius is smaller.
        # This curve resembles a strict right turn.
        r = 5.0/16.0*self.size
        step = 90.0/(self.decreased_count)
        x_0 = attach_point[0]
        y_0 = attach_point[1]
        points = []
        offset = self.size
        
        if ctuple == (1, 1):
            angle = 180
            x_0 += offset
        elif ctuple == (-1, 1):
            angle = 270
        elif ctuple == (-1, -1):
            angle = 0
            y_0 += offset
        else:
            angle = 90
            x_0 += offset
            y_0 += offset
        
        for i in range(self.decreased_count):
            points.append([])
            points[i].append(x_0+r*math.cos(math.radians(angle+i*step)))
            points[i].append(y_0-r*math.sin(math.radians(angle+i*step)))
            
        # Add one more point in the far end of the curve, when adjacent path-pieces
        # are not identical, there's a chance that a "hole" will be left in the path.
        # Adding a coordinate pair at index self.count will stop this from happening.
        # Note that after reversing the order the following point will be at index 0.
        
        points.append([])
        
        if ctuple == (1, 1):
            points[-1].append(x_0)
            points[-1].append(y_0+r)
        elif ctuple == (-1, 1):
            points[-1].append(x_0+r)
            points[-1].append(y_0)
        elif ctuple == (-1, -1):
            points[-1].append(x_0)
            points[-1].append(y_0-r)
        else:
            points[-1].append(x_0-r)
            points[-1].append(y_0)
        
        # This must be done so that the list index grows as we move along the path.
        points.reverse()
        
        # Remove the now last coordinate pair, the first coordinates of the following
        # path piece would otherwise be identical.
        points.pop(-1)
        
        self.coordinates.append(points)















