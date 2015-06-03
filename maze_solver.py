
import sys, os
import Queue
from PIL import Image


"""
crops extra white space from the maze image so everything outside of the 
borders are not included

@return : cropped Image file

"""
def crop_maze(width, height, im, pixels):
    left = search_wall_location(1, width, height, pixels)
    top = search_wall_location(2, width, height, pixels)
    right = search_wall_location(3, width, height, pixels)
    bottom = search_wall_location(4, width, height, pixels)
    
    return im.crop((left, top, right, bottom))

    
"""
helper method for cropping the image, searches for location of walls

mode:
    1: left wall
    2: top wall
    3. right wall
    4. bottom wall
    
    corresponding side and mode:
    1/2 2 2/3
    1       3
    1       3
    1       3
    1/4 4 4/3
    
@return: corresponding wall location

"""
def search_wall_location(mode, width, height, pixels):
    # path color is white
    path_color = 255
    
    # for scanning left
    if mode == 1:
        offset = 0
        incr = width
        scan_range = height * incr
        adv = 1
        limit = width
        
    # for scanning top
    elif mode == 2:
        offset = 0
        incr = 1
        scan_range = width
        adv = width
        limit = height * width
        
    # for scanning right
    elif mode == 3:
        offset = width - 1
        incr = width
        scan_range = height * incr
        adv = -1
        limit = -1
        
    # for scanning bottom
    elif mode == 4:
        offset = (height - 1) * width
        incr = 1
        scan_range = width
        adv = -1 * width
        limit = -1
    
    # scan for walls
    while offset != limit:
        for i in xrange(offset, scan_range + offset, incr):
            if pixels[i] != path_color:
                if mode == 1:
                    return offset
                elif mode == 2:
                    return offset / width
                elif mode == 3:
                    return offset + 1
                elif mode == 4:
                    return offset / width + 1
        offset += adv
    
    print "error, invalid maze image"
    sys.exit()

    
"""
finds the entrance and exit of the maze

@return openings: list of location of the openings in format:
                  (start pixel, end pixel, side of wall, edge)

"""
def find_entrance_exit(width, height, pixels):
    openings = []
    
    # scan to find openings
    # 1 for left col, 2 for top row, 3 for right col, 4 for bottom row
    search_side_for_opening(1, width, height, pixels, openings)
    search_side_for_opening(2, width, height, pixels, openings)
    search_side_for_opening(3, width, height, pixels, openings)
    search_side_for_opening(4, width, height, pixels, openings)
    
    """
    corresponding side and mode:
    
    1/2 2 2/3
    1       3
    1       3
    1       3
    1/4 4 4/3
    
    """
    # openings in the format of (start, end, side of opening, edge)
    
    # error handling when >2  or <2 openings are detected
    if len(openings) < 2:
        print "error, can't find entrance/exit"
        sys.exit()
    elif len(openings) > 2:
        temp_opening = []
        opening_edge = []
        
        # an edge case is when an opening is at an edge, will get 2 openings
        # check all edges to see if any are at the same edge
        for i in xrange(0, 5):
            for opening in openings:
                edge = opening[3]
                if edge == 0 and i == 0:
                    temp_opening.append(opening)
                elif edge == i:
                    opening_edge.append(opening)
            
            # if opening is at the edge keep first opening, discard the other
            if len(opening_edge) > 1:
                temp_opening.append(opening_edge[0])
            opening_edge = []
        
        openings = temp_opening
        
        if len(openings) > 2:
            print "error, invalid maze image, too many openings"
            sys.exit()
    
    return openings
    
    
"""
helper method for finding the openings or entrance/exit of the maze
modifies the list of openings
@return: nothing

"""
def search_side_for_opening(mode, width, height, pixels, openings):
    path_color = 255
    
    """
    edges defined as
    1 ---- 2
    |      |
    |      |
    3 ---- 4
    
    openings not at an edge will have edge value as 0
    
    """
    
    start1 = -1
    end1 = -1
    edge1 = 0
    
    start2 = -1
    end2 = -1
    edge2 = 0
    
    # for scanning left
    if mode == 1:
        offset = 0
        incr = width
        scan_range = height * width
        
    # for scanning top
    elif mode == 2:
        offset = 0
        incr = 1
        scan_range = width
        
    # for scanning right
    elif mode == 3:
        offset = width - 1
        incr = width
        scan_range = height * width
        
    # for scanning bottom
    elif mode == 4:
        offset = (height - 1) * width
        incr = 1
        scan_range = width
    
    # scan and find pixel coordinate of openings
    for i in xrange(offset, scan_range + offset, incr):
        if pixels[i] == path_color and start1 == -1:
            start1 = i
            # for edge case where opening starts at an edge
            if i == offset:
                if mode == 1 or mode == 2:
                    edge1 = 1
                elif mode == 3:
                    edge1 = 2
                elif mode == 4:
                    edge1 = 3
                
        elif (start1 != -1 and start2 == -1
              and pixels[i - incr] == path_color and pixels[i] != path_color):
            end1 = i - incr
        elif end1 != -1 and start2 == -1 and pixels[i] == path_color:
            start2 = i
        elif start2 != -1 and pixels[i - incr] == path_color and pixels[i] != path_color:
            end2 = i - incr
            break
            
    if start1 != -1 and end1 != -1:
        openings.append((start1, end1, mode, edge1))
    # for case if opening is at edge
    elif start1 != -1:
        if mode == 1:
            end1 = scan_range - 1
            edge1 = 3
        elif mode == 2:
            end1 = scan_range - 1
            edge1 = 2
        elif mode == 3:
            end1 = scan_range - 1
            edge1 = 4
        elif mode == 4:
            end1 = offset + scan_range - 1
            edge1 = 4
        openings.append((start1, end1, mode, edge1))
        
    if start2 != -1 and end2 != -1:
        openings.append((start2, end2, mode, edge2))
    # for case if 2nd opening is at edge
    elif start2 != -1:
        if mode == 1:
            end2 = scan_range - 1
            edge2 = 3
        elif mode == 2:
            end2 = scan_range - 1
            edge2 = 2
        elif mode == 3:
            end2 = scan_range - 1
            edge2 = 4
        elif mode == 4:
            end2 = offset + scan_range - 1
            edge2 = 4
        openings.append((start2, end2, mode, edge2))

    return

    
"""
finds the shortest path through the maze, and calls make_path to draw it
to the list of pixel values

"""
def find_path(openings, width, height, pixels):
    size = width * height
    path_color = 255
    
    # for tracing path and avoiding exploring same pixel twice
    # pixels explored will store the index of the previous explored pixel
    # in other words the pixel value points to the pixel it recently visited
    path = [-1] * size
    
    # put exit pixel coordinates into set
    exit = set()
    if openings[1][2] == 2 or openings[1][2] == 4:
        for x in xrange(openings[1][0], openings[1][1] + 1):
            exit.add(x)
    else:
        for x in xrange(openings[1][0], openings[1][1] + width, width):
            exit.add(x)
    
    
    # perform BFS on maze
    q = Queue.Queue()
    print "running BFS on maze..."
    
    # add pixels from first opening to queue for BFS
    if openings[0][2] == 2 or openings[0][2] == 4:
        for x in xrange(openings[0][0], openings[0][1] + 1):
            path[x] = x
            q.put(x)
    else:
        for x in xrange(openings[0][0], openings[0][1] + width, width):
            path[x] = x
            q.put(x)
    
    while not q.empty():
        coor = q.get()
        
        left = coor - 1
        top = coor - width
        right = coor + 1
        bottom = coor + width
        
        # check if new pixel coordinate is 
        # 1. out of bounds 2. already explored 3. not part of path 4. if is part of exit
        if left >= 0 and path[left] == -1 and pixels[left] == path_color:
            path[left] = coor
            q.put(left)
            if left in exit:
                final_exit = left
                break
        if top >= 0 and path[top] == -1 and pixels[top] == path_color:
            path[top] = coor
            q.put(top)
            if top in exit:
                final_exit = top
                break
        if right < size and path[right] == -1 and pixels[right] == path_color:
            path[right] = coor
            q.put(right)
            if right in exit:
                final_exit = right
                break
        if bottom < size and path[bottom] == -1 and pixels[bottom] == path_color:
            path[bottom] = coor
            q.put(bottom)
            if bottom in exit:
                final_exit = bottom
                break
    
    if q.empty():
        print "error, no path found in maze"
        sys.exit()
        
    print "finished searching for shortest path"
    make_path(pixels, path, final_exit, width, height)
    
    return
    
    
"""
draws the shortest path found by the find_path method
modifies the pixel values to highlight and thicken trace
marks pixels that are part of shortest path with value = -1

""" 
def make_path(pixels, path, final_exit, width, height):
    size = width * height
    path_color = 255
    print "drawing shortest path..."
    
    # traverse backwards to find and mark shortest path
    prev = final_exit
    pixels[prev] = -1
    x = path[prev]
    diff = prev - x
    wall_at_side = 0
    
    """
    wall_at_side:
    0: none
    1: top
    2: bottom
    3: left
    4: right
    5: above and below or left and right
    
    coordinates of pixels nearby regarding x:
    
           x - width
              ^
              |
    x - 1 <-- x --> x + 1
              |
              v
           x + width
         
    """
    
    exit = 0
    # exit one iteration after reaching the entrance, for trace drawing purposes
    while exit <= 2:
    
        # if direction has changed, color the correct pixels to make path wider
        if prev - x != diff:
            retrace = prev
            while retrace >= 0 and retrace < size and pixels[retrace] == -1:
                if wall_at_side == 1:
                    pixels[retrace + width] = -1
                    pixels[retrace + 2 * width] = -1
                elif wall_at_side == 2:
                    pixels[retrace - width] = -1
                    pixels[retrace - 2 * width] = -1
                elif wall_at_side == 3:
                    pixels[retrace + 1] = -1
                    pixels[retrace + 2] = -1
                elif wall_at_side == 4:
                    pixels[retrace - 1] = -1
                    pixels[retrace - 2] = -1
                retrace += diff
                
            # reinitialize wall and diff after retracing and thickening trace
            wall_at_side = 0
            diff = prev - x
        
        # for traces going left/right, check above and below for walls/out of bounds
        if diff == 1 or diff == -1:
            top_out = x - width < 0 or pixels[x - width] != path_color and pixels[x - width] != -1
            bottom_out = (x + width >= size or pixels[x + width] != path_color 
                          and pixels[x + width] != -1)
            
            if wall_at_side == 0 and top_out and bottom_out:
                wall_at_side = 5
            elif wall_at_side == 0 and top_out: 
                wall_at_side = 1
            elif wall_at_side == 0 and bottom_out: 
                wall_at_side = 2
            elif wall_at_side == 1 and bottom_out:
                wall_at_side = 5
            elif wall_at_side == 2 and top_out:
                wall_at_side = 5
                
        # for traces going up or down, check left/right for walls/out of bounds
        else:
            left_out = x - 1 < 0 or pixels[x - 1] != path_color and pixels[x - 1] != -1
            right_out = x + 1 >= size or pixels[x + 1] != path_color and pixels[x + 1] != -1
            
            if wall_at_side == 0 and left_out and right_out: 
                wall_at_side = 5
            elif wall_at_side == 0 and left_out: 
                wall_at_side = 3
            elif wall_at_side == 0 and right_out: 
                wall_at_side = 4
            elif wall_at_side == 3 and right_out:
                wall_at_side = 5
            elif wall_at_side == 4 and left_out:
                wall_at_side = 5
        
        # mark trace
        pixels[x] = -1
        # update variables for traversing
        prev = x
        x = path[x]
        
        # exit condition
        if x == path[x]:
            exit += 1
    
    return

 
"""
saves maze with shortest path into an image file

"""
def save_image(im, pixels, filename):
    pixels2 = []
    wall = (0, 0, 0)
    path = (100, 100, 100)
    trace = (0, 255, 0)
    
    for p in pixels:
        if p == 255:
            pixels2.append(path)
        elif p == -1:
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
shows image for debugging purposes

"""
def show_image(im, pixels):
    pixels2 = []
    wall = (0, 0, 0)
    path = (100, 100, 100)
    trace = (0, 255, 0)
    # print pixels
    
    for p in pixels:
        if p == 255:
            pixels2.append(path)
        elif p == -1:
            pixels2.append(trace)
        else:
            pixels2.append(wall)
            
    im2 = Image.new(im.mode, im.size)
    im2 = im2.convert("RGB")
    
    # print pixels
    im2.putdata(pixels2)
    im2.show()
    
    return
   
   
"""
prints openings for debugging purposes

"""
def show_opening(pixels, width, openings, im):

    start = openings[0][0]
    end = openings[0][1]
    mode = openings[0][2]
    if mode == 2 or mode == 4:
        for x in xrange(start, end + 1):
            pixels[x] = -1
            
    else:
        for x in xrange(start, end + width, width):
            pixels[x] = -1
        
    show_image(im, pixels)
   
   
"""
main

"""
def main():
    args = sys.argv[1:]
    
    if args == []:
        print "Please place maze image in the same directory as the script and enter file name"
        filename = raw_input()
    else:
        filename = args[0]
    
    while True:    
        try:
            im = Image.open(filename)
            break
        except IOError:
            print "Error in file name"
            print "Please place maze image in the same directory as the script and enter file name"
            filename = raw_input()
    
    # get pixel values and store to list
    im = im.convert("L")
    pixels = list(im.getdata())
    width, height = im.size
    
    # crop image
    im = crop_maze(width, height, im, pixels)
    pixels = list(im.getdata())
    width, height = im.size
    
    # find entrance and exit
    openings = find_entrance_exit(width, height, pixels)
    
    # find shortest path
    find_path(openings, width, height, pixels)
    
    # print image to same directory
    save_image(im, pixels, filename)
    # show_image(im, pixels)

    
if __name__ == '__main__':
  main()
