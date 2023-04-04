

import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.Qt import QGraphicsRectItem, QBrush, QColor, \
    QGraphicsEllipseItem, QLabel, QMessageBox, QProgressBar, QFont
from PyQt5.QtWidgets import QApplication
    
from city_center import CityCenter
from vehicle import Vehicle
from vehicle_graphics_model import VehicleGraphicsModel
from city_graphics_item import CityGraphicsItem
from constants import Constants
from random import randint


class GUI(QtWidgets.QMainWindow):
    
    '''
    This class sets the window that lets the user interact with the program.
    The window holds a vertical box layout, which has a layout of it's own.
    The main layout, 'self.layout', has a QGraphicsView- and a QGraphicsScene-
    object that are used for the traffic simulation itself. The vertical box
    layout within the main layout, 'self.sub_layout', will contain the rest
    of the widgets. These are 3 QLabels, 5 QPushButtons, 1 QProgressBar and 1
    QInputDialog. Two of the QLabels are empty and are used to keep the buttons
    in the middle of the sub layout. The third QLabel is for displaying the
    vehicle count, '4/7 Vehicles' for example. The progress bar does the same
    thing, but with a bar. When the vehicle count is at the maximum, the bar
    is full and so on. The buttons and the live input dialog allow the user to
    interact with the program. The first button enables a start/stop feature.
    When the second one is clicked, rush hour simulation starts and stops when
    it's clicked again. The third button allows the user to build a new window
    for a new map without closing the program. The new map size selected with a
    QInputDialog that pops on the screen after the 'new map' button is pressed.
    The same dialog is shown as the program is run for the first time. The next
    button enables a restart feature. When this button is clicked, the simulation
    will start over with the same map. The last button allows the user to exit 
    the program, just like clicking the cross button on the top right. The live
    input dialog lets the user set the preferred amount of vehicles on the map.
    The program runs with the help of a QTimer with a 10 millisecond time step.
    '''
    
    def __init__(self):
        
        super(GUI, self).__init__()
        self.setCentralWidget(QtWidgets.QWidget())
        self.layout = QtWidgets.QBoxLayout(1) # for graphics
        self.sub_layout = QtWidgets.QVBoxLayout() # for widgets
        self.layout.addLayout(self.sub_layout)
        self.centralWidget().setLayout(self.layout)
        
        # Let the user select the desired size for the city.
        size = self.select_size()
        if not size: return
        
        # The size has been selected,
        # construct the city layout.
        self.city = CityCenter(size)
        
        # Set the default parameters.
        self.frozen = 1 # stopped
        self.rush_hour = 0 # calm traffic
        self.erase = 0 # for deleting vehicles
        self.restart = False # only when asked
               
        # Set the window graphics and widgets.
        self.set_window()
        self.set_buttons()
        self.set_occupation_display()
        self.set_live_dialog()
        self.set_city_graphics()
        
        # A couple dictionaries to keep track 
        # of added graphics, each vehicle acts 
        # as a key for the corresponding items.
        self.vehicle_graphics = dict()
        self.path_items = dict()
        self.radar_areas = dict()
        
        # Start the clock.
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_everything)
        self.timer.start(Constants.TIME_STEP) # 10 milliseconds    
    
    def update_everything(self):
        # Keeps every vehicle moving and removes them when they are done.
        # Sets the desired paths visible/invisible in case of a mouse press event.
        # A restart is performed by clicking the 'restart' button.
        
        if not self.restart:
            
            # When the simulation is paused, the vehicles don't move.
            if not self.frozen:
                if len(self.city.get_vehicles()) < self.set_count:
                    self.spawn_vehicles()
                # 'expired' is a list of all the 
                # vehicles that have reached their goal.
                expired = self.city.update()
                if len(expired):
                    self.remove_items(expired) 
                # The graphics move only when the vehicles move.
                for graphicsitem in self.vehicle_graphics.values():
                    # Update the position and rotation of every VehicleGraphicsModel-object.
                    graphicsitem.update()
                        
            erased = None
            # If a vehicle is clicked, the result is instantaneous frozen or not.
            for graphicsitem in self.vehicle_graphics.values():
                if graphicsitem.flag_set():
                    vehicle = graphicsitem.owner                    
                    if not self.erase:
                        visible = graphicsitem.show_path()
                        dots = self.path_items[vehicle]
                        for dot in dots:
                            dot.setVisible(visible)
                        area = self.radar_areas[vehicle]
                        area.setVisible(visible)
                    else:
                        erased = vehicle
                    # Set the flag back to zero.
                    graphicsitem.set_flag()
            
            if erased:
                # There will be a maximum of 1 vehicles erased, the
                # user will not be fast enough to click 2 separate
                # vehicles during one cycle (10 milliseconds).
                self.remove_items([erased])
                self.city.remove_vehicles([erased])
        else:       
            # Remove all graphics from the scene.
            self.remove_items(self.city.get_vehicles())
            # Keep the same city, but start over.
            self.city.reset()
            # Reset the parameters.
            self.frozen = 0
            self.rush_hour = 0
            self.erase = 0
            self.restart = False
            # Set the original title.
            self.set_title()
            # Set the original vehicle count as well.
            self.set_count = self.default_casual_count
            self.vehicle_dialog.setIntValue(self.set_count)
            self.change_displayed_count()
            
    def spawn_vehicles(self):
        
        def another_one():
            # Add one vehicle to the simulation.
            
            if self.city.is_overheated():
                # There is no spot to place 
                # the vehicle at the moment.            
                return
            
            if self.city.is_at_full_capacity(self.rush_hour):
                # The map is at the maximum capacity,
                # can not place another vehicle.
                return
            
            # Choose the vehicle type randomly, but with bigger chance
            # of getting a sedan than a mini van and a bigger chance
            # of getting a mini van than a pickup truck.
            result = randint(1, 10)
    
            if result <= 2:
                # 20 percent chance
                vehicle_type = Constants.PICKUP_TRUCK
            elif result <= 5:
                # 30 percent chance
                vehicle_type = Constants.MINI_VAN
            else:
                # 50 percent chance
                vehicle_type = Constants.SEDAN
            
            # All colors are equally likely.
            colors = ['Green','Blue','Yellow','Turquoise','Violet','Gray','Black','Orange','White']
            color = colors[randint(0, len(colors)-1)]
            
            # Doesn't have a path yet, therefore doesn't
            # have a position, a velocity or a rotation either.
            vehicle = Vehicle(vehicle_type, color)
            
            # Determine where the vehicle is spawned 
            # and what kind of a path it will get.
            self.city.add_vehicle(vehicle)
            
            if self.rush_hour: 
                # Casual mode by default
                vehicle.change_mode()
            
            self.set_vehicle_graphics(vehicle)
            self.paint_radar(vehicle)
            self.draw_path(vehicle)
            self.change_displayed_count()
        
        current_amount = len(self.city.get_vehicles())
        desired_amount = self.set_count
        difference = desired_amount-current_amount
        
        if difference >= 3:
            # Don't let the vehicle count drop 
            # more than 2 from the desired amount.
            while difference > 2:
                another_one()
                difference -= 1
        elif difference == 2:
            # A vehicle won't be spawned immediately with a 100% chance, but
            # with the offset of 2 vehicles, another one will be shortly spawned.
            if self.rush_hour: another_one()
            elif randint(1, 250) == 250: another_one()
        else:
            # Same as the one above, but a new vehicle won't appear as fast.
            if self.rush_hour:
                if randint(1, 250) == 250: another_one()
            elif randint(1, 300) == 300: another_one()
        
    def remove_items(self, expired):
        # List 'expired' contains all of the vehicles whose graphics
        # (hull, wheels, windows, path) need to be removed from the scene.
                
        while expired != []:
            
            vehicle = expired.pop()
            # Remove all the expended VehicleGraphicsModel-objects first.
            graphicsitem = self.vehicle_graphics[vehicle]
            self.scene.removeItem(graphicsitem)
            
            for window in graphicsitem.get_windows():
                self.scene.removeItem(window)
            for wheel in graphicsitem.get_wheels():
                self.scene.removeItem(wheel)
                
            del self.vehicle_graphics[vehicle]
                
            # Take care of the respective paths and radars as well.
            for dot in self.path_items[vehicle]:
                self.scene.removeItem(dot)
            del self.path_items[vehicle]
            
            self.scene.removeItem(self.radar_areas[vehicle])
            del self.radar_areas[vehicle]
            
        # Change the displayed vehicle amount accordingly.
        self.change_displayed_count()
        
    def set_title(self):
        # The window title is the result of a couple of parameters.
        
        first = 'Traffic simulation'
        size = self.city.get_dimensions()
        second = '/'+str(size)+'x'+str(size)
        
        if self.rush_hour: third = '/Rush hour'
        else: third = '/Casual'
            
        if self.frozen: fourth = '/Stopped'
        else: fourth = ''
            
        if self.erase: fifth = '/Erase'
        else: fifth = ''
        
        description = first+second+third+fourth+fifth
        
        self.setWindowTitle(description)
        
    def change_displayed_count(self, new_limit=False):
        # Change what is displayed on the vehicle bar
        # and the vehicle label on the bottom right.
        
        if not new_limit:
            # A number of vehicles have been added or removed,
            # change the displayed amount of vehicles by that much.
            new_count = len(self.city.get_vehicles())
            max_count = self.city.get_maximum(self.rush_hour)
            description = '     '+str(new_count)+'/'+str(max_count)+' Vehicles     '
            self.vehicle_label.setText(description)
            
            if new_count > max_count:
                self.vehicle_bar.setValue(max_count)
                bold_font = QFont()
                bold_font.setBold(1)
                self.vehicle_label.setFont(bold_font)
            else:
                regular_font = QFont()
                regular_font.setBold(0)
                self.vehicle_label.setFont(regular_font)
                self.vehicle_bar.setValue(new_count)
        else:
            # The user has pressed the 'rush hour'-button, 
            # this means that the map capacity has changed.
            # Rush hour mode allows more vehicles to enter the map.
            if self.rush_hour: self.set_count = self.default_rush_count
            else: self.set_count = self.default_casual_count
            self.vehicle_dialog.setIntValue(self.set_count)
            
            count = len(self.city.get_vehicles())
            new_max_count = self.city.get_maximum(self.rush_hour)
            description = '     '+str(count)+'/'+str(new_max_count)+' Vehicles     '
            self.vehicle_label.setText(description)
            self.vehicle_dialog.setIntRange(1, new_max_count)
            self.vehicle_bar.setRange(0, new_max_count)
            
            if count > new_max_count:
                self.vehicle_bar.setValue(new_max_count)
                bold_font = QFont()
                bold_font.setBold(1)
                self.vehicle_label.setFont(bold_font)
            else:
                self.vehicle_bar.setValue(count)
        
    def select_size(self):
        # Let the user decide how big of a city is built. If
        # the first time fails, the user will be shown an error 
        # message and will be given a chance to try again.
        
        size = self.set_dialog(first_time=True)
        
        # This is the first thing the user will see this dialog
        # and can be reused if a new CityCenter-object is built.
        if size: return size
        
        def failure_message():
            # Failed to get a suitable value for city dimensions.
            
            # Display a message before terminating, or give the user one
            # last chance to give a value for the city size in case he/
            # she had unintentionally rejected the previous input dialog.
            msg_box = QMessageBox()
            msg_box.setWindowTitle('Failure')
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setText('No dimensions given, failed to set up the traffic simulation.')
            msg_box.setInformativeText('Do you want to try again?')
            msg_box.setDetailedText('In order to set up the traffic simulation, an integer '+\
                'from 3 to 9 must be given. This value represents the map size, e.g. the '+\
                'edge length of the square-shaped layout. By clicking "Yes", the previous '+\
                'dialog will be shown again.')
            
            # Set the message box buttons.
            msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg_box.setDefaultButton(QMessageBox.No)
            
            return msg_box.exec_()
        
        ret = failure_message()
        
        if ret == QMessageBox.No:
            # The user intended to close the program.
            return None
        elif ret == QMessageBox.Yes:
            # The user has decided try again, display the same
            # input dialog that was seen before this message box.
            selected_size = self.set_dialog(first_time=True)
            if selected_size:
                # This time the dialog was successful.
                return selected_size
            else:
                # Failed again, the error message
                # won't be displayed another time.
                return None
    
    def set_dialog(self, first_time=False):

        def set_size(input): self.selected_size = input
                
        if first_time:
            # The information is acquired with the help of a QInputDialog-
            # object, the same dialog is re-used when a new layout is built.
            self.init_dialog = QtWidgets.QInputDialog()
            self.init_dialog.setWindowTitle('Set up')
            self.init_dialog.setLabelText('Set dimensions for the map.')
            self.init_dialog.setOkButtonText('Create')
            # Integers only
            self.init_dialog.setInputMode(QtWidgets.QInputDialog.InputMode.IntInput)
            self.init_dialog.setIntRange(3, 9)
            self.init_dialog.setIntValue(7)
            self.init_dialog.intValueSelected.connect(set_size)
            
            OK = self.init_dialog.exec_()
        else:
            # A functioning layout already exists, but
            # the user has decided to build a new one.
            # No need to set up a new QInputDialog-object.
            self.init_dialog.setLabelText('Set dimensions for the new map.')
            
            OK = self.init_dialog.exec_()
            
        # 'OK' will tell whether the 
        # dialog was successful or not.
        if OK:
            selected_size = self.selected_size
            self.selected_size = None
            return selected_size
        else: return None
    
    def set_window(self):
        # The window size depends on the map size (self.city.get_dimensions()).
        
        # Set the big window in the middle first.
        width = Constants.BLOCK_SIZE*self.city.get_dimensions()
        extra = 0.2*Constants.BLOCK_SIZE
        x, y = 1080*1.78-width-extra, 1080-width-4*extra
        self.setGeometry(int(x/2),int(y/2),int(width+extra/2+186),int(width+extra))
        size = self.city.get_dimensions()
        self.set_title() # hand-made method
        self.show()
        
        # The scene will hold all of the home made graphics.
        self.scene = QtWidgets.QGraphicsScene()
        self.scene.setSceneRect(0, 0, width, width)
        self.view = QtWidgets.QGraphicsView(self.scene, self)
        self.view.adjustSize()
        self.view.show()
        self.layout.addWidget(self.view)
        
        # Start building the layout on the right ('self.sub_layout').
        # Add an empty label to keep the relevant widgets centered.
        if self.city.get_dimensions() != 3:
            if self.city.get_dimensions() != 4:
                self.sub_layout.addWidget(QLabel())
    
    def set_buttons(self):
        # Set the buttons on the right hand side in 
        # self.sub_layout. A good number of tiny methods 
        # are defined here as well to keep things simple.
    
        def start():
            # start/stop
            self.frozen = 1 - self.frozen
            self.set_title()
                    
        # Pressing this button will start the simulation or pause it
        # depending on self.frozen. Initially, the simulation is paused.
        start_btn = QtWidgets.QPushButton("start/stop")
        start_btn.clicked.connect(start)
        start_btn.setMinimumSize(start_btn.sizeHint())   
        self.sub_layout.addWidget(start_btn)
        
        def change_simulation():
            # rush hour/calm
            self.rush_hour = 1 - self.rush_hour
            self.set_title()
            self.change_displayed_count(new_limit=True)
            for vehicle in self.city.get_vehicles():
                if self.rush_hour and not vehicle.is_rushing():
                    vehicle.change_mode()
                elif not self.rush_hour and vehicle.is_rushing():
                    vehicle.change_mode()
        
        # Switch between rush hour/calm traffic, calm traffic by default.
        rush_btn = QtWidgets.QPushButton("rush hour")
        rush_btn.clicked.connect(change_simulation)
        rush_btn.setMinimumSize(rush_btn.sizeHint()) 
        self.sub_layout.addWidget(rush_btn)
        
        def new_one():
            # Stop the simulation while the dialog is
            # visible. If the user doesn't want to
            # build a new one, start the simulation again.
            was_frozen = self.frozen
            if not was_frozen: start()
            new_size = self.set_dialog()
            if new_size: self.constuct_new(new_size)
            elif not was_frozen: start()
        
        # Create a completely new city, this gives the ability to change 
        # the size. If the size stays equal this is still a different
        # operation than restart (below), since the city layout can change.
        new_btn = QtWidgets.QPushButton("new map")
        new_btn.clicked.connect(new_one)
        new_btn.setMinimumSize(new_btn.sizeHint()) 
        self.sub_layout.addWidget(new_btn)
        
        def restart():
            # Start over without changing the city layout, 
            # this will affect self.update_everything().
            self.restart = True
        
        # Restart the traffic simulation with the current layout.
        restart_btn = QtWidgets.QPushButton("restart")
        restart_btn.clicked.connect(restart)
        restart_btn.setMinimumSize(restart_btn.sizeHint()) 
        self.sub_layout.addWidget(restart_btn)
        
        def set_eraser():
            # Set the eraser active.
            self.erase = 1 - self.erase
            self.set_title()
        
        # A button to set the eraser active. If a vehicle is clicked while
        # the eraser is active, it's immediately removed from the scene.
        erase_btn = QtWidgets.QPushButton("erase")
        erase_btn.clicked.connect(set_eraser)
        erase_btn.setMinimumSize(erase_btn.sizeHint()) 
        self.sub_layout.addWidget(erase_btn)
        
        def close():
            # Close the program for good.
            self.setWindowTitle('Terminating')
            sys.exit(app.exec_())
        
        # A button for closing the program.
        exit_btn = QtWidgets.QPushButton("exit")
        exit_btn.clicked.connect(close)
        exit_btn.setMinimumSize(exit_btn.sizeHint()) 
        self.sub_layout.addWidget(exit_btn)
        
        # Add another empty label to set the buttons
        # in the middle of 'self.sub_layout'.
        if self.city.get_dimensions() != 3:
            self.sub_layout.addWidget(QLabel())
    
    def set_occupation_display(self):
        # Add two widgets on the bottom right of the window.
        
        def set_default_counts():
            # Set the default amount of vehicles on the map
            # for casual and rush hour traffic simulation.
            
            casual_max = self.city.get_maximum(0)
            rush_max = self.city.get_maximum(1)
            difference = rush_max-casual_max
            
            self.default_rush_count = casual_max
            self.default_casual_count = casual_max-difference
            self.set_count = self.default_casual_count
            
        set_default_counts()
        
        # A label to display the vehicle count, updated in
        # 'self.update_everything() any time the vehicle count changes.
        max = self.city.get_maximum(0) # not rush hour by default
        self.vehicle_label = QLabel()
        description = '     '+str(0)+'/'+str(max)+' Vehicles     '
        self.vehicle_label.setText(description)
        self.vehicle_label.setMaximumSize(self.vehicle_label.sizeHint())
        self.sub_layout.addWidget(self.vehicle_label)
        
        # A progress bar to demonstrate the vehicle count.
        self.vehicle_bar = QProgressBar()
        self.vehicle_bar.setRange(0, max)
        self.vehicle_bar.setValue(0)
        self.vehicle_bar.setTextVisible(0)
        self.sub_layout.addWidget(self.vehicle_bar)
    
    def set_live_dialog(self):
        # Add one more widget in the bottom-right corner.
        
        def preference(selected):
            # 'self.set_count' represents the set 
            # amount of vehicles chosen by the user.
            self.set_count = selected
             
        # A live QInputDialog-object to select the desired amount of vehicles in
        # the city. Decreasing this will not lead to any vehicle suddenly disappearing.
        self.vehicle_dialog = QtWidgets.QInputDialog()
        self.vehicle_dialog.setOption(QtWidgets.QInputDialog.NoButtons)
        self.vehicle_dialog.setInputMode(QtWidgets.QInputDialog.InputMode.IntInput)
        self.vehicle_dialog.setIntRange(1, self.city.get_maximum(0))
        self.vehicle_dialog.setIntValue(self.set_count)
        self.vehicle_dialog.setLabelText('Set the vehicle count:')  
        self.vehicle_dialog.intValueChanged.connect(preference)
        self.sub_layout.addWidget(self.vehicle_dialog)
        # The dialog will remain visible even if 'Escape' is pressed.
        self.vehicle_dialog.rejected.connect(self.set_live_dialog)
    
    def set_city_graphics(self):
        
        # Set the desired graphics with the help of 'self.city.blocks'.
        size = Constants.BLOCK_SIZE
        for i in range(self.city.get_dimensions()):
            for j in range(self.city.get_dimensions()):
                block = self.city.get_block(i, j)
                map_piece = CityGraphicsItem(i*size, j*size, block)
                self.scene.addItem(map_piece)
                
        if self.city.get_dimensions() == 3:
            # Add six more pieces to cover  
            # the white area around the map.
            grass_piece = [0,0,0,0]
            vertical_road_piece = [0,1,0,1]
            map_piece1 = CityGraphicsItem(0, -size, grass_piece)
            self.scene.addItem(map_piece1)
            map_piece2 = CityGraphicsItem(size, -size, vertical_road_piece)
            self.scene.addItem(map_piece2)
            map_piece3 = CityGraphicsItem(2*size, -size, grass_piece)
            self.scene.addItem(map_piece3)
            map_piece4 = CityGraphicsItem(0, 3*size, grass_piece)
            self.scene.addItem(map_piece4)
            map_piece5 = CityGraphicsItem(size, 3*size, vertical_road_piece)
            self.scene.addItem(map_piece5)
            map_piece6 = CityGraphicsItem(2*size, 3*size, grass_piece)
            self.scene.addItem(map_piece6)
    
    def set_vehicle_graphics(self, vehicle):
        # Set the graphics for 'vehicle', this can't be
        # done before the vehicle has been spawned, since
        # it's position or rotation aren't defined before that.
                    
        graphics = VehicleGraphicsModel(vehicle)
        x, y = vehicle.get_position()
        angle = vehicle.get_scene_rotation()
        
        self.scene.addItem(graphics)
        self.vehicle_graphics[vehicle] = graphics
        
        graphics.setPos(x, y)
        graphics.setRotation(angle)
        # All vehicles are painted on top of the paths,
        # radar areas don't matter since they are see-through.
        graphics.setZValue(1)
        
        # Wheels and windows are separately added.
        for wheel in graphics.get_wheels():
            self.scene.addItem(wheel)
            wheel.setPos(x, y)
            wheel.setRotation(angle)
            wheel.setZValue(1)
        for window in graphics.get_windows():
            self.scene.addItem(window)
            window.setPos(x, y)
            window.setRotation(angle)
            window.setZValue(1)
    
    def draw_path(self, vehicle):
        # Draw the path coordinates of 'vehicle' as black dots and set them invisible.
        # The visibility can be changed by clicking on the respective vehicle graphics.
        
        dot = Constants.DOT_SIZE
        visible = 0 # invisible
        
        self.path_items[vehicle] = []
        all_coordinates = vehicle.get_path().get_coordinates()
        if self.city.get_dimensions() == 3:
            start = 0
            stop = len(all_coordinates)
        else:
            start = 1
            stop = len(all_coordinates)-1
        for index in range(start, stop):
            # Don't mark any coordinates outside the map, e.g. the bordering pieces.
            piece = all_coordinates[index]
            for location in piece:
                elli = QGraphicsEllipseItem(location[0]-dot/2,location[1]-dot/2,dot,dot)
                elli.setBrush(QBrush(QColor(20,20,20)))
                elli.setVisible(visible) 
                self.scene.addItem(elli)
                self.path_items[vehicle].append(elli)
        if self.city.get_dimensions() != 3:
            # One last dot on the edge of the map.
            index = len(all_coordinates)-1
            piece = all_coordinates[index]
            location = piece[0]
            elli = QGraphicsEllipseItem(location[0]-dot/2,location[1]-dot/2,dot,dot)
            elli.setBrush(QBrush(QColor(20,20,20)))
            elli.setVisible(visible)
            self.scene.addItem(elli)
            self.path_items[vehicle].append(elli)
    
    def paint_radar(self, vehicle):
        # The radar is visualized by a red see-through circle.
        # If the center-point of another vehicle is within the
        # area, then it's visible to the owner of the radar.
        
        visible = 0 # invisible
                    
        diam = 2*vehicle.get_radar().range                        
        area = QGraphicsEllipseItem(-diam/2, -diam/2, diam, diam)
        area.setParentItem(self.vehicle_graphics[vehicle])
        area.setTransformOriginPoint(-diam/2, -diam/2)
        area.setBrush(QBrush(QColor(255,0,0),  1))
        area.setOpacity(0.25) # see-through
        area.setVisible(visible)
        self.scene.addItem(area)
        self.radar_areas[vehicle] = area
    
    def constuct_new(self, new_size):
        # This method is very similar to 'self.__init__()',
        # the same methods can easily be reused.
                
        if new_size <= 4:
            amount = 2
        else:
            amount = 1
        
        for i in range(amount):
            
            self.vehicle_graphics.clear()
            self.path_items.clear()
            self.radar_areas.clear()
        
            # Set a new central widget and new layouts, this
            # way all the previous items are lost (as intended).
            self.setCentralWidget(QtWidgets.QWidget())
            self.layout = QtWidgets.QBoxLayout(1)
            self.sub_layout = QtWidgets.QVBoxLayout()
            self.layout.addLayout(self.sub_layout)
            self.centralWidget().setLayout(self.layout)
            
            # A completely new city.
            self.city = CityCenter(new_size)
            
            # Restore the default parameters.
            self.frozen = 1
            self.rush_hour = 0
            self.erase = 0
            self.restart = False
            
            # Set the view for
            # the fresh city.
            self.set_window()
            self.set_buttons()
            self.set_occupation_display()
            self.set_live_dialog()
            self.set_city_graphics()
    
    
if __name__ == '__main__':
    # The main function
    global app
    app = QApplication(sys.argv)
    gui = GUI()
    sys.exit(app.exec_())
    'Simulation over.'



        