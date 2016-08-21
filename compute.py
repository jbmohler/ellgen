import os
import math
import numpy

dist2 = lambda x: math.sqrt(x[0]**2+x[1]**2)

CANVAS_SIZE = 10
foci = numpy.array([[3, 3], [3, -3], [-3, 3], [-3, -3]])
C = 20.5

def _compute_boundary_random(foci, C, ctl, cbr):
    points = 100000
    x = numpy.random.uniform(ctl[0], cbr[0], points)
    y = numpy.random.uniform(ctl[1], cbr[1], points)
    scatter = numpy.array([p for p in zip(x, y)])
    #scatter = numpy.array([[1.2, 1]])

    #print(foci)

    fd = [numpy.apply_along_axis(dist2, 1, scatter-foci[i]) for i in range(len(foci))]
    distances = sum(fd)
    boundary = scatter[numpy.logical_and(distances<C+.1, distances>C-.1)]
    #print(scatter[])

    return boundary

def _foci_sum(pnt, foci):
    return sum([dist2(foci[i]-pnt) for i in range(len(foci))])

def _compute_boundary_centered(foci, C, ctl, cbr):
    center = sum(numpy.array(foci))/len(foci)
    boundary = []
    iterations = int(math.log(C*2000))
    for _theta in range(400):
        theta = _theta/400.*2*math.pi
        inner = center
        outer = center + C*numpy.array([math.cos(theta), math.sin(theta)])
        for i in range(iterations):
            midpoint = (inner+outer)/2.
            if _foci_sum(midpoint, foci) < C:
                inner = midpoint
            else:
                outer = midpoint
        boundary.append(inner)
    return boundary

def compute_boundary(foci, C, ctl, cbr):
    center = sum(numpy.array(foci))/len(foci)
    if _foci_sum(center, foci) < C:
        return _compute_boundary_centered(foci, C, ctl, cbr)
    else:
        return _compute_boundary_random(foci, C, ctl, cbr)

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
