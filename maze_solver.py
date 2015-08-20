
import sys, os
import Maze
from PIL import Image

PATH_COLOR = 255 # equivalent to the color white
MARK_PATH = -1


"""
The Rectangle class is made for 2 uses
1. to represent borders of maze image
2. to represent openings (exit and entrance) in maze image. The class 
    outlines the boundaries of the openings and make iterating 
    easy using a for loop as seen in the methods:
    find_openings()
    find_entrance_exit()

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
This method crops extra white space from the borders of the maze image
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
    
    for i in xrange(height):
        for j in xrange(width):
            if pixels[i][j] != PATH_COLOR:
                xmin = min(j, xmin)
                xmax = max(j, xmax)
                ymin = min(i, ymin)
                ymax = max(i, ymax)
    
    if xmin == width:
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
        # for the special case in which the opening is at an edge, there will
        # be two openings recorded. for the program I choose to delete the
        # smaller one of the two
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
This method is a helper method for finding the openings/entrance/exit
in the maze image
It directly modifies the list of openings by appending the openings

The variable rect is of the type Rectangle and represents one the 
four borders of the maze image (depending on which one is passed in
in the find_entrance_exit() method)

"""
def find_opening_ranges(rect, openings, pixels):
    global PATH_COLOR
    
    height = len(pixels)
    width = len(pixels[0])
    
    horizontal = rect.xmax - rect.xmin != 1
    
    xlast, ylast = -1, -1 # last wall location
    
    for i in xrange(rect.ymin, rect.ymax):
        for j in xrange(rect.xmin, rect.xmax):
            if pixels[i][j] != PATH_COLOR: # wall hit
                if horizontal and xlast != j - 1:
                    openings.append(Rectangle(xlast + 1, j, rect.ymin, rect.ymax))
                elif not horizontal and ylast != i - 1:
                    openings.append(Rectangle(rect.xmin, rect.xmax, ylast + 1, i))
                ylast = i
                xlast = j
            
    if horizontal and xlast != rect.xmax - 1:
        openings.append(Rectangle(xlast + 1, rect.xmax, rect.ymin, rect.ymax))
    elif not horizontal and ylast != rect.ymax - 1:
        openings.append(Rectangle(rect.xmin, rect.xmax, ylast + 1, rect.ymax))
    
    return
    

"""
saves maze with shortest path into a PNG file

"""
def save_image(im, pixels, filename):
    global MARK_PATH

    pixels2 = []
    wall = (0, 0, 0)        # color black
    path = (100, 100, 100)  # color gray (works well visually with green path)
    trace = (0, 255, 0)     # color green
    
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
    # convert to list to 2D
    pixels = [pixels[i * width:(i + 1) * width] for i in xrange(height)]
    
    # crop image
    im = crop_maze(im, pixels)
    pixels = list(im.getdata())
    width, height = im.size
    pixels = [pixels[i * width:(i + 1) * width] for i in xrange(height)]
    
    # find entrance and exit
    openings = find_entrance_exit(pixels)
    
    # calls the Maze class to process maze image and find shortest path
    maze = Maze.Maze(openings, pixels)
    maze.find_path()
    
    # print image to same directory
    save_image(im, pixels, filename)

    
if __name__ == '__main__':
  main()
