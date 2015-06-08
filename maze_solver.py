
import sys, os
import Queue
import heapq
from PIL import Image

PATH_COLOR = 255
MARK_PATH = -1


"""
a class made to represent borders and openings of maze image

"""

class Rectangle:
    def __init__(self, xmin, xmax, ymin, ymax):
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
    
    def long_len(self):
        return max(self.xmax - self.xmin, self.ymax - self.ymin)

    def overlap(self, that):
        x_overlap = self.xmax >= that.xmin and self.xmin <= that.xmax 
        y_overlap = self.ymax >= that.ymin and self.ymin <= that.ymax
        return x_overlap and y_overlap


"""
crops extra white space from the maze image so everything outside of the 
borders are not included

@return : cropped Image file

"""
def crop_maze(im, pixels):
    global PATH_COLOR
    
    height = len(pixels)
    width = len(pixels[0])
    
    xmin = width
    xmax = -1
    ymin = height
    ymax = -1
    
    for i in xrange(height / 2):
        for j in xrange(width / 2):
            if pixels[i][j] != PATH_COLOR and xmin == width:
                ymin = i
                xmin = j
            elif pixels[i][j] != PATH_COLOR and j < xmin:
                xmin = j
            if pixels[height - 1 - i][width - 1 - j] != PATH_COLOR and xmax == -1:
                ymax = height - 1 - i
                xmax = width - 1 - j
            elif pixels[height - 1 - i][width - 1 - j] != PATH_COLOR and width - 1 - j > xmax:
                xmax = width - 1 - j
    
    if xmin == width and ymin == height:
        print "Error, invalid maze image"
        sys.exit()
        
    return im.crop((xmin, ymin, xmax + 1, ymax + 1))

    
"""
finds the entrance and exit of the maze
@return openings: in format of rectangles (see Rectangle class)

"""
def find_entrance_exit(pixels):
    height = len(pixels)
    width = len(pixels[0])

    openings = []
    
    # constructor of Rectangle needs (xmin, xmax, ymin, ymax)
    left_rect = Rectangle(0, 1, 0, height)
    right_rect = Rectangle(width - 1, width, 0, height)
    top_rect = Rectangle(0, width, 0, 1)
    bottom_rect = Rectangle(0, width, height - 1, height)
    
    # scan to find openings
    find_opening_ranges(left_rect, openings, pixels)
    find_opening_ranges(right_rect, openings, pixels)
    find_opening_ranges(top_rect, openings, pixels)
    find_opening_ranges(bottom_rect, openings, pixels)
    
    # deal with error and edge cases
    if len(openings) < 2:
        print "error, unable to successfully find entrance/exit"
        sys.exit()
    elif len(openings) > 2:
        del_flag = [0] * len(openings)
        for i in xrange(len(openings)):
            for j in xrange(i + 1, len(openings)):
                if openings[i].overlap(openings[j]):
                    if openings[i].long_len() > openings[j].long_len():
                        del_flag[j] = 1
                    else:
                        del_flag[i] = 1
            
        openings = [openings[i] for i in xrange(len(del_flag)) if del_flag[i] == 0]
        
    if len(openings) > 2:
            print "error, invalid maze image, too many openings"
            sys.exit()
    
    return openings
    
    
"""
helper method for finding the openings or entrance/exit of the maze
modifies the list of openings

"""
def find_opening_ranges(rect, openings, pixels):
    global PATH_COLOR
    
    height = len(pixels)
    width = len(pixels[0])
    
    start1, end1 = -1, -1
    start2, end2 = -1, -1
    
    if rect.xmax - rect.xmin == 1:
        prev = (1, 0)
        horizontal = False
    else:
        prev = (0, 1)
        horizontal = True
    
    for i in xrange(rect.ymin, rect.ymax):
        for j in xrange(rect.xmin, rect.xmax):
            if pixels[i][j] == PATH_COLOR and start1 == -1:
                start1 = j if horizontal else i
            elif (start1 != -1 and start2 == -1
              and pixels[i - prev[0]][j - prev[1]] == PATH_COLOR and pixels[i][j] != PATH_COLOR):
                end1 = j if horizontal else i
            elif end1 != -1 and start2 == -1 and pixels[i][j] == PATH_COLOR:
                start2 = j if horizontal else i
            elif (start2 != -1 and pixels[i - prev[0]][j - prev[1]] == PATH_COLOR 
              and pixels[i][j] != PATH_COLOR):
                end2 = j if horizontal else i
                break
    
    # append opening to openings list
    # constructor of Rectangle needs (xmin, xmax, ymin, ymax)
    if start1 != -1 and end1 != -1 and horizontal:
        openings.append(Rectangle(start1, end1, rect.ymin, rect.ymax))
    elif start1 != -1 and end1 != -1:
        openings.append(Rectangle(rect.xmin, rect.xmax, start1, end1))
    elif start1 != -1 and horizontal:
        openings.append(Rectangle(start1, width, rect.ymin, rect.ymax))
    elif start1 != -1:
        openings.append(Rectangle(rect.xmin, rect.xmax, start1, height))
        return
    
    if start2 != -1 and end2 != -1 and horizontal:
        openings.append(Rectangle(start2, end2, rect.ymin, rect.ymax))
    elif start2 != -1 and end2 != -1:
        openings.append(Rectangle(rect.xmin, rect.xmax, start2, end2))
    elif start2 != -1 and horizontal:
        openings.append(Rectangle(start2, width, rect.ymin, rect.ymax))
    elif start2 != -1:
        openings.append(Rectangle(rect.xmin, rect.xmax, start2, height))
    
    return

    
"""
finds the shortest path through the maze via BFS, but keeps a certain distance from the walls

"""
def find_path(openings, pixels):
    global PATH_COLOR
    global MARK_PATH
    
    # constants
    LEFT = 1
    RIGHT = 2
    UP = 3
    DOWN = 4
    UNEXPLORED = -1
    
    height = len(pixels)
    width = len(pixels[0])
    
    # for tracing path and avoiding exploring same pixel twice
    # pixels explored will store the index of the previous explored pixel
    # in other words the pixel value points to the pixel it visited in the previous step
    path = [[UNEXPLORED] * width for i in xrange(height)]
    
    # put exit pixel coordinates into set
    exit = set()
    x = openings[1]
    for i in xrange(x.ymin, x.ymax):
        for j in xrange(x.xmin, x.xmax):
            exit.add((i, j))
    
    # perform BFS on maze
    print "searching for shortest path on maze..."
    
    wall_dist = dist_to_wall(pixels)
    side_buffer = min(openings[0].long_len(), openings[1].long_len()) / 2
    
    directions = [(0, -1, LEFT), (0, 1, RIGHT), (-1, 0, UP), (1, 0, DOWN)]
    
    # loop until path found
    for buffer in xrange(side_buffer, 0, -1):
        h = []
        
        # add pixels from first opening to heap
        x = openings[0]
        for i in xrange(x.ymin, x.ymax):
            for j in xrange(x.xmin, x.xmax):
                if wall_dist[i][j] >= buffer:
                    path[i][j] = (i, j)
                    heapq.heappush(h, (0, i, j, 0))
        
        while h:
            data = heapq.heappop(h)
            priority = data[0]
            prev_coord = (data[1], data[2])
            prev_dir = data[3]
            
            for move in directions:
                i = data[1] + move[0]
                j = data[2] + move[1]
                new_dir = move[2]
                
                # check if new pixel coordinate is 
                # 1. out of bounds 2. already explored 3. not part of path 4. if is part of exit
                in_bounds = i >= 0 and i < height and j >= 0 and j < width
                if (in_bounds and path[i][j] == UNEXPLORED and pixels[i][j] == PATH_COLOR 
                  and wall_dist[i][j] >= buffer):
                    path[i][j] = prev_coord
                    # penalize changing directions to prevent diagonal lines
                    new_priority = priority if new_dir == prev_dir else priority + 1
                    heapq.heappush(h, (new_priority, i, j, new_dir))
                    
                    if (i, j) in exit:
                        print "finished searching for shortest path"
                        make_path(pixels, path, (i, j), buffer)
                        
                        return
    
    print "error, no path found in maze"
    sys.exit()
  

"""
calculates each pixel's distance to the wall
used for A* search heuristic
@return wall_dist: list containing pixel's distance to nearest wall

"""
def dist_to_wall(pixels):
    global PATH_COLOR
    UNEXPLORED = -1
    
    height = len(pixels)
    width = len(pixels[0])
    
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
        coord = q.get()
        val = wall_dist[coord[0]][coord[1]]
        
        for x in directions:
            i = coord[0] + x[0]
            j = coord[1] + x[1]
            new_coord = (i, j)
            
            # check if new pixel coordinate is 
            # 1. out of bounds 2. already explored 3. part of path
            in_bounds = i >= 0 and i < height and j >= 0 and j < width
            if in_bounds and wall_dist[i][j] == UNEXPLORED:
                wall_dist[i][j] = val + 1
                q.put(new_coord)
    
    return wall_dist
    
    
"""
draws the shortest path found by the find_path method
modifies the pixel values to highlight and thicken trace
marks pixels that are part of shortest path with value = -1

""" 
def make_path(pixels, path, final_exit, buffer):
    global PATH_COLOR
    global MARK_PATH
    DIR_LEFT = (0, -1)
    DIR_RIGHT = (0, 1)
    
    height = len(pixels)
    width = len(pixels[0])
    
    print "drawing shortest path..."
    
    # traverse backwards to find and mark shortest path
    prev = final_exit
    pixels[prev[0]][prev[1]] = MARK_PATH
    x = path[prev[0]][prev[1]]
    prev_dir = (prev[0] - x[0], prev[1] - x[1])
    
    end = 0
    reach_end = False
    while not reach_end:
        # if direction has changed, color the correct pixels to make path wider
        new_dir = (prev[0] - x[0], prev[1] - x[1])
        if new_dir != prev_dir and buffer >= 2:
            i = prev[0]
            j = prev[1]
            in_bounds = i >= 0 and i < height and j >= 0 and j < width
            
            while in_bounds and pixels[i][j] == -1:
                if prev_dir == DIR_LEFT or prev_dir == DIR_RIGHT:
                    for k in xrange(1, buffer / 2):
                        pixels[i - k][j] = MARK_PATH
                        pixels[i + k][j] = MARK_PATH
                else:
                    for k in xrange(1, buffer / 2):
                        pixels[i][j - k] = MARK_PATH
                        pixels[i][j + k] = MARK_PATH
                
                # update i and j
                i += prev_dir[0]
                j += prev_dir[1]
                in_bounds = i >= 0 and i < height and j >= 0 and j < width
            
            # update direction
            prev_dir = new_dir
        
        # mark trace
        pixels[x[0]][x[1]] = MARK_PATH
        # update variables for traversing
        prev = x
        x = path[x[0]][x[1]]
        
        # exit one iteration after reaching the entrance, for trace drawing purposes
        if x == path[x[0]][x[1]]:
            end += 1
            reach_end = end > 2
    
    return
    

"""
saves maze with shortest path into an image file

"""
def save_image(im, pixels, filename):
    global MARK_PATH

    pixels2 = []
    wall = (0, 0, 0)
    path = (100, 100, 100)
    trace = (0, 255, 0)
    
    for row in pixels:
        for p in row:
            if p == 255:
                pixels2.append(path)
            elif p == MARK_PATH:
                pixels2.append(trace)
            else:
                pixels2.append(wall)
            
    im2 = Image.new(im.mode, im.size)
    im2 = im2.convert("RGB")
    
    im2.putdata(pixels2)
    filename, e = os.path.splitext(filename)
    filename += "_solution.png"
    im2.save(filename, "PNG")
    
    return


"""
main

"""
def main():
    args = sys.argv[1:]
    
    filename = args[0]
      
    try:
        im = Image.open(filename)
    except IOError:
        print "Error in file name"
        print "Please place maze image in the same directory as the script and enter file name"
        sys.exit()
    
    # get pixel values and store to list
    im = im.convert("L")
    pixels = list(im.getdata())
    width, height = im.size
    pixels = [pixels[i * width:(i + 1) * width] for i in xrange(height)]
    
    # crop image
    im = crop_maze(im, pixels)
    pixels = list(im.getdata())
    width, height = im.size
    pixels = [pixels[i * width:(i + 1) * width] for i in xrange(height)]
    
    # find entrance and exit
    openings = find_entrance_exit(pixels)
    
    # find shortest path
    find_path(openings, pixels)
    
    # print image to same directory
    save_image(im, pixels, filename)

    
if __name__ == '__main__':
  main()
