

import math
from path import Pathh
from radar import Radar
from constants import Constants


class Vehicle():
    
    '''
    This is the vehicle that is visualized by a VehicleGraphicsModel-
    object on the map. A vehicle can be a sedan, a mini van or a pickup
    truck. Every vehicle has a Radar- and a Pathh-object as an
    attribute to help it navigate across the map. Each method and
    attribute exists to define the vehicle's movement and characteristics.
    The vehicle's "brains" is the drive-method, which in it's turn
    calls the appropriate methods. The update-method updates the
    radar, path and everything closely related to the vehicle.
    Vehicles navigate across the map based on their path coordinates.
    If there are no intersecting paths, the vehicle will drive with no
    concern of it's surroundings. If there are intersecting paths, 
    attributes 'self.slows', 'self.yields', 'self.commited' and 'self.blocked' 
    will define what the vehicle will do. The radar will spot all the relevant
    targets for the vehicle, check 'self.update' for further information.
    '''
    
    def __init__(self, vehicle_type, color='White'):
        # Not all relevant attributes are initialized
        # here, check 'self.spawn' for further information.
        self.type = vehicle_type
        self.position = [None, None]
        self.velocity = [None, None]
        self.rotation = None
        self.color = color
        self.path = Pathh(self.type)
        self.radar = Radar()
        # These attributes define the vehicle status,
        # check 'self.update_blocking', 'self.set_limit'
        # and 'self.update_yielding' for further information.
        self.slows = False
        self.yields = False
        self.blocked = False
        self.rushing = 0
        # A leading vehicle and it's last known location
        self.to_follow = [None, None] 
        self.limit = None
        # mass, speed, turning radius, length,
        # width, maximum and preferred speeds,
        # maximum and preferred amounts of force
        self.set_parameters()
        # These will list other vehicles.
        self.blocking, self.to_ignore = [], []
        # The next two are for calling 'heavy' 
        # functions periodically, but not each cycle.
        self.counter, self.pause = 0, 200 # 200 milliseconds
        # True when the goal has been reached.
        self.done = False
            
    def spawn(self):
        # Spawn the vehicle on the map, all the necessary
        # information for this is found in 'self.path.spawn'.
        
        (x, y, initial_rotation) = self.get_path().get_spawn()
        v_x = 0.02*math.cos(math.radians(initial_rotation))
        v_y = 0.02*math.sin(math.radians(initial_rotation))
        self.position = [x, y]
        self.velocity = [v_x, v_y]
        self.rotation = initial_rotation
        
        # This refers to trying to get through a traffic jam.
        self.tried_already = False
                
        # Locations where this vehicle's path intersects with the
        # path of another vehicle. The angle between the routes and 
        # the location where the vehicle was found in are also listed.
        self.intersections = dict()
        
        # Same as the one above, but only locations where
        # this vehicle should yield by default are listed.
        self.yield_coords = dict()
        
        # Call the update function once to give the vehicle
        # all the required attributes, this will not move the
        # vehicle like the drive method does the drive method.
        self.update()
            
    def get_position(self):
        # The initial position and velocity are not determined upon constructing,
        # but when the spawn-point is set in the Pathhh-object (self.path.set_spawn()).
        # Check self.spawn() for further information.
        return self.position

    def get_speed(self):
        # Return the velocity magnitude.
        return math.sqrt(math.pow(self.velocity[0],2)+math.pow(self.velocity[1],2))

    def get_rotation(self):
        # Get the velocity direction in degrees counting from the positive
        # x-axis counter clockwise. If the velocity equals zero, the direction
        # the vehicle was traveling before stopping is given.
        return self.rotation

    def get_path(self):
        # The Pathh-object will contain all the vehicle's path coordinates
        # and the information to determine which of these are relevant.
        return self.path
    
    def get_radar(self):
        # The Radar-object keeps track of the rest of the vehicles in the city.
        # The radar also helps the vehicle with numerous vector operations.
        return self.radar
    
    def get_relevant_coordinates(self):
        # Return the coordinates that are considered relevant, typically these are
        # the coordinates of the closest four path pieces. Coordinates that have
        # been passed already are not taken to account.
        return self.relevant
    
    def get_scene_rotation(self):
        # The rotation in the graphics scene starts from the 
        # positive x-axis and grows clock wise. In this class,
        # the angle grows counter-clockwise and the origin is in 
        # the bottom-left corner unlike in the graphics scene.
        return 450 - self.rotation
    
    def is_blocked(self):
        # Return True if this vehicle is physically blocked.
        return self.blocked
        
    def is_blocking(self, vehicle):
        # Return True if the given vehicle is in the list
        # of vehicles that this vehicle is currently blocking.
        return vehicle in self.blocking
            
    def is_commited(self):
        # Return True is this vehicle has decided to cross an intersection
        # despite having to yield to another vehicle. Usually this
        # is the result of not wanting to block said intersection.
        return self.commited
    
    def is_rushing(self):
        # Return True if this vehicle is in rush hour-mode.
        return self.rushing
    
    def change_mode(self):
        # Switch between rush- and casual-mode.
        self.rushing = 1 - self.rushing
        self.set_default_speeds()
        self.set_default_forces()
        
    def finish(self):
        # This method is called when this vehicle reaches it's goal.
        self.done = True
    
    def is_done(self):
        # When this equals True, the vehicle has reached it's 
        # goal and is no longer relevant for the simulation.
        return self.done
    
    def drive(self):
        # This is the only periodically called method by the
        # CityCenter-object. After this vehicle has been spawned, it's
        # ready to drive. Most of the work is done in 'self.update', but
        # this method decides how the velocity is affected by that outcome.
        
        # Update everything that needs to be updated.
        self.update()
        
        # Keep the vehicle moving.
        self.run()
        
        offroad, turn, cruise = self.default_speeds
                         
        # Here are the set of rules that determine the vehicle's behavior.
        if self.yields or self.is_blocked():
            # Stop and wait until the road is clear.
            cruise = 0
            turn = 0
            offroad = 0
        elif self.slows:
            # Prepare to yield.
            cruise = cruise/2
            turn = 2*turn/3
            offroad = 2*offroad/3
        
        if self.limit:
            # There is a vehicle close ahead,
            # adjust the speed accordingly.
            cruise = min(cruise, self.limit)
            turn = min(turn, self.limit)
            offroad = min(offroad, self.limit)
            
        if not self.on_path():
            # Get back on the road.
            self.seek(offroad)
        elif not self.on_course():
            # Try to stay on the road.
            self.regain_course(turn, cruise)
        else:
            # No correction needs to be done, drive "freely".
            self.achieve_speed(cruise)
    
    def update(self):

        # 'self.rotation' is set for each cycle 
        # and then used in numerous methods.
        self.update_rotation()
        
        # Let the radar know where the vehicle is going.
        self.get_radar().set_radar(self.get_position(), self.get_rotation())
        
        # Check if the vehicle has moved enough to consider
        # another set of coordinates the most relevant.
        self.update_path_progress()
        
        # Choose the relevant coordinates out of all coordinates according
        # to the path progress. This is then used in several methods.
        self.set_relevant_coordinates()
        
        # Observe the surrounding vehicles.
        self.set_intersections()
        
        # Default values
        self.limit = None
        self.slows = False
        self.yields = False
        self.commited = False
        self.blocked = False
        self.blocking = []
        
        # Set an up limit to the vehicle speed 
        # considering the leading vehicle. 
        if self.to_follow[0]: self.set_limit()
        
        # Check if there are any vehicles physically blocking
        # this one or if this one is blocking any other vehicle.
        if len(self.intersections): self.update_blocking()
        
        # Prepare to adjust the velocity according to the traffic rules.
        if not self.rushing and len(self.yield_coords): self.update_yielding()
            
        # Try to solve a traffic jam situation if possible.
        if not self.is_blocked(): self.solve_standstill()
        
        if self.blocked:
            # This attribute may become True if a bad traffic jam is formed.
            self.tried_already = False
        
        # The counter grows by 1000 each active
        # second and is reset after reaching 1000.
        self.counter += int(Constants.TIME_STEP)
        
    def run(self):
        # Keep the vehicle running, if this is suddenly not called it will
        # appear as if the vehicle gets stopped by an inhumanely large force.
        self.position[0] += Constants.BLOCK_SIZE*self.scale(self.velocity[0])/100
        self.position[1] -= Constants.BLOCK_SIZE*self.scale(self.velocity[1])/100
    
    def update_rotation(self):
        # This is done to remember the vehicle direction. When the speed equals
        # zero, it is impossible to calculate the direction using the velocity vector.
        if self.get_speed() <= 0.01:
            return
        if self.velocity[1] >= 0:
            self.rotation = math.degrees(math.acos(self.velocity[0]/self.get_speed()))
        else:
            self.rotation = 360-math.degrees(math.acos(self.velocity[0]/self.get_speed()))
               
    def proximity(self):
        # Return the coordinates of the four closest path pieces determined by 'self.path.progress'.
        # If we are close enough to reaching the goal, return as many coordinates as possible.
        
        all_coordinates = self.get_path().get_coordinates()
        index, sub_index = self.get_path().get_progress()
        up_limit = self.get_path().limit
        
        if index+3 <= up_limit:
            return all_coordinates[index]+all_coordinates[index+1]+\
                all_coordinates[index+2]+all_coordinates[index+3]
        elif index+2 <= up_limit:
            return all_coordinates[index]+all_coordinates[index+1]+\
                all_coordinates[index+2]
        else:
            return all_coordinates[index]+all_coordinates[index+1]
    
    def update_path_progress(self):
        # This method decides when it's okay to increase the path progress (self.path.progress).
        # The path progress is used to decide which coordinates are relevant to the vehicle,
        # check self.get_relevant_coordinates() for further information.
        
        posi = self.get_position()
        own_radar = self.get_radar()
        own_path = self.get_path()
        all_coordinates = own_path.get_coordinates()
        index, sub_index = own_path.get_progress()
        up_limit = own_path.limit
        nearby_coordinates = self.proximity()
         
        if index+1 == up_limit:
            # The vehicle is starting to be very close to the end, so this is a good time to
            # start observing whether it is within 'r' distance from the goal point. When the goal 
            # point is within the distance, the CityCenter-object will stop calling the drive() method.
            
            r = Constants.BLOCK_SIZE/2
            if own_radar.distance(posi, own_path.goal) <= r:
                # The simulation will end for this vehicle.
                self.finish()

            close = own_radar.distance(posi, nearby_coordinates[sub_index])
            next = own_radar.distance(posi, nearby_coordinates[sub_index+1])
            
            while next < close:
                own_path.update()
                sub_index = own_path.get_progress()[-1]
                close = own_radar.distance(posi, nearby_coordinates[sub_index])
                next = own_radar.distance(posi, nearby_coordinates[sub_index+1])
                
            # The path progress must not grow anymore ('sub_progress' can though).
            return
        
        past_location = nearby_coordinates[0]
        future_location = nearby_coordinates[-1]
        behind = own_radar.distance(posi, past_location)
        ahead = own_radar.distance(posi, future_location)
        
        if ahead < behind:
            own_path.update(next_piece=True)
            nearby_coordinates = self.proximity()
        
        close = own_radar.distance(posi, nearby_coordinates[sub_index])
        next = own_radar.distance(posi, nearby_coordinates[sub_index+1])
        
        while next < close:
            # Loop until we have the index of the closest coordinates.
            own_path.update()
            sub_index = own_path.get_progress()[-1]
            close = own_radar.distance(posi, nearby_coordinates[sub_index])
            next = own_radar.distance(posi, nearby_coordinates[sub_index+1])
    
    def set_relevant_coordinates(self):
        # Define the relevant coordinates for the vehicle.
        
        relevant = self.proximity()
        sub_index = self.get_path().get_progress()[-1]
        
        # Remove all the coordinates that are further
        # than self.path.count/2 dots behind the vehicle.
        while sub_index >= int(self.get_path().count/2):
            relevant.pop(0)
            sub_index -= 1
            
        self.last = relevant[-1]
        self.first = relevant[0]
            
        self.relevant = relevant
    
    def set_intersections(self):
        # Set all the dangerous locations, e.g. the locations where this
        # vehicle's path intersects with the path of another vehicle.
        
        # We can't afford to do this every cycle. This method is paused
        # for self.pause amount of milliseconds between each active cycle.
        if self.counter%self.pause: return
        
        if self.counter >= 1000:
            # Reset every second.
            self.counter = 0
            self.to_ignore = []
        
        own = self.get_relevant_coordinates()
        radar = self.get_radar()
        checked = []
                
        for vehicle in radar.in_radar():
            
            check = False
            cross_location = None
            spotted_now = vehicle.get_position()
            
            if vehicle in self.to_ignore: 
                check = True
            elif vehicle == self.to_follow[0]:
                last_spotted = self.to_follow[1]
                if not radar.distance(last_spotted, spotted_now):
                    check = True
            elif vehicle in self.intersections.keys():
                cross_location, angle, last_spotted = self.intersections[vehicle]
            
            if not check:
                
                obsv = vehicle.get_relevant_coordinates()
                has_to_yield, coords, angle = radar.intersects(own, obsv, cross_location)
                
                if has_to_yield:
                    relevant_dist = Constants.BLOCK_SIZE/1.5
                    if vehicle != self.to_follow[0]:
                        if vehicle.to_follow[0] != self:
                            if radar.is_ahead(coords):
                                # This vehicle prepares to yield to 'vehicle'.
                                self.yield_coords[vehicle] = (coords, angle, spotted_now)
                                self.intersections[vehicle] = (coords, angle, spotted_now)
                            elif radar.distance(self.get_position(), vehicle.get_position()) <= relevant_dist:
                                # If the location is behind, but within the distance 
                                # of 'relevant_distance', it still counts.
                                self.intersections[vehicle] = (coords, angle, spotted_now)
                                self.yield_coords[vehicle] = (coords, angle, spotted_now)
                    else:
                        # This vehicle and the one it's following (or the other way around!) 
                        # are starting to go their own separate ways, no need to yield.
                        dist = radar.distance(self.to_follow[0].get_position(), coords)
                        if dist >= relevant_dist:
                            self.to_follow = [None, None]
                elif angle:
                    # Doesn't have to yield, but the routes intersect. There is a possibility
                    # that 'vehicle' blocks this vehicle, so it can't always be ignored.
                    self.intersections[vehicle] = (coords, angle, spotted_now)
                elif coords:
                    # If 'angle' equals None but 'coords' exist, the paths are at least
                    # partially identical and therefore this vehicle is following 'vehicle'
                    if radar.is_ahead(coords):
                        # Only vehicles ahead count.
                        if not self.to_follow[0]:
                            self.to_follow = [vehicle, spotted_now]
                        elif vehicle == self.to_follow[0]:
                            # The only vehicle in 'visible' (so far!)
                            # that shares the same path with this vehicle.
                            self.to_follow = [vehicle, spotted_now]
                        else:
                            # If this vehicle's path is shared with more than one other
                            # vehicle in 'visible', follow the closest one of these.
                            own_posi = self.get_position()
                            new = self.get_radar().distance(own_posi, vehicle.get_position())
                            org = self.get_radar().distance(own_posi, self.to_follow[0].get_position())
                            if new < org:
                                self.to_follow = [vehicle, vehicle.get_position()]
                else:
                    self.to_ignore.append(vehicle)
                    
            checked.append(vehicle)
                
        # Keep the the leading vehicle for as long as it's relevant.
        if not self.to_follow[0] in checked: self.to_follow = [None, None]
    
    def set_limit(self):
        # Set a limit to this vehicle's speed considering the
        # distance between this vehicle and the one being followed.
        
        x = Constants.BLOCK_SIZE
        own_posi = self.get_position()
        leading_vehicle, last_spotted = self.to_follow
        # Value 'ahead' represents the distance between 
        # this vehicle and the one being followed.
        ahead = self.get_radar().distance(own_posi, last_spotted)
        # The bigger the vehicles, the further
        # away their center points have to be.
        ahead -= self.length/2+leading_vehicle.length/2+x/50
        reference = leading_vehicle.get_speed()
        
        if ahead <= x:
            if ahead <= 0.7*x:
                if ahead <= 0.4*x:
                    if ahead <= 0.2*x:
                        if ahead <= 0.1*x:
                            # Don't get any closer than this.
                            self.blocked = True
                        else: self.limit = max(0.7*reference, 2.5)
                    else: self.limit = max(1.0*reference, 3.0)
                else: self.limit = max(1.2*reference, 6.5)
            else: self.limit = max(1.5*reference, 8.0)
        
    def update_blocking(self):
        # Update 'self.blocking' and 'self.blocked' to the current situation, 
        # 'self.blocked' may already equal True. When 'self.blocked' equals True,
        # there is no room to move any further and therefore the vehicle will stop.
        # There is a chance that 'self.yields' becomes True as well, but if so, it
        # will be due to another vehicle breaking the traffic rules (the right hand rule).
        
        x = Constants.BLOCK_SIZE
        own_posi = self.get_position()
        
        # For every location this vehicle's path intersects with
        # another one, there is a possibility that the path is blocked.
        for vehicle in self.intersections.keys():
            
            location, angle, last_spotted = self.intersections[vehicle]
            ahead = self.get_radar().is_ahead(location)
            blocking_dist = self.get_radar().get_blocking_distance( \
                angle, self.length, vehicle.width, ahead)
            if self.get_radar().distance(own_posi, location) <= blocking_dist:
                
                if not vehicle.is_blocking(self):
                    # This vehicle is close enough to a location of intersection to not let
                    # the other one get through. It's crucial that both vehicles don't think
                    # they are blocking the other one, otherwise they would both stop in place
                    # place and not move anywhere. It's enough that one vehicle will take care
                    # of the stopping.
                    self.blocking.append(vehicle)
            
            if vehicle.is_blocking(self):
                if self.get_radar().is_ahead(location):
                    stop_dist = self.get_radar().get_yielding_distance(angle, self.length)
                    if self.get_radar().distance(own_posi, location) <= stop_dist:
                        # Let the crossing vehicle finish it's business first.
                        self.yields = True
                        obsv_ahead = vehicle.get_radar().is_ahead(location)
                        dist_to_cross = self.get_radar().distance_to_cross(own_posi, location, angle, obsv_ahead)
                        dist_to_trgt = self.get_radar().distance(own_posi, vehicle.get_position())
                        if not self.is_blocking(vehicle):
                            col_dist = self.get_radar().get_collision_distance(self, vehicle, angle)
                            if min(dist_to_cross, dist_to_trgt) <= col_dist:
                                # The observed vehicle is blocking the intersection
                                # and this one is close enough to get blocked by it.
                                self.blocked = True
                
            if vehicle.is_commited():
                if self.get_radar().is_ahead(location):
                    if self.get_radar().distance(self.get_position(), location) > self.length/2:
                        stop_dist = self.get_radar().get_yielding_distance(angle, self.length)
                        if self.get_radar().distance(own_posi, location) <= stop_dist:
                            # Let the other vehicle get through.
                            self.yields = True
        
    def update_yielding(self):
        # Update 'self.slows' and 'self.yields' to the current situation.
        # A vehicle typically stops when it has to yield. There are a few
        # exceptions to this though. When 'self.slows' equals True, the
        # vehicle speed drops as a preparation to yielding.
        
        on_the_way = False
                
        for vehicle in self.yield_coords.keys():
            # This vehicle will stay approximately within 'stop_dist'
            # from the location where the paths intersect. This way, this
            # vehicle doesn't just mindlessly charge into the intersection,
            # but waits at a polite distance until the road is clear.
            
            location, angle, last_spotted = self.yield_coords[vehicle]
            
            if self.get_radar().is_ahead(location):
                dist = self.get_radar().distance(self.get_position(), location)
                stop_dist = self.get_radar().get_yielding_distance(angle, self.length)
                if dist <= 1.5*stop_dist:
                    self.slows = True
                    if dist <= stop_dist:
                        if dist <= stop_dist-Constants.BLOCK_SIZE/10:
                            # Too close to the location of intersection.
                            on_the_way = True                            
                        else:
                            # There is enough space to stop and wait.
                            self.yields = True
        
        if on_the_way and not self.yields:
            # The only vehicles this one is supposed
            # to yield to are blocked by this one.
            # This vehicle commits to finishing the crossing
            # even if it should yield otherwise, stopping
            # in the middle of the road would cause more trouble.
            self.commited = True
            self.slows = False
            self.yields = False
    
    def solve_standstill(self):
        # Solve a standstill situation, e.g. a situation where every nearby
        # vehicle is not moving. A standstill is formed when several vehicles
        # approach the same intersection simultaneously and they all have  
        # either a vehicle to yield to, or are just physically blocked.
        
        blocker_count = 0
        
        for vehicle in self.get_radar().in_radar():
            if self.is_blocking(vehicle):
                blocker_count += 1
            if vehicle.is_blocking(self):
                if not self.tried_already:
                    # Don't make the situation any worse. As 'self.tried_already' becomes
                    # True, the vehicle will try diffusing a traffic jam a bit harder.
                    self.tried_already = True
                    return
            
        if not blocker_count:
            visible = []
            for vehicle in self.get_radar().in_radar():
                if self.get_radar().is_ahead(vehicle.get_position()):
                    visible.append(vehicle)
            vehicles_moving = len(visible)
            for vehicle in visible:
                if not vehicle.get_speed():
                    vehicles_moving -= 1
            if vehicles_moving:
                # Let the other vehicles 
                # finish their business first.
                return
            
        # Now is a good time to move,
        # initiate solving the situation.
        if self.yields: self.commited = True
        self.slows = False
        self.yields = False
        
    def on_path(self):
        # Return True if the vehicle position is inside the path's radius.
        
        posi = self.get_position()
        r = self.get_path().radius
        nearby = self.get_relevant_coordinates()
        for point in nearby:
            if self.get_radar().distance(posi, point) <= r:
                return True
        # If we get here, there is no coordinate pair in the vehicle's path 
        # within the the 'r' distance, therefore the vehicle is off path.
        return False
    
    def on_course(self):
        # Return True if the scaled velocity vector is pointing inside the path radius.
        
        magnitude = 25
        normalized = self.get_radar().normalize(self.velocity)
        x = self.get_position()[0] + magnitude*normalized[0]
        y = self.get_position()[1] - magnitude*normalized[1]
        headed = [x, y]
        # 'headed' is a coordinate pair directly in front of the vehicle, the distance 
        # from the vehicle'sfront is determined by the velocity direction and 'magnitude'.
        r = self.get_path().radius
        nearby = self.get_relevant_coordinates()
        # This is very similar to self.on_path().
        for point in nearby:
            if self.get_radar().distance(point, headed) <= r:
                return True                
        return False
    
    def seek(self, offroad_speed):
        # This method makes the car return to it's desired path. The
        # vehicle is considered off path when it's position is not within
        # the distance of 'self.path.radius' from any of the path coordinates.
        
        dist = math.inf
        posi = self.get_position()
        radar = self.get_radar()
        nearby = self.get_relevant_coordinates()
        
        self.achieve_speed(offroad_speed)
        
        # Stepper i is used to remember the 
        # index of the path's closest point.
        i = 0
        for point in nearby:
            new_dist = radar.distance(posi, point)
            if new_dist < dist:
                dist = new_dist
                closest = point
                i_0 = i
            i += 1
        
        x = Constants.PATH_RADIUS
        r = self.get_path().radius
        
        def get_approaching_angle():
            # Determine the approaching angle based on the distance from the path.
            # The further away the vehicle is, the steeper the approaching angle.
            if dist > r+3*x: return 90
            elif dist > r+2*x: return 75
            elif dist > r+1.5*x: return 60
            elif dist > r+x: return 40
            elif dist > r+0.5*x: return 20
            elif dist > r+0.25*x: return 10
            else: return 5
            
        appro_angle = get_approaching_angle()
                
        # This is a vector from the path's closest point to the vehicle location.
        v_positon = [self.get_position()[0]-closest[0], -(self.get_position()[1]-closest[1])]
        # This vector represents the path's direction two points forward from the closest point.
        v_path = [nearby[i_0+2][0]-closest[0], -nearby[i_0+2][1]+closest[1]]
        # This is the direction the vehicle is headed.
        v_direction = [math.cos(math.radians(self.get_rotation())), math.sin(math.radians(self.get_rotation()))]
        # This is the angle counting from the path direction to the vehicle direction.
        angle_between = radar.check_angle(v_path, v_direction)
        
        F_steer = self.default_forces[2] 
        
        if radar.check_angle(v_path, v_positon) >= 0:
            # The vehicle is on the left side of the path.
            appro_angle = -appro_angle
            if angle_between > appro_angle:
                if angle_between-1 < appro_angle: return
                else: self.steer_right(F_steer)
            elif angle_between < appro_angle:
                if angle_between+1 > appro_angle: return
                else: self.steer_left(F_steer)
        else:
            # The vehicle is on the right side of the path.
            if angle_between < appro_angle:
                if angle_between+1 > appro_angle: return
                else: self.steer_left(F_steer) 
            elif angle_between > appro_angle:
                if angle_between-1 < appro_angle: return
                else: self.steer_right(F_steer)
    
    def regain_course(self, turn_speed, cruise_speed):
        # This method will make the vehicle steer the correct way until it's back on course.
        
        dist = math.inf
        posi = self.get_position()
        radar = self.get_radar()
        nearby = self.get_relevant_coordinates()
        
        # Stepper 'i' is used to remember the index
        # of the path's closest coordinate pair.
        i = 0
        for point in nearby:
            new_dist = radar.distance(posi, point)
            if new_dist < dist:
                dist = new_dist
                #closest = point
                i_0 = i
            i += 1
        
        lead = 4
        start = i_0+lead
        end = i_0+int(lead/2)
        # This vector represents the path's direction 'lead' points forward from the closest point.
        v_path = [nearby[start][0]-nearby[end][0], -nearby[start][1]+nearby[end][1]]
        # This is the direction the vehicle is headed.
        v_direction = [math.cos(math.radians(self.get_rotation())), math.sin(math.radians(self.get_rotation()))]
        # This is the angle counting from the path direction to the vehicle direction.
        angle_between = radar.check_angle(v_path, v_direction)
        
        if abs(angle_between) <= 5: self.achieve_speed(cruise_speed)
        else: self.achieve_speed(turn_speed)
                
        F_steer = self.default_forces[2]
        
        if angle_between > 0:
            # The vehicle is steering too much to the left.
            self.steer_right(F_steer)
        elif angle_between < 0:
            # The vehicle is steering too much to the right.
            self.steer_left(F_steer)
    
    def scale(self, base_value):
        # Scales 'base_value' to the time step.
        return 0.01*base_value*Constants.TIME_STEP
    
    def steer_left(self, F):
        # This method is used alongside 'self.run()' to simulate steering to the left.

        if not self.get_speed(): 
            # Can not steer if the vehicle is not moving,
            # the vehicle can not rotate in place.        
            return
        
        angle = self.get_rotation()
        abs_speed = self.get_speed()
        
        # 'self.F_normal' amount of force can not be exceeded.
        F = min(F, self.F_normal)
        
        # Maximum amount of rotation added considering the steering radius:
        c_rotate_max = abs_speed/self.min_radius
        # The desired rotation:
        c_rotate_des = 100*F/(abs_speed*self.mass)
        # This makes sure the maximum amount is not exceeded.
        c_rotate = min(c_rotate_max, c_rotate_des)
        # The change is scaled considering 'Constants.TIME_STEP'.
        angle = angle + self.scale(c_rotate)
        
        # First quarter
        if self.velocity[0] >= 0 and self.velocity[1] >= 0:
            v_x = abs_speed*math.cos(math.radians(angle))
            v_y = math.sqrt(math.pow(abs_speed,2)-math.pow(v_x,2))
        # Second quarter
        if self.velocity[0] < 0 and self.velocity[1] >= 0:
            v_x = -abs_speed*math.sin(math.radians(angle-90))
            if angle <= 180: v_y = math.sqrt(math.pow(abs_speed,2)-math.pow(v_x,2))
            else: v_y = -math.sqrt(math.pow(abs_speed,2)-math.pow(v_x,2))
        # Third quarter    
        if self.velocity[0] < 0 and self.velocity[1] < 0:
            v_x = -abs_speed*math.cos(math.radians(angle-180))
            v_y = -math.sqrt(math.pow(abs_speed,2)-math.pow(v_x,2))
        # Fourth quarter
        if self.velocity[0] >= 0 and self.velocity[1] < 0:
            v_x = abs_speed*math.sin(math.radians(angle-270))
            if angle < 360: v_y = -math.sqrt(math.pow(abs_speed,2)-math.pow(v_x,2))
            else: v_y = math.sqrt(math.pow(abs_speed,2)-math.pow(v_x,2))
    
        self.velocity = [v_x, v_y]
    
    def steer_right(self, F):
        # Can not steer if the vehicle is not moving, the vehicle can not rotate in place.
        if not self.get_speed(): return
        # This is used alongside self.run() to simulate steering to the right.
        angle = self.get_rotation()
        abs_speed = self.get_speed()
        # self.F_normal can not be exceeded.
        F = min(F, self.F_normal)
        
        # The maximum amount of rotation added considering the steering radius:
        c_rotate_max = abs_speed/self.min_radius
        # The desired rotation according to 'F':
        c_rotate_des = 100*F/(abs_speed*self.mass)
        # This makes sure the maximum amount is not exceeded.
        c_rotate = min(c_rotate_max, c_rotate_des)
        # The change is scaled considering the Constants.TIME_STEP.
        angle = angle - self.scale(c_rotate)
    
        # First quarter
        if self.velocity[0] >= 0 and self.velocity[1] >= 0:
            v_x = abs_speed*math.cos(math.radians(angle))
            if angle >= 0: v_y = math.sqrt(math.pow(abs_speed,2)-math.pow(v_x,2))
            else: v_y = -math.sqrt(math.pow(abs_speed,2)-math.pow(v_x,2))
        # Second quarter
        if self.velocity[0] < 0 and self.velocity[1] >= 0:
            v_x = -abs_speed*math.sin(math.radians(angle-90))
            v_y = math.sqrt(math.pow(abs_speed,2)-math.pow(v_x,2))
        # Third quarter    
        if self.velocity[0] < 0 and self.velocity[1] < 0:
            v_x = -abs_speed*math.cos(math.radians(angle-180))
            if angle >= 180: v_y = -math.sqrt(math.pow(abs_speed,2)-math.pow(v_x,2))
            else: v_y = math.sqrt(math.pow(abs_speed,2)-math.pow(v_x,2))
        # Fourth quarter
        if self.velocity[0] >= 0 and self.velocity[1] < 0:
            v_x = abs_speed*math.sin(math.radians(angle-270))
            v_y = -math.sqrt(math.pow(abs_speed,2)-math.pow(v_x,2))
    
        self.velocity = [v_x, v_y]
    
    def achieve_speed(self, desired_speed):
        # This method makes the vehicle achieve the speed of 'desired_speed'.
                
        if self.get_speed() == desired_speed: return
        
        # Normal circumstances
        F_accelerate, F_brake, F_steer = self.default_forces
                
        if self.is_blocked() and len(self.blocking):
            # Tricky situation
            if self.on_path() and self.on_course():
                F_accelerate = 1.5*F_accelerate
                F_brake = 1.5*F_brake
        elif self.is_blocked():
            # Brake harder than usual.
            F_brake = 1.5*F_brake
        elif len(self.blocking):
            # Get out of the way quickly.
            if self.on_path() and self.on_course():
                F_accelerate = 1.5*F_accelerate
        
        def match_velocity():
            # When the actual speed is within the margin of 0.01
            # from the desired one, we might as well say they are equal.
            angle = self.get_rotation()
            v_x = desired_speed*math.cos(math.radians(angle))
            v_y = desired_speed*math.sin(math.radians(angle))
            self.velocity = [v_x, v_y]
                
        if self.get_speed() > desired_speed:
            if not self.get_speed()-0.01 < desired_speed:
                self.decelerate(F_brake)
            else: match_velocity()
        elif self.get_speed() < desired_speed:
            if not self.get_speed()+0.01 > desired_speed:
                self.accelerate(F_accelerate)
            else: match_velocity()
    
    def accelerate(self, F):
        # Grow the vehicle velocity magnitude in
        # small increments to simulate accelerating.
        
        if self.get_speed() == self.max_speed: return
        
        angle = math.radians(self.get_rotation())
        
        if not self.get_speed(): 
            # A minimal velocity to ensure the
            # vehicle starts driving the correct way.
            self.velocity[0] = 0.01*math.cos(angle)
            self.velocity[1] = 0.01*math.sin(angle)
        
        F = min(F, self.F_positive) # 'self.F_positive' can not be exceeded.
        acceleration = self.scale(F/self.mass)
        x_step = abs(acceleration*math.cos(angle))
        y_step = math.sqrt(pow(acceleration,2)-pow(x_step,2))
        
        # These are the velocity components when the
        # vehicle is traveling at the maximum speed.
        x_max = abs(self.max_speed*math.cos(angle))
        y_max = abs(self.max_speed*math.sin(angle))
        
        if abs(self.velocity[0])+x_step >= x_max:
            if self.velocity[0] > 0: self.velocity[0] = x_max
            else: self.velocity[0] = -x_max
            if self.velocity[1] > 0: self.velocity[1] = y_max
            else: self.velocity[1] = -y_max
        else:
            if self.velocity[0] > 0: self.velocity[0] = self.velocity[0] + x_step
            else: self.velocity[0] = self.velocity[0] - x_step
            if self.velocity[1] > 0: self.velocity[1] = self.velocity[1] + y_step
            else: self.velocity[1] = self.velocity[1] - y_step            
    
    def decelerate(self, F):
        # Bring the vehicle to a full stop if 
        # needed, very similar to 'self.accelerate'.
        
        if not self.get_speed(): return
        
        # 'self.F_negative' can not be exceeded.
        F = min(F, self.F_negative)
        acceleration = self.scale(F/self.mass)
        
        angle = math.radians(self.get_rotation())
        x_step = abs(acceleration*math.cos(angle))
        y_step = math.sqrt(pow(acceleration,2)-pow(x_step,2))
        
        if abs(self.velocity[0]) <= x_step: self.velocity[0] = 0
        elif self.velocity[0] > 0: self.velocity[0] = self.velocity[0] - x_step
        else: self.velocity[0] = self.velocity[0] + x_step
        
        if abs(self.velocity[1]) < y_step: self.velocity[1] = 0
        elif self.velocity[1] > 0: self.velocity[1] = self.velocity[1] - y_step
        else: self.velocity[1] = self.velocity[1] + y_step
    
    def set_parameters(self):
        # Different types of vehicles have differing parameters.
        
        def set_mass():
            if self.type == Constants.SEDAN:
                self.mass = 1000
            elif self.type == Constants.MINI_VAN:
                self.mass = 1500
            else:
                self.mass = 2000
            
        def set_size():
            base = Constants.VEHICLE_SIZE
            if self.type == Constants.SEDAN:
                self.width = 1.05*base
                self.length = self.width*1.85
            elif self.type == Constants.MINI_VAN:
                self.width = 1.1*base
                self.length = self.width*1.85
            else:
                self.width = 1.15*base
                self.length = self.width*2.1
            
        def set_max_speed():
            if self.type == Constants.SEDAN:
                self.max_speed = 50
            elif self.type == Constants.MINI_VAN:
                self.max_speed = 42
            else:
                self.max_speed = 30
    
        def set_min_radius():
            # This is a value to represent the minimum turn radius.
            # This is not a physical radius, but a proportion between the vehicle's
            # speed and the amount of rotation it can experience during each cycle.
            # The smaller the value, the tighter the curve.
            if self.type == Constants.SEDAN:
                self.min_radius = 0.40
            elif self.type == Constants.MINI_VAN:
                self.min_radius = 0.43
            else:
                self.min_radius = 0.50
        
        set_mass()
        set_size()
        set_max_speed()
        set_min_radius()
        self.set_default_speeds()
        self.set_default_forces()
    
    def set_default_speeds(self):
        # Off road-, turning- and cruising speeds for each vehicle type:
                
        if not self.is_rushing():
            if self.type == Constants.SEDAN:
                self.default_speeds = (4.4, 5.5, 6.0)
            elif self.type == Constants.MINI_VAN:
                self.default_speeds = (3.7, 4.0, 5.5)
            else:
                self.default_speeds = (3.5, 3.5, 4.5)
        else:
            if self.type == Constants.SEDAN:
                self.default_speeds = (4.6, 5.8, 6.4)
            elif self.type == Constants.MINI_VAN:
                self.default_speeds = (3.9, 4.3, 5.9)
            else:
                self.default_speeds = (3.7, 3.8, 4.9)
        
    def set_default_forces(self):
        # The amount of accelerating- braking- and steering force 
        # depend on the vehicle mode (rush versus no rush).
        
        # Maximum forces are equal amongst all vehicles.
        self.F_positive = 1500  # accelerating
        self.F_normal = 2000    # steering
        self.F_negative = 7000  # braking
                
        if not self.is_rushing():
            self.default_forces = (0.333*self.F_positive, 0.25*self.F_negative, 0.75*self.F_normal)
        else:
            self.default_forces = (0.666*self.F_positive, 0.5*self.F_negative, 0.9*self.F_normal)
        
        

