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

def foci_f(foci, pnt):
    return sum([dist2(foci[i]-pnt) for i in range(len(foci))])

def foci_f_x(foci, pnt):
    return sum([(pnt[0]-foci[i][0])/dist2(foci[i]-pnt) for i in range(len(foci)) if dist2(foci[i]-pnt)>=0.0001])

def foci_f_xx(foci, pnt):
    return sum([(pnt[1]-foci[i][1])**2/dist2(foci[i]-pnt)**3 for i in range(len(foci)) if dist2(foci[i]-pnt)>=0.0001])

def foci_f_y(foci, pnt):
    return sum([(pnt[1]-foci[i][1])/dist2(foci[i]-pnt) for i in range(len(foci)) if dist2(foci[i]-pnt)>=0.0001])

def foci_f_yy(foci, pnt):
    return sum([(pnt[0]-foci[i][0])**2/dist2(foci[i]-pnt)**3 for i in range(len(foci)) if dist2(foci[i]-pnt)>=0.0001])

def foci_centroid(foci):
    pnt = numpy.array((0, 0))
    while abs(foci_f_y(foci, pnt)) + abs(foci_f_x(foci, pnt)) > 0.001:
        print(pnt, foci_f(foci, pnt), foci_f_x(foci, pnt), foci_f_y(foci, pnt))
        if abs(foci_f_y(foci, pnt)) < abs(foci_f_x(foci, pnt)):
            x = -foci_f_x(foci, pnt)/foci_f_xx(foci, pnt) + pnt[0]
            y = pnt[1]
        else:
            x = pnt[0]
            y = -foci_f_y(foci, pnt)/foci_f_yy(foci, pnt) + pnt[1]
        pnt = numpy.array([x, y])
    return pnt[0], pnt[1]

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
            if foci_f(foci, midpoint) < C:
                inner = midpoint
            else:
                outer = midpoint
        boundary.append(inner)
    return boundary

def compute_boundary(foci, C, ctl, cbr):
    center = sum(numpy.array(foci))/len(foci)
    if foci_f(foci, center) < C:
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
