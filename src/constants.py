

class Constants():
    
    '''
    This class helps to tweak the size of every item
    in the graphics scene to make them just the right size.
    Certain tests can also be performed with greater accuracy
    when parameters, such as 'BLOCK_SIZE' or 'TIME_STEP', are
    altered. The default values are parameters that are deemed
    to be the most suitable.
    '''
    
    SEDAN = 0
    MINI_VAN = 1
    PICKUP_TRUCK = 2
    
    # Default 100.0
    BLOCK_SIZE = 100.0
    
    # Default 0.1875*BLOCK_SIZE
    PATH_RADIUS = 0.1875*BLOCK_SIZE
    
    # Default 1.2*PATH_RADIUS
    VEHICLE_SIZE = 1.2*PATH_RADIUS
    
    # Default 0.025*BLOCK_SIZE
    DOT_SIZE = 0.025*BLOCK_SIZE
    
    # Default 10, too big time steps will result in unwanted features. 
    TIME_STEP = 10
    
    