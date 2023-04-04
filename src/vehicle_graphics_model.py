

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.Qt import QGraphicsRectItem, QBrush, QColor, Qt, \
    QPolygonF, QGraphicsPolygonItem
from constants import Constants

class VehicleGraphicsModel(QtWidgets.QGraphicsPolygonItem):
    
    '''
    This class represents the graphics of a vehicle. The vehicle
    hull is constructed with a QPolygonF-object and the rest
    (wheels and windows) with QGraphicsRectItem-objects.
    The respective vehicle is set as an attribute, making
    it easy to update the  position and rotation of the
    graphics on the map. 
    '''
    
    def __init__(self, vehicle):
        super(VehicleGraphicsModel, self).__init__()
        self.owner = vehicle
        self.type = self.owner.type
        self.color = self.owner.color
        self.width = self.owner.width
        self.length = self.owner.length
        # Initially the respective path is invisible.
        self.path_visible = 0
        # This will equal 1 if the user wants
        # to change the path visibility.
        self.flag = 0
        self.construct_hull()
        self.set_color()
        self.add_windows()
        self.add_wheels() 
        
    def set_flag(self): self.flag = 1 - self.flag
    
    def flag_set(self): return self.flag
    
    def show_path(self): return self.path_visible
            
    def get_wheels(self): return self.wheels
    
    def get_windows(self): return self.windows
    
    def update(self):
        
        # Update the position and rotation.
        x, y = self.owner.get_position()
        rotation = self.owner.get_scene_rotation()
        
        self.setPos(x, y)            
        self.setRotation(rotation)
        
        # Same for the wheels and windows.
        for wheel in self.get_wheels():
            wheel.setPos(x, y)
            wheel.setRotation(rotation)
        for window in self.get_windows():
            window.setPos(x, y)
            window.setRotation(rotation)
            
    def mousePressEvent(self, *args, **kwargs):
        # A mouse press event will set the flag, this will result in the GUI-
        # object calling the 'set_visibility' method and changing the path visibility
        self.path_visible = 1 - self.path_visible
        self.set_flag()
        
    def construct_hull(self):
        
        self.setBrush(QtGui.QBrush(1))
        hull = QtGui.QPolygonF()
        
        if self.type == Constants.SEDAN:
            # front end
            hull.append(QtCore.QPointF(0, self.width/4))
            hull.append(QtCore.QPointF(self.width/8.8, self.width/10))
            hull.append(QtCore.QPointF(self.width/4.4, self.width/24)) 
            hull.append(QtCore.QPointF(self.width/2.2, 0))
            hull.append(QtCore.QPointF(self.width-self.width/2.2, 0))
            hull.append(QtCore.QPointF(self.width-self.width/4.4, self.width/24))
            hull.append(QtCore.QPointF(self.width-self.width/8.8, self.width/10))
            hull.append(QtCore.QPointF(self.width, self.width/4))
            # rear end
            hull.append(QtCore.QPointF(self.width, self.length-self.width/8))
            hull.append(QtCore.QPointF(self.width-self.width/30, self.length-self.width/16))
            hull.append(QtCore.QPointF(self.width-self.width/10, self.length-self.width/32))
            hull.append(QtCore.QPointF(self.width-self.width/3.5, self.length))
            hull.append(QtCore.QPointF(self.width/3.5, self.length))
            hull.append(QtCore.QPointF(self.width/10, self.length-self.width/32))
            hull.append(QtCore.QPointF(self.width/30, self.length-self.width/16))
            hull.append(QtCore.QPointF(0, self.length-self.width/8))
            # back to starting point
            hull.append(QtCore.QPointF(0, self.width/4))
            
        elif self.type == Constants.MINI_VAN:
            # front end
            hull.append(QtCore.QPointF(0, self.width/2))
            hull.append(QtCore.QPointF(self.width/60, self.width/4))
            hull.append(QtCore.QPointF(self.width/19, self.width/7))
            hull.append(QtCore.QPointF(self.width/8.8, self.width/12))
            hull.append(QtCore.QPointF(self.width/4.4, self.width/35))
            hull.append(QtCore.QPointF(self.width/2.2, 0))
            hull.append(QtCore.QPointF(self.width-self.width/2.2, 0))
            hull.append(QtCore.QPointF(self.width-self.width/4.4, self.width/35))
            hull.append(QtCore.QPointF(self.width-self.width/8.8, self.width/12))
            hull.append(QtCore.QPointF(self.width-self.width/19, self.width/7))
            hull.append(QtCore.QPointF(self.width-self.width/60, self.width/4))
            hull.append(QtCore.QPointF(self.width, self.width/2))
            # rear end
            hull.append(QtCore.QPointF(self.width, self.length-self.width/5))
            hull.append(QtCore.QPointF(self.width-self.width/35, self.length-self.width/8))
            hull.append(QtCore.QPointF(self.width-self.width/8, self.length-self.width/25))
            hull.append(QtCore.QPointF(self.width-self.width/4, self.length))
            hull.append(QtCore.QPointF(self.width/4, self.length))
            hull.append(QtCore.QPointF(self.width/8, self.length-self.width/25))
            hull.append(QtCore.QPointF(self.width/35, self.length-self.width/8))
            hull.append(QtCore.QPointF(0, self.length-self.width/5))
            # back to starting point
            hull.append(QtCore.QPointF(0, self.width/2))
            
        else: # Pickup truck
            # front end
            hull.append(QtCore.QPointF(0, self.width/10))
            hull.append(QtCore.QPointF(self.width/3, 0))
            hull.append(QtCore.QPointF(self.width-self.width/3, 0))
            hull.append(QtCore.QPointF(self.width, self.width/10))
            # back end
            hull.append(QtCore.QPointF(self.width, self.length-self.width/15))
            hull.append(QtCore.QPointF(self.width-self.width/12, self.length-self.width/15))
            hull.append(QtCore.QPointF(self.width-self.width/5, self.length))
            hull.append(QtCore.QPointF(self.width/5, self.length))
            hull.append(QtCore.QPointF(self.width/12, self.length-self.width/15))
            hull.append(QtCore.QPointF(0, self.length-self.width/15))
            # back to the starting point
            hull.append(QtCore.QPointF(0, self.width/10))               
        
        hull.translate(-self.width/2, -self.length/2)
        self.setPolygon(hull)
       
    def set_color(self):
        
        if self.color == 'Red':
            brush = QColor(221,42,90)
        elif self.color == 'Green':
            brush = QColor(119,221,119)
        elif self.color == 'Blue':
            brush = QColor(55,83,221)
        elif self.color == 'Yellow':
            brush = QColor(215,221,33)
        elif self.color == 'Turquoise':
            brush = QColor(60,221,210)
        elif self.color == 'Violet':
            brush = QColor(181,49,221)
        elif self.color == 'Gray':
            brush = QColor(114,117,109)
        elif self.color == 'Black':
            brush = QColor(69,72,67)
        elif self.color == 'Orange':
            brush = QColor(221,112,49)
        else: # White
            brush = QColor(255, 255, 255)
            
        self.setBrush(QtGui.QBrush(brush))
        
    def add_windows(self):
        # Add one or two rectangles to visualize the vehicle windows.
        # A couple elements that are not exactly windows can be listed as well.
        
        self.windows = []
        black_brush = QBrush(QColor(20, 20, 20))
        gray_brush = QBrush(QColor(75, 75, 75))
        
        if self.type == Constants.SEDAN:
            # Add a wind shield and a rear window.
            windshield = QGraphicsRectItem(self.width/10-self.width/2, \
                1.2*self.length/4-self.length/2.2, 4*self.width/5, self.length/10)
            windshield.setBrush(gray_brush)
            self.windows.append(windshield)
            
            rear_window = QGraphicsRectItem(self.width/9-self.width/2, \
                1.25*self.length/4, 7*self.width/9, self.length/18)
            rear_window.setBrush(black_brush) # tinted rear window
            self.windows.append(rear_window)
            # Connect the window corners with a rectangular polygon.
            cords = QPolygonF()
            cords.append(QtCore.QPointF(self.width/10-self.width/2, 1.2*self.length/4-self.length/2.2+self.length/10))
            cords.append(QtCore.QPointF(-self.width/10+self.width/2, 1.2*self.length/4-self.length/2.2+self.length/10))
            cords.append(QtCore.QPointF(-self.width/9+self.width/2, 1.25*self.length/4))
            cords.append(QtCore.QPointF(self.width/9-self.width/2, 1.25*self.length/4))
            cords.append(QtCore.QPointF(self.width/10-self.width/2, 1.2*self.length/4-self.length/2.2+self.length/10))
            roof = QGraphicsPolygonItem(cords)
            self.windows.append(roof)
        elif self.type == Constants.MINI_VAN:
            # Add just a wind shield.
            windshield = QGraphicsRectItem(self.width/10-self.width/2, \
                self.length/4-self.length/2, 4*self.width/5, self.length/10)
            windshield.setBrush(gray_brush) 
            self.windows.append(windshield)
        else: # Pickup truck
            # Add a wind shield and a gray-colored rectangle with a visible
            #  grid-like pattern on top to visualize the truck bed.
            windshield = QGraphicsRectItem(self.width/10-self.width/2, \
                self.length/4-self.length/2, 4*self.width/5, self.length/10)
            windshield.setBrush(gray_brush)
            self.windows.append(windshield)
            
            bed_brush = QBrush(QColor(130,130,130)) # Dark gray
            truck_bed = QGraphicsRectItem(self.width/7-self.width/2, \
                self.length/16, 5*self.width/7, self.length/3)
            truck_bed.setBrush(bed_brush)
            self.windows.append(truck_bed)
            
            grid_brush = QBrush(QColor(20,20,20), Qt.DiagCrossPattern)   
            truck_bed_grid = QGraphicsRectItem(self.width/7-self.width/2, \
                self.length/16, 5*self.width/7, self.length/3)
            truck_bed_grid.setBrush(grid_brush)
            self.windows.append(truck_bed_grid)

    def add_wheels(self):
        # Add four black rectangles to visualize the wheels.
        
        self.wheels = []
        black_brush = QBrush(QColor(20, 20, 20)) # very black
        
        if self.type == Constants.SEDAN:
            length = self.length/6.5
            width = self.width/25
            # Front left
            wheel1 = QGraphicsRectItem(-width-self.width/2, length-self.length/2.5, width, length)
            wheel1.setBrush(black_brush)
            self.wheels.append(wheel1)
            # Front right
            wheel2 = QGraphicsRectItem(self.width-self.width/2, length-self.length/2.5, width, length)
            wheel2.setBrush(black_brush)
            self.wheels.append(wheel2)
            # Rear left
            wheel3 = QGraphicsRectItem(-width-self.width/2, self.length-2.5*length-self.length/2.35, width, length)
            wheel3.setBrush(black_brush)
            self.wheels.append(wheel3)
            # Rear right
            wheel4 = QGraphicsRectItem(self.width-self.width/2, self.length-2.5*length-self.length/2.35, width, length)
            wheel4.setBrush(black_brush)
            self.wheels.append(wheel4)
        elif self.type == Constants.PICKUP_TRUCK:        
            length = self.length/7
            width = self.width/20
            # Front left
            wheel1 = QGraphicsRectItem(-width-self.width/2, length-self.length/2, width, length)
            wheel1.setBrush(black_brush)
            self.wheels.append(wheel1)
            # Front right
            wheel2 = QGraphicsRectItem(self.width-self.width/2, length-self.length/2, width, length)
            wheel2.setBrush(black_brush)
            self.wheels.append(wheel2)
            # Rear left
            wheel3 = QGraphicsRectItem(-width-self.width/2, self.length-2.5*length-self.length/2, width, length)
            wheel3.setBrush(black_brush)
            self.wheels.append(wheel3)
            # Rear right
            wheel4 = QGraphicsRectItem(self.width-self.width/2, self.length-2.5*length-self.length/2, width, length)
            wheel4.setBrush(black_brush)
            self.wheels.append(wheel4)
        else:
            # No visible wheels for a mini van.
            pass
        