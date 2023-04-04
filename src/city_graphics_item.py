

from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtWidgets import QGraphicsItem
from PyQt5.Qt import QGraphicsRectItem, QBrush, QColor
from PyQt5.QtCore import QPointF, QRectF, Qt
from constants import Constants

class CityGraphicsItem(QGraphicsItem):
    
    '''
    This class will paint every block on the map according
    to the city blocks. Each block is defined individually
    and returned to the GUI, which then adds the block to the 
    scene. There are twelve options in total, 'self.identifier'
    will decide which kind of a piece the CityGraphicsItem-
    object will resemble. The identifier will be a four-term
    list, check 'self.paint' and 'CityCenter.set_options' for
    further information.
    '''
    
    def __init__(self, x, y, identifier):
        super(CityGraphicsItem, self).__init__()
        self.block_size = Constants.BLOCK_SIZE
        self.identifier = identifier
        self.x = x
        self.y = y
        self.bRekt = QRectF(self.x,self.y,self.block_size,self.block_size)
        
    def boundingRect(self): return self.bRekt
    
    def paint(self, painter, option, widget):
        self.painter = painter
        rect = QRectF(self.x, self.y, self.block_size, self.block_size)
        # Lawn green
        self.painter.setBrush(QBrush(QColor(110,221,13)))
        # Pavement gray
        self.painter.setPen(QColor(211, 211, 211))
        self.painter.drawRect(rect)

        if self.identifier == [0,0,0,0]: self.lawn()
        
        elif self.identifier == [1,0,1,0]: self.horizontal_road()
        elif self.identifier == [0,1,0,1]: self.vertical_road()
        
        elif self.identifier == [1,1,0,0]: self.curve1()
        elif self.identifier == [0,1,1,0]: self.curve2()
        elif self.identifier == [0,0,1,1]: self.curve3()
        elif self.identifier == [1,0,0,1]: self.curve4()
        
        elif self.identifier == [1,1,0,1]: self.t_intersection1()
        elif self.identifier == [1,1,1,0]: self.t_intersection2()
        elif self.identifier == [0,1,1,1]: self.t_intersection3()
        elif self.identifier == [1,0,1,1]: self.t_intersection4()
        
        else: self.four_way_intersection()
        
    def lawn(self):
        # The lawn is already painted.
        pass
    
    def vertical_road(self):
        x = self.block_size/8
        width = self.block_size-2*x
        offset = self.block_size/52
        line_width = 2.5*self.block_size/100
        rect = QRectF(x+self.x, self.y, width, self.block_size)
        self.painter.setBrush(QBrush(QColor(211,211,211)))
        self.painter.drawRect(rect)
        self.painter.setPen(QPen(QColor(255,255,23),line_width))
        self.painter.drawLine(self.x+self.block_size/2+offset,self.y+line_width/2,self.x+self.block_size/2+offset,self.y+self.block_size-line_width/2)
        self.painter.drawLine(self.x+self.block_size/2-offset,self.y+line_width/2,self.x+self.block_size/2-offset,self.y+self.block_size-line_width/2)

    def horizontal_road(self):
        y = self.block_size/8
        height = self.block_size-2*y
        offset = self.block_size/52
        line_width = 2.5*self.block_size/100
        rect = QRectF(self.x, y+self.y, self.block_size, height)
        self.painter.setBrush(QBrush(QColor(211, 211, 211)))
        self.painter.drawRect(rect)
        self.painter.setPen(QPen(QColor(255,255,23),line_width))
        self.painter.drawLine(self.x+line_width/2,self.y+self.block_size/2+offset,self.x+self.block_size-line_width/2,self.y+self.block_size/2+offset)
        self.painter.drawLine(self.x+line_width/2,self.y+self.block_size/2-offset,self.x+self.block_size-line_width/2,self.y+self.block_size/2-offset)  
    
    def curve1(self):
        astart = -1440
        alen = -1440
        r = 14*self.block_size/8
        attach_x = self.x+self.block_size-r/2
        attach_y = self.y-r/2
        offset = self.block_size/52
        line_width = 2.5*self.block_size/100
        # Pavement
        self.painter.setBrush(QBrush(QColor(211,211,211)))
        self.painter.drawPie(attach_x,attach_y,r,r,astart,alen)
        # Laser lemon yellow
        r = self.block_size + 2*offset + line_width
        attach_x = self.x+self.block_size-r/2
        attach_y = self.y-r/2
        self.painter.setBrush(QBrush(QColor(255,255,23)))
        self.painter.drawPie(attach_x,attach_y,r,r,astart,alen)
        # Pavement
        r = self.block_size + 2*offset - line_width
        attach_x = self.x+self.block_size-r/2
        attach_y = self.y-r/2
        self.painter.setBrush(QBrush(QColor(211,211,211)))
        self.painter.drawPie(attach_x,attach_y,r,r,astart,alen)
        # Laser lemon yellow
        r = self.block_size - 2*offset + line_width
        attach_x = self.x+self.block_size-r/2
        attach_y = self.y-r/2
        self.painter.setBrush(QBrush(QColor(255,255,23)))
        self.painter.drawPie(attach_x,attach_y,r,r,astart,alen)
        # Pavement
        r = self.block_size - 2*offset - line_width
        attach_x = self.x+self.block_size-r/2
        attach_y = self.y-r/2
        self.painter.setBrush(QBrush(QColor(211,211,211)))
        self.painter.drawPie(attach_x,attach_y,r,r,astart,alen)
        # Lawn
        r = self.block_size/4
        attach_x = self.x+self.block_size-r/2
        attach_y = self.y-r/2
        self.painter.setBrush(QBrush(QColor(110,221,13)))
        self.painter.drawPie(attach_x,attach_y,r,r,astart,alen)

    def curve2(self):
        astart = 0
        alen = -1440
        r = 14*self.block_size/8
        attach_x = self.x-r/2
        attach_y = self.y-r/2
        offset = self.block_size/52
        line_width = 2.5*self.block_size/100
        # Pavement
        self.painter.setBrush(QBrush(QColor(211,211,211)))
        self.painter.drawPie(attach_x,attach_y,r,r,astart,alen)
        # Laser lemon yellow
        r = self.block_size + 2*offset + line_width
        attach_x = self.x-r/2
        attach_y = self.y-r/2
        self.painter.setBrush(QBrush(QColor(255,255,23)))
        self.painter.drawPie(attach_x,attach_y,r,r,astart,alen)
        # Pavement
        r = self.block_size + 2*offset - line_width
        attach_x = self.x-r/2
        attach_y = self.y-r/2
        self.painter.setBrush(QBrush(QColor(211,211,211)))
        self.painter.drawPie(attach_x,attach_y,r,r,astart,alen)
        # Laser lemon yellow
        r = self.block_size - 2*offset + line_width
        attach_x = self.x-r/2
        attach_y = self.y-r/2
        self.painter.setBrush(QBrush(QColor(255,255,23)))
        self.painter.drawPie(attach_x,attach_y,r,r,astart,alen)
        # Pavement
        r = self.block_size - 2*offset - line_width
        attach_x = self.x-r/2
        attach_y = self.y-r/2
        self.painter.setBrush(QBrush(QColor(211,211,211)))
        self.painter.drawPie(attach_x,attach_y,r,r,astart,alen)
        # Lawn
        r = self.block_size/4
        attach_x = self.x-r/2
        attach_y = self.y-r/2
        self.painter.setBrush(QBrush(QColor(110,221,13)))
        self.painter.drawPie(attach_x,attach_y,r,r,astart,alen)

    def curve3(self):
        astart = 0
        alen = 1440
        r = 14*self.block_size/8
        attach_x = self.x-r/2
        attach_y = self.y+self.block_size-r/2
        offset = self.block_size/52
        line_width = 2.5*self.block_size/100
        # Pavement
        self.painter.setBrush(QBrush(QColor(211,211,211)))
        self.painter.drawPie(attach_x,attach_y,r,r,astart,alen)
        # Laser lemon yellow
        r = self.block_size + 2*offset + line_width
        attach_x = self.x-r/2
        attach_y = self.y+self.block_size-r/2
        self.painter.setBrush(QBrush(QColor(255,255,23)))
        self.painter.drawPie(attach_x,attach_y,r,r,astart,alen)
        # Pavement
        r = self.block_size + 2*offset - line_width
        attach_x = self.x-r/2
        attach_y = self.y+self.block_size-r/2
        self.painter.setBrush(QBrush(QColor(211,211,211)))
        self.painter.drawPie(attach_x,attach_y,r,r,astart,alen)
        # Laser lemon yellow
        r = self.block_size - 2*offset + line_width
        attach_x = self.x-r/2
        attach_y = self.y+self.block_size-r/2
        self.painter.setBrush(QBrush(QColor(255,255,23)))
        self.painter.drawPie(attach_x,attach_y,r,r,astart,alen)
        # Pavement
        r = self.block_size - 2*offset - line_width
        attach_x = self.x-r/2
        attach_y = self.y+self.block_size-r/2
        self.painter.setBrush(QBrush(QColor(211,211,211)))
        self.painter.drawPie(attach_x,attach_y,r,r,astart,alen)
        # Lawn
        r = self.block_size/4
        attach_x = self.x-r/2
        attach_y = self.y+self.block_size-r/2
        self.painter.setBrush(QBrush(QColor(110,221,13)))
        self.painter.drawPie(attach_x,attach_y,r,r,astart,alen)

    def curve4(self):
        astart = 1440
        alen = 1440
        r = 14*self.block_size/8
        attach_x = self.x+self.block_size-r/2
        attach_y = self.y+self.block_size-r/2
        offset = self.block_size/52
        line_width = 2.5*self.block_size/100
        # Pavement
        self.painter.setBrush(QBrush(QColor(211,211,211)))
        self.painter.drawPie(attach_x,attach_y,r,r,astart,alen)
        # Laser lemon yellow
        r = self.block_size + 2*offset + line_width
        attach_x = self.x+self.block_size-r/2
        attach_y = self.y+self.block_size-r/2
        self.painter.setBrush(QBrush(QColor(255,255,23)))
        self.painter.drawPie(attach_x,attach_y,r,r,astart,alen)
        # Pavement
        r = self.block_size + 2*offset - line_width
        attach_x = self.x+self.block_size-r/2
        attach_y = self.y+self.block_size-r/2
        self.painter.setBrush(QBrush(QColor(211,211,211)))
        self.painter.drawPie(attach_x,attach_y,r,r,astart,alen)
        # Laser lemon yellow
        r = self.block_size - 2*offset + line_width
        attach_x = self.x+self.block_size-r/2
        attach_y = self.y+self.block_size-r/2
        self.painter.setBrush(QBrush(QColor(255,255,23)))
        self.painter.drawPie(attach_x,attach_y,r,r,astart,alen)
        # Pavement
        r = self.block_size - 2*offset - line_width
        attach_x = self.x+self.block_size-r/2
        attach_y = self.y+self.block_size-r/2
        self.painter.setBrush(QBrush(QColor(211,211,211)))
        self.painter.drawPie(attach_x,attach_y,r,r,astart,alen)
        # Lawn
        r = self.block_size/4
        attach_x = self.x+self.block_size-r/2
        attach_y = self.y+self.block_size-r/2
        self.painter.setBrush(QBrush(QColor(110,221,13)))
        self.painter.drawPie(attach_x,attach_y,r,r,astart,alen)

    def t_intersection1(self):
        # Paint the whole piece pavement-colored first.
        rect = QRectF(self.x, self.y, self.block_size, self.block_size)
        self.painter.setBrush(QBrush(QColor(211,211,211)))
        self.painter.drawRect(rect)
        
        rect = QRectF(self.x, self.y, self.block_size/8, self.block_size)
        self.painter.setBrush(QBrush(QColor(110,221,13)))
        self.painter.drawRect(rect)
        
        astart = 1440
        alen = 1440
        r = self.block_size/4
        attach_x = self.x+self.block_size-r/2
        attach_y = self.y+self.block_size-r/2
        self.painter.drawPie(attach_x,attach_y,r,r,astart,alen)

        astart = -1440
        alen = -1440
        attach_x = self.x+self.block_size-r/2
        attach_y = self.y-r/2
        self.painter.drawPie(attach_x,attach_y,r,r,astart,alen)
        # Draw white lines on the road.
        div = self.block_size/8
        line_width = 2.5*self.block_size/100
        self.painter.setPen(QPen(QColor(255,255,255),line_width))
        for i in range(0,10,2):
            self.painter.drawLine(self.x+self.block_size/2,self.y+line_width/2+(i+1/2)*div,self.x+self.block_size/2,self.y+(i+3/2)*div-line_width/2)

    def t_intersection2(self):
        # Paint the whole piece pavement-colored first.
        rect = QRectF(self.x, self.y, self.block_size, self.block_size)
        self.painter.setBrush(QBrush(QColor(211,211,211)))
        self.painter.drawRect(rect)
        
        rect = QRectF(self.x, self.y+7*self.block_size/8, self.block_size, self.block_size/8)
        self.painter.setBrush(QBrush(QColor(110,221,13)))
        self.painter.drawRect(rect)
        
        astart = -1440
        alen = -1440
        r = self.block_size/4
        attach_x = self.x+self.block_size-r/2
        attach_y = self.y-r/2
        self.painter.drawPie(attach_x,attach_y,r,r,astart,alen)

        astart = 0
        alen = -1440
        attach_x = self.x-r/2
        attach_y = self.y-r/2
        self.painter.drawPie(attach_x,attach_y,r,r,astart,alen)
        # Draw white lines on the road.
        div = self.block_size/8
        line_width = 2.5*self.block_size/100
        self.painter.setPen(QPen(QColor(255,255,255),line_width))
        for i in range(0,10,2):
            self.painter.drawLine(self.x+line_width/2+(i+1/2)*div,self.y+self.block_size/2,self.x+(i+3/2)*div-line_width/2,self.y+self.block_size/2)
            
    def t_intersection3(self):
        # Paint the whole piece pavement-colored first.
        rect = QRectF(self.x, self.y, self.block_size, self.block_size)
        self.painter.setBrush(QBrush(QColor(211,211,211)))
        self.painter.drawRect(rect)
        
        rect = QRectF(self.x+7*self.block_size/8, self.y, self.block_size/8, self.block_size)
        self.painter.setBrush(QBrush(QColor(110,221,13)))
        self.painter.drawRect(rect)
        
        astart = 0
        alen = -1440
        r = self.block_size/4
        attach_x = self.x-r/2
        attach_y = self.y-r/2
        self.painter.drawPie(attach_x,attach_y,r,r,astart,alen)

        astart = 0
        alen = 1440
        attach_x = self.x-r/2
        attach_y = self.y+self.block_size-r/2
        self.painter.drawPie(attach_x,attach_y,r,r,astart,alen)
        # Draw white lines on the road.
        div = self.block_size/8
        line_width = 2.5*self.block_size/100
        self.painter.setPen(QPen(QColor(255,255,255),line_width))
        for i in range(0,10,2):
            self.painter.drawLine(self.x+self.block_size/2,self.y+line_width/2+(i+1/2)*div,self.x+self.block_size/2,self.y+(i+3/2)*div-line_width/2)

    def t_intersection4(self):
        # Paint the whole piece pavement-colored first.
        rect = QRectF(self.x, self.y, self.block_size, self.block_size)
        self.painter.setBrush(QBrush(QColor(211,211,211)))
        self.painter.drawRect(rect)
        
        rect = QRectF(self.x, self.y, self.block_size, self.block_size/8)
        self.painter.setBrush(QBrush(QColor(110,221,13)))
        self.painter.drawRect(rect)
        
        astart = 1440
        alen = 1440
        r = self.block_size/4
        attach_x = self.x+self.block_size-r/2
        attach_y = self.y+self.block_size-r/2
        self.painter.drawPie(attach_x,attach_y,r,r,astart,alen)

        astart = 0
        alen = 1440
        attach_x = self.x-r/2
        attach_y = self.y+self.block_size-r/2
        self.painter.drawPie(attach_x,attach_y,r,r,astart,alen)
        # Draw white lines on the road.
        div = self.block_size/8
        line_width = 2.5*self.block_size/100
        self.painter.setPen(QPen(QColor(255,255,255),line_width))
        for i in range(0,10,2):
            self.painter.drawLine(self.x+line_width/2+(i+1/2)*div,self.y+self.block_size/2,self.x+(i+3/2)*div-line_width/2,self.y+self.block_size/2)

    def four_way_intersection(self):
        # Paint the whole piece pavement-colored first.
        rect = QRectF(self.x, self.y, self.block_size, self.block_size)
        self.painter.setBrush(QBrush(QColor(211,211,211)))
        self.painter.drawRect(rect)
    
        astart = -1440
        alen = -1440
        r = self.block_size/4
        attach_x = self.x+self.block_size-r/2
        attach_y = self.y-r/2
        self.painter.setBrush(QBrush(QColor(110,221,13)))
        self.painter.drawPie(attach_x,attach_y,r,r,astart,alen)

        astart = 0
        alen = -1440
        attach_x = self.x-r/2
        attach_y = self.y-r/2
        self.painter.drawPie(attach_x,attach_y,r,r,astart,alen)

        astart = 0
        alen = 1440
        attach_x = self.x-r/2
        attach_y = self.y+self.block_size-r/2
        self.painter.drawPie(attach_x,attach_y,r,r,astart,alen)

        astart = 1440
        alen = 1440
        attach_x = self.x+self.block_size-r/2
        attach_y = self.y+self.block_size-r/2
        self.painter.drawPie(attach_x,attach_y,r,r,astart,alen)
    
    