

class Graph():
    
    '''
    The Graph-class takes in the CityCenter-objects layout as 'city_blocks'
    and uses this to form a graph data structure. In the graph, vertices
    are expressed as two-character strings that refer to the vertex location
    in the original CityCenter-object. The graph edges are expressed as a dictionary, 
    where a vertex (such as '14') is the key and a list of tuples is the
    value. The list has as many tuples as the vertex has directly accessible
    vertices. In each tuple, the first value is the accessible vertex, the second
    is an integer representing the distance between these two and the third one
    is the accessible vertex's direction (0, 1, 2 or 3) from the original vertex.
    There are a maximum of 4 directions from each vertex, if a direction equals
    0, it refers to the right-hand-side. Direction 1 represents the top side and
    so on, just like the blocks in the CityCenter-object.
    '''
    
    def __init__(self, city_blocks):        
        self.vertices = []
        self.adjacency = dict()
        self.generate_graph(city_blocks)
        
    def get_vertices(self): return self.vertices
    
    def get_adjacency(self): return self.adjacency
    
    def generate_graph(self, city_blocks):
        
        limit = len(city_blocks)
        
        for i in range(limit):
            for j in range(limit):
                # Naturally every intersection block will become a vertex.
                if self.calculate_weight(city_blocks[i][j]) > 2:
                    self.vertices.append(str(i)+str(j))
                # Every bordering piece that has road access will also serve as a vertex.
                elif i == 0 or i == limit-1:
                    if 1 in city_blocks[i][j]:
                        self.vertices.append(str(i)+str(j))
                elif j == 0 or j == limit-1:
                    if 1 in city_blocks[i][j]:
                        self.vertices.append(str(i)+str(j))
        
        def find_neighbors(i, j, previous, counter, original_direction):
            # This is recursive algorithm that finds every neighboring vertex for vertex
            # i, j and their respective distances and directions from the first vertex.

            # Must stay inside the correct indexes, every bordering piece
            # has a certain direction that is forbidden.
            forbidden = None
            if i == 0: forbidden = 2
            elif i == limit-1: forbidden = 0
            elif j == 0: forbidden = 1
            elif j == limit-1: forbidden = 3
            
            if previous == None:
                # Don't add anything to the lists in the first vertex.
                pass
            else:
                if forbidden != None:
                    # If we get here, it means that this is a bordering
                    # piece and this is not the piece we started from.
                    neighbors.append(str(i)+str(j))
                    distances.append(counter)
                    directions.append(original_direction)
                    # We don't have to move any further.
                    return
                elif self.calculate_weight(city_blocks[i][j]) > 2:
                    # Intersection are naturally vertices.
                    neighbors.append(str(i)+str(j))
                    distances.append(counter)
                    directions.append(original_direction)
                    # We don't have to move any further.
                    return
            
            # Each time we move to the next block, the counter grows by one.
            # Here, the amount of find_neighbors()-function calls it requires
            # to move from vertex A to B is the distance between these two.
            counter += 1
            
            # Move forward on the road until we arrive to the next vertex.
            if city_blocks[i][j][0] == 1:
                if not forbidden == 0 and not previous == 0:
                    if original_direction == None: find_neighbors(i+1, j, 2, counter, 0)
                    else: find_neighbors(i+1, j, 2, counter, original_direction)
            if city_blocks[i][j][1] == 1:
                if not forbidden == 1 and not previous == 1:
                    if original_direction == None: find_neighbors(i, j-1, 3, counter, 1)
                    else: find_neighbors(i, j-1, 3, counter, original_direction)
            if city_blocks[i][j][2] == 1:
                if not forbidden == 2 and not previous == 2:
                    if original_direction == None: find_neighbors(i-1, j, 0, counter, 2)
                    else: find_neighbors(i-1, j, 0, counter, original_direction)
            if city_blocks[i][j][3] == 1:
                if not forbidden == 3 and not previous == 3:
                    if original_direction == None: find_neighbors(i, j+1, 1, counter, 3)
                    else: find_neighbors(i, j+1, 1, counter, original_direction)
        
        for vertex in self.vertices:
            # The coordinates are directly in the vertex.
            i, j = int(vertex[0]), int(vertex[1])
            # Initialize three lists, where the first one represents all the neighboring vertices
            # of the currently observed vertex. The second list represents their respective
            # distances and the third one the respective directions (0, 1, 2, 3) we must start
            # traveling to reach the destined vertex eventually.
            neighbors, distances, directions = [], [], []
            # Fill the lists accordingly.
            find_neighbors(i, j, None, 0, None)
            # Form three-term tuples from the lists and list these behind the key.
            self.adjacency[vertex] = []
            for index in range(len(neighbors)):
                new_tuple = neighbors[index], distances[index], directions[index]
                on_watch = []
                for tuple in self.adjacency[vertex]:
                    on_watch.append(tuple[0])
                if not new_tuple[0] in on_watch:
                    self.adjacency[vertex].append(new_tuple)
                else:
                    # This happens rather rarely, but when it happens, it means that there are
                    # more than one direct links between two intersections. We choose the one 
                    # with the smaller distance, or both, if they are equal.
                    adj = self.adjacency[vertex]
                    for tuple in adj:
                        if tuple[0] == new_tuple[0]:
                            original_tuple = tuple
                    original_distance = tuple[1]
                    new_distance = new_tuple[1]
                    if original_distance < new_distance:
                        pass
                    elif original_distance == new_distance:
                        self.adjacency[vertex].append(new_tuple)
                    else:
                        self.adjacency[vertex].remove(original_tuple)
                        self.adjacency[vertex].append(new_tuple)
            # self.adjacency[vertex] = [(neighbor_vertex_A, distance_to_A, direction_to_A),
            # (neighbor_vertex_B, distance_to_B, direction_to_B)]

    def calculate_weight(self, block):
        # A blocks weight is defined by how many accessible sides it has.
        weight = 0
        for i in block:
            if i == 1:
                weight += 1
        return weight
    
    
    
    