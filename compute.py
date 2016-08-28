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

PROXIMITY = 0.1

def foci_f_x(foci, pnt):
    return sum([(pnt[0]-foci[i][0])/dist2(foci[i]-pnt) for i in range(len(foci)) if dist2(foci[i]-pnt)>=PROXIMITY])

def foci_f_y(foci, pnt):
    return sum([(pnt[1]-foci[i][1])/dist2(foci[i]-pnt) for i in range(len(foci)) if dist2(foci[i]-pnt)>=PROXIMITY])

def foci_f_xx(foci, pnt):
    return sum([(pnt[1]-foci[i][1])**2/dist2(foci[i]-pnt)**3 for i in range(len(foci)) if dist2(foci[i]-pnt)>=PROXIMITY])

def foci_f_yy(foci, pnt):
    return sum([(pnt[0]-foci[i][0])**2/dist2(foci[i]-pnt)**3 for i in range(len(foci)) if dist2(foci[i]-pnt)>=PROXIMITY])

def foci_centroid_newton(foci):
    # This method is based on Newton's method in either the x or y direction.
    # It appears to work, but I believe the minimum is too shallow and
    # convergence is numerically unstable.
    pnt = sum(numpy.array(foci))/len(foci)
    while abs(foci_f_y(foci, pnt)) + abs(foci_f_x(foci, pnt)) > 0.001:
        if abs(foci_f_y(foci, pnt)) < abs(foci_f_x(foci, pnt)):
            if abs(foci_f_xx(foci, pnt)) <= 0.01:
                break
            x = -foci_f_x(foci, pnt)/foci_f_xx(foci, pnt) + pnt[0]
            y = pnt[1]
        else:
            if abs(foci_f_yy(foci, pnt)) <= 0.01:
                break
            x = pnt[0]
            y = -foci_f_y(foci, pnt)/foci_f_yy(foci, pnt) + pnt[1]
        pnt = numpy.array([x, y])
    return pnt[0], pnt[1]

def foci_directional_derivative(foci, t, base, dirvec):
    pnt = numpy.array(base)+numpy.array(dirvec)*t
    return sum([((pnt[0]-foci[i][0])*dirvec[0]+(pnt[1]-foci[i][1])*dirvec[1])/dist2(foci[i]-pnt) for i in range(len(foci)) if dist2(foci[i]-pnt)>=PROXIMITY])

def foci_centroid(foci, line):
    if len(foci) == 1:
        return foci[0]
    base = sum(numpy.array(foci))/len(foci)
    band = max([dist2(foci[i]-base) for i in range(len(foci))])*2
    dirvec = numpy.array([math.cos(1.), math.sin(1.)]) # arbitrary direction
    basex = base+[1, 1]
    while dist2(basex-base) > PROXIMITY:
        basex = base
        gp = lambda t, foci=foci, base=base, dirvec=dirvec: foci_directional_derivative(foci, t, base, dirvec)
        # find minimum of g for t in [-band, band]
        l1, l2 = -band, band

        ### DIAGNOSTICS ####
        # ep1 = base+dirvec*l1
        # ep2 = base+dirvec*l2
        # print('line:  ', ep1, ep2)
        # print(base, dirvec)
        # for ss in range(41):
        #     ss = (ss-20)/20. * band
        #     p = base+dirvec*ss
        #     print('p=({:5.1f}, {:5.1f});  g({:5.1f})={:5.1f};  gp({:5.1f})={:5.1f}'.format(p[0], p[1], ss, foci_f(foci, p), ss, gp(ss)))
        # line(ep1, ep2)
        while abs(l1-l2) > PROXIMITY**2:
            assert gp(l1)*gp(l2) < 0.
            m = (l1+l2)/2.
            if abs(gp(m)) < 0.00001:
                break
            if gp(m)*gp(l1) > 0:
                l1 = m
            else:
                l2 = m
        base = base+dirvec*m
        dirvec = numpy.array([dirvec[1], -dirvec[0]])
    return base

def _compute_boundary_centered(foci, C, cent):
    boundary = []
    r1 = (C - sum([dist2(fc-cent) for fc in foci]))/len(foci)
    r2 = C - min([dist2(fc-cent) for fc in foci])
    iterations = int(math.log2((r2-r1)/PROXIMITY**2))
    for _theta in range(400):
        theta = _theta/400.*2*math.pi
        dirvec = numpy.array([math.cos(theta), math.sin(theta)])
        inner = cent + r1*dirvec
        outer = cent + r2*dirvec
        for i in range(iterations):
            midpoint = (inner+outer)/2.
            if foci_f(foci, midpoint) < C:
                inner = midpoint
            else:
                outer = midpoint
        boundary.append(inner)
    return boundary

def compute_boundary(foci, C, ctl, cbr):
    cent = foci_centroid(foci, lambda:None)
    if foci_f(foci, cent) < C:
        return _compute_boundary_centered(foci, C, cent)
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
