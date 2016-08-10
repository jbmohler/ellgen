import os
import math
import numpy

dist2 = lambda x: math.sqrt(x[0]**2+x[1]**2)

CANVAS_SIZE = 10
foci = numpy.array([[3, 3], [3, -3], [-3, 3], [-3, -3]])
C = 20.5

def compute_boundary(foci, C):
    points = 100000
    scatter = numpy.random.uniform(-CANVAS_SIZE/2, CANVAS_SIZE/2, points).reshape(points//2, 2)
    #scatter = numpy.array([[1.2, 1]])

    #print(foci)

    fd = [numpy.apply_along_axis(dist2, 1, scatter-foci[i]) for i in range(len(foci))]
    distances = sum(fd)
    boundary = scatter[numpy.logical_and(distances<C+.1, distances>C-.1)]
    #print(scatter[])

    return boundary

def write_png(boundary, foci, granularity=20):
    from PIL import Image, ImageDraw

    im = Image.new('RGB', (CANVAS_SIZE*granularity, CANVAS_SIZE*granularity), 'white')
    def p2pixel(pnt):
        x = (pnt[0]+CANVAS_SIZE/2, pnt[1]+CANVAS_SIZE/2)
        return (int(x[0]*granularity), int(x[1]*granularity))

    for p in boundary:
        im.putpixel(p2pixel(p), (0, 0, 255))
    for i in range(len(foci)):
        im.putpixel(p2pixel(foci[i]), (255, 0, 0))

    im.save('three-ellipse.png')
    os.system('xdg-open three-ellipse.png')

GRANULARITY = 20
if __name__ == '__main__':
    write_png(boundary, foci, granularity=GRANULARITY)
