
import sys
import Queue
import heapq

PATH_COLOR = 255 # equivalent to the color white
MARK_PATH = -1

class Maze:
    def __init__(self, openings, pixels):
        self.openings = openings
        self.pixels = pixels
        self.height = len(pixels)
        self.width = len(pixels[0])
        
        
    """
    check if certain coordinate is in bounds
    
    """
    def is_in_bounds(self, i, j):
        return i >= 0 and i < self.height and j >= 0 and j < self.width
    
    
    """
    Uses an Best First/A* Search with restrictions and heuristics to find 
    shortest path of the maze
    
    The restriction limits the path finding to at least a certain distance
    to the walls. The purpose is to have the shortest path be "as middle of 
    the path as possible" when drawn
    However such a search might fail due to inconsistent width of path 
    within the maze. Hence we incrementally decrease the restriction 
    (distance from wall) if the algorithm fails
    
    An extra heuristic is added to make the final drawn path free of diagonal
    lines
    The heuristic is "amount of turns/direction changes made". This allows the
    pixels with the least amount of direction changes to be explored first, 
    which in the end gives us a path with no unnecessary diagonal lines
    
    """
    def find_path(self):
        global PATH_COLOR
        global MARK_PATH
        
        # constants
        LEFT = 1
        RIGHT = 2
        UP = 3
        DOWN = 4
        UNEXPLORED = -1
        
        pixels = self.pixels
        openings = self.openings
        height = self.height
        width = self.width
        
        # path stores the indices of the previous pixel that expanded to the current pixel
        # in other words the pixel value points to the pixel it visited in the previous step
        path = [[UNEXPLORED] * width for i in xrange(height)]
        
        # put exit pixel coordinates into set
        exit = set()
        opening1 = openings[1]
        for i in xrange(opening1.ymin, opening1.ymax):
            for j in xrange(opening1.xmin, opening1.xmax):
                exit.add((i, j))
        
        
        print "searching for shortest path on maze..."
        
        # uses nearest wall distance as a restriction during BFS
        wall_dist = self.calculate_dist_to_walls()
        
        # side buffer stores the distance to keep from the wall
        # starts with half the length of the smallest opening
        side_buffer = min(openings[0].long_len(), openings[1].long_len()) / 2
        
        directions = [(0, -1, LEFT), (0, 1, RIGHT), (-1, 0, UP), (1, 0, DOWN)]
        
        # run BFS with restrictions on maze, loop until path found
        for buffer in xrange(side_buffer, 0, -1):
            h = []
            
            # add pixels from first opening to heap
            opening2 = openings[0]
            for i in xrange(opening2.ymin, opening2.ymax):
                for j in xrange(opening2.xmin, opening2.xmax):
                    if wall_dist[i][j] >= buffer:
                        path[i][j] = (i, j)
                        heapq.heappush(h, (0, i, j, 0))
            
            while h:
                priority, yprev, xprev, prev_dir = heapq.heappop(h)
                
                for ydir, xdir, new_dir in directions:
                    i = yprev + ydir
                    j = xprev + xdir
                    
                    # check if new pixel coordinate is 
                    # 1. in bounds 2. not explored 3. part of path 4. if is part of exit
                    if (self.is_in_bounds(i, j) and path[i][j] == UNEXPLORED and 
                      pixels[i][j] == PATH_COLOR and wall_dist[i][j] >= buffer):
                        path[i][j] = (yprev, xprev)
                        # penalize changing directions to prevent diagonal lines
                        new_priority = priority if new_dir == prev_dir else priority + 1
                        heapq.heappush(h, (new_priority, i, j, new_dir))
                        
                        if (i, j) in exit:
                            print "finished searching for shortest path"
                            self.make_path(path, (i, j), buffer)
                            
                            return
        
        print "error, no path found in maze"
        sys.exit()
    
    
    """
    Uses BFS to calculate each pixel's distance to the nearest wall
    @return wall_dist: list containing pixel's distance to nearest wall
    
    """
    def calculate_dist_to_walls(self):
        global PATH_COLOR
        UNEXPLORED = -1
        
        pixels = self.pixels
        height = self.height
        width = self.width
        
        wall_dist = [[UNEXPLORED] * width for i in xrange(height)]
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        q = Queue.Queue()
        
        # put all wall elements onto Queue
        for i in xrange(height):
            for j in xrange(width):
                if pixels[i][j] != PATH_COLOR:
                    q.put((i, j))
                    wall_dist[i][j] = 0
        
        # run BFS
        while not q.empty():
            ycoord, xcoord = q.get()
            val = wall_dist[ycoord][xcoord]
            
            for y, x in directions:
                i = ycoord + y
                j = xcoord + x
                
                if self.is_in_bounds(i, j) and wall_dist[i][j] == UNEXPLORED:
                    wall_dist[i][j] = val + 1
                    q.put((i, j))
        
        return wall_dist
    
    
    """
    Marks the shortest path found by the find_path() method with the`
    constant: MARK_PATH = -1, and thickens trace by marking the correct
    adjacent pixels
    
    The method that does the drawing can then use this information to 
    color the pixels on the shortest path
    
    """
    def make_path(self, path, final_exit, buffer):
        global PATH_COLOR
        global MARK_PATH
        
        pixels = self.pixels
        height = self.height
        width = self.width
        
        print "drawing shortest path..."
        
        # start traversing from the exit to mark shortest path
        ycurr, xcurr = final_exit
        pixels[ycurr][xcurr] = MARK_PATH
        ynext, xnext = path[ycurr][xcurr]
        yprev_dir = ycurr - ynext
        xprev_dir = xcurr - xnext
        
        end = 0
        reach_end = False
        while not reach_end:
            # if direction has changed, make path wider by traverse backwards
            # and coloring the pixels adjacent to the path 
            ynew_dir = ycurr - ynext
            xnew_dir = xcurr - xnext
            if (ynew_dir, xnew_dir) != (yprev_dir, xprev_dir) and buffer >= 2:
                i = ycurr
                j = xcurr
                
                while self.is_in_bounds(i, j) and pixels[i][j] == MARK_PATH:
                    if yprev_dir == 0:
                        for k in xrange(1, buffer / 2):
                            pixels[i - k][j] = MARK_PATH
                            pixels[i + k][j] = MARK_PATH
                    else:
                        for k in xrange(1, buffer / 2):
                            pixels[i][j - k] = MARK_PATH
                            pixels[i][j + k] = MARK_PATH
                    
                    # update i and j
                    i += yprev_dir
                    j += xprev_dir
                
                # update direction
                yprev_dir, xprev_dir = ynew_dir, xnew_dir
            
            # mark trace
            pixels[ynext][xnext] = MARK_PATH
            
            # update variables
            ycurr, xcurr = ynext, xnext
            ynext, xnext = path[ynext][xnext]
            
            # exit one iteration after reaching the entrance, for trace drawing purposes
            if (ynext, xnext) == path[ynext][xnext]:
                end += 1
                reach_end = end > 2
        
        return
