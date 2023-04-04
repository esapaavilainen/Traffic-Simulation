
import math
from constants import Constants


class Radar():
    
    '''
    This class helps the vehicle observe it's surroundings, every
    vehicle has one Radar-object. This class also helps with numerous
    vector calculations. The radar has to be constantly updated to
    have it in the correct location and keep it pointing the right way.
    The radar is a full circle around the vehicle, the radius is equal
    to 'self.range'. Every vehicle (except the owner) in the 
    city can be found in 'self.targets', not all of these are visible
    though.
    '''
    
    def __init__(self):
        self.range = 1.75*Constants.BLOCK_SIZE
        self.location = None
        self.rotation = None
        self.direction = [None, None]
        self.targets = []
        self.visible = []
    
    def set_radar(self, radar_position, rotation):
        # This is constantly called to keep the radar up to date.
        
        # Same as the vehicle position
        self.location = radar_position
        
        # Same as the vehicle rotation
        self.rotation = rotation
        
        # A pseudo velocity
        x_component = 10*math.cos(math.radians(self.rotation))
        y_component = 10*math.sin(math.radians(self.rotation))
        self.direction = [x_component, y_component]
        
        # All the relevant targets
        self.visible = []
        for vehicle in self.targets:
            if self.distance(self.location, vehicle.get_position()) <= self.range:
                # 'vehicle' is inside the range.
                self.visible.append(vehicle)
    
    def add_target(self, new_vehicle):
        # Update the vehicles to the current situation, this is
        # called every time a new vehicle is spawned on the map.
        self.targets.append(new_vehicle)
    
    def remove_target(self, removed_vehicle):
        # Remove the target after it has reached it's goal.
        self.targets.remove(removed_vehicle)
        
    def in_radar(self):
        # Return a list of all the vehicles inside the radar.
        return self.visible
    
    def distance(self, p1, p2):
        # Return the distance between the given locations.
        return math.sqrt(pow(p1[0]-p2[0],2)+pow(p1[1]-p2[1],2))
    
    def magnitude(self, vector):
        # Get the vector magnitude.
        return self.distance(vector, [0,0])
        
    def normalize(self, vector):
        # Returns the given vector with it's magnitude scaled to one.
        magn = self.magnitude(vector)
        direction = self.get_direction(vector)
        if magn == 0: normalized = [0, 0]
        else: normalized = [vector[0]/magn, vector[1]/magn]
        return normalized
   
    def set_vector(self, p1, p2):
        # Create a two-dimensional vector from 
        # coordinates 'p1' to coordinates 'p2'.
        vector = []
        vector.append(p2[0]-p1[0]) # delta x
        vector.append(p2[1]-p1[1]) # delta y
        return vector
    
    def get_direction(self, vector):
        # Returns the direction of the given vector between 0 and 360 degrees.
        magn = self.magnitude(vector)
        if magn == 0:
            return None
        elif vector[1] >= 0:
            return math.degrees(math.acos(vector[0]/magn))
        else:
            return 360-math.degrees(math.acos(vector[0]/magn))

    def check_angle(self, v_original, v_new):
        # This method returns the angle between vectors 'v_original' and 'v_new'.
        # The angle is calculated starting from v_original and is given between
        # -180 and 180 degrees.
        
        dir1 = self.get_direction(v_original)
        dir2 = self.get_direction(v_new)
        if dir1==None or dir2==None: print('oh dear lord')
        delta = dir2-dir1
        
        if abs(delta) <= 180: return delta
        elif delta > 0: return delta-360
        else: return delta+360

    def is_ahead(self, target_location):
        # Return True if 'target_location' is ahead of the radar location.
        
        v_target = self.set_vector(self.location, target_location)
        v_target[1] = -v_target[1]       
        angle_between = self.check_angle(self.direction, v_target)
            
        if abs(angle_between) <= 90: return True
        else: return False
    
    def is_behind(self, target_location):
        # Return True if 'target_location' is behind the radar location.
        
        ahead = self.is_ahead(target_location)
        
        if ahead: return False
        else: return True
    
    def get_yielding_distance(self, angle, own_length):
        # Define the distance the vehicle must stay back from
        # an intersection with no possibility of blocking it.
        # Staying at this distance is more productive than just
        # getting as close as possible and then stopping to wait.
        # The angle between the intersecting routes and the vehicle
        # length are enough to determine a polite distance between
        # the yielding vehicle and the location of intersection.
                                
        base = own_length/2
        x = Constants.BLOCK_SIZE
        
        if angle > 0:
            if angle < 32: addition = 7/10*x
            elif angle < 41.625: addition = 5/16*x
            elif angle < 65: addition = x/3
            elif angle < 100: addition = x/2
            elif angle < 140: addition = 8/21*x
            else: addition = 5/12*x
        else:
            angle = abs(angle)
            if angle < 32: addition = 11/15*x
            elif angle < 41.625: addition = 4/5*x
            elif angle < 65: addition = 4/5*x
            elif angle < 95: addition = 2/3*x
            elif angle < 111: addition = 7/16*x
            else: addition = 3/5*x
            return base + addition
            
        return base + addition

    def get_blocking_distance(self, angle, own_length, target_width, ahead):
        # Define the minimum distance the vehicle must stay back
        # from an intersection without blocking it. The intersection
        # is the location where the paths overlap, the angle between
        # the paths is enough to define the minimum safe distance.
        # The bigger the vehicles, the further away they have to be.
        
        x = Constants.BLOCK_SIZE
        base = own_length/2 + target_width/2
        
        if ahead:
            if angle > 0:
                if angle < 32: addition = x/1.7
                elif angle < 41.625: addition = x/20
                elif angle < 65: addition = x/15
                elif angle < 95: addition = x/15
                elif angle < 111: addition = x/5
                elif angle < 140: addition = x/10
                else: addition = x/5.5
            else:
                angle = abs(angle)
                if angle < 32: addition = x/3
                elif angle < 41.625: addition = x/10
                elif angle < 65: addition = x/10
                elif angle < 95: addition = x/15
                elif angle < 111: addition = x/7
                elif angle < 140: addition = x/3
                else: addition = x/5.5
        else: # behind
            if angle > 0:
                if angle < 32: addition = 0
                elif angle < 41.625: addition = x/20
                elif angle < 65: addition = 0
                elif angle < 95: addition = x/5
                elif angle < 111: addition = x/7
                elif angle < 140: addition = x/3.5
                else: addition = x/5.5
            else:
                angle = abs(angle)
                if angle < 32: addition = x/3
                elif angle < 41.625: addition = x/10
                elif angle < 65: addition = x/10
                elif angle < 95: addition = x/12
                elif angle < 111: addition = x/7        
                elif angle < 140: addition = x/4
                else: addition = x/6
            
        return base + addition
    
    def get_collision_distance(self, observer, observed, angle):
        # Define the the minimum distance between vehicles
        # 'observer' and 'observer' without having them overlap.
        
        org_dir = abs(observed.get_rotation())
        if org_dir > 180: org_dir -= 180
        
        targ_dir = abs(observer.get_rotation())
        if targ_dir > 180: targ_dir -= 180
        
        angle_between = abs(org_dir-targ_dir)
        if angle_between > 90: angle_between -= 90
        
        org_length, org_width = observer.length, observer.width
        targ_length, targ_width = observed.length, observed.width
                
        view_angle = math.degrees(math.atan(org_width/org_length))
        
        # The safe distance between the center points 
        # depends heavily on the directions they are facing.
        if angle_between <= view_angle:
            dist = org_length/2+targ_length/2
        elif angle_between <= 40:
            dist = org_length/2+0.85*targ_length/2
        elif angle_between <= 60:
            dist = org_length/2+0.70*targ_length/2
        elif angle_between <= 80:
            dist = org_length/2+0.65*targ_length/2
        else:
            dist = org_length/2+targ_width/2+Constants.BLOCK_SIZE/20
        
        return dist + Constants.BLOCK_SIZE/20
    
    def distance_to_cross(self, org_posi, location, angle, ahead):
        # Return the safe distance to location where paths intersect.
        
        base = self.distance(org_posi, location)
        x = Constants.BLOCK_SIZE
        angle = abs(angle)
        addition = 0
        
        if angle < 32:
            if ahead: addition = -x/3.5
        elif angle < 41.625:
            if ahead: addition = -x/10
        elif angle < 140: pass
        else: addition = -x/2.5
        
        return base + addition
     
    def intersects(self, own_coordinates, target_coordinates, cross_location):
        # Return True as the first returnable if 'own_coordinates' intersect with
        # 'target_coordinates'. The location of intersection is also returned as well 
        # as the angle between the routes if they exist.
        
        def get_first_indexes():
            # If 'cross_location' doesn't equal None, paths 'own_coordinates' and
            # 'target_coordinates' have been found crossing before near location
            # 'cross_location'. This information can be used to find the first indexes
            # in 'target_coordinates' and in 'cross_location' to save time and energy.
            # The indexes themselves are not returned, since the the relevant coordinates
            # change while the vehicle moves, the crossing location can remain unchanged
            # for long periods of time though.
            
            start_i, start_j = 0, 0
                
            while own_coordinates[start_i] != cross_location:
                start_i += 1
                if start_i == limit_i:
                    # Doesn't work every time.
                    start_i = 0
                    break
                
            if start_i != 0:
                own_start_location = own_coordinates[start_i]
                while self.distance(own_start_location, \
                    target_coordinates[start_j]) > min_distance:
                    # When the crossing location was found last time,
                    # the coordinates must have been within the distance
                    # of 'identical_distance' from each other.
                    start_j += 1
                    if start_j == limit_j:
                        # Doesn't work every time either.
                        start_j = 0
                        break
                    
            return start_i, start_j
                 
        def identical_paths(starting_from):
            # If two consecutive coordinate pairs are within 'identical_distance'
            # of each other, the paths are considered identical at those indexes.
            
            test_i, test_j = starting_from
            idd = identical_distance
                        
            if self.distance(own_coordinates[test_i+2], target_coordinates[test_j+1]) <= idd: return True
            elif self.distance(own_coordinates[test_i+3], target_coordinates[test_j+1]) <= idd: return True
            elif self.distance(own_coordinates[test_i+1], target_coordinates[test_j+2]) <= idd: return True
            elif self.distance(own_coordinates[test_i+2], target_coordinates[test_j+2]) <= idd: return True
            elif self.distance(own_coordinates[test_i+3], target_coordinates[test_j+2]) <= idd: return True
            elif self.distance(own_coordinates[test_i+1], target_coordinates[test_j+3]) <= idd: return True
            elif self.distance(own_coordinates[test_i+2], target_coordinates[test_j+3]) <= idd: return True
            elif self.distance(own_coordinates[test_i+3], target_coordinates[test_j+3]) <= idd: return True
            else: return False
                
        min_distance = Constants.BLOCK_SIZE/10
        identical_distance = Constants.BLOCK_SIZE/100
        start_i, limit_i = 0, len(own_coordinates)-4
        start_j, limit_j = 0, len(target_coordinates)-4
        
        if cross_location: start_i, start_j = get_first_indexes()
        
        for i in range(start_i, limit_i-4):
            for j in range(start_j, limit_j):
                if self.distance(own_coordinates[i], target_coordinates[j]) < min_distance:
                    # The routes intersect.
                    cross_point = own_coordinates[i]
                    if identical_paths((i, j)):
                        # The routes intersect due to being at least partially identical.
                        return False, cross_point, None
                    v_current = self.set_vector(own_coordinates[i], own_coordinates[i+1])
                    v_nearby = self.set_vector(target_coordinates[j], target_coordinates[j+1])
                    angle_between = self.check_angle(v_current, v_nearby)
                    if angle_between < 0 or abs(angle_between) > 150:
                        # The nearby vehicle is approaching from the right.
                        return True, cross_point, angle_between
                    # The nearby vehicle is approaching from the left.
                    return False, cross_point, angle_between
        # This vehicle doesn't have an intersecting route with the observed one.
        return False, None, None 

