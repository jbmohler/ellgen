import sys
import json
import subprocess
from PIL import Image, ImageDraw
import numpy
import compute


def drawpoints(im, points, drawdefn):
    draw = ImageDraw.Draw(im)

    frad = numpy.array([3, 3])

    color = drawdefn["color"]
    rad = drawdefn.get("radius", 1)

    for f in points:
        rect = (*list(f - rad * frad), *list(f + rad * frad))
        draw.ellipse(rect, fill=color)


def drawbounds(im, boundaries, color):
    draw = ImageDraw.Draw(im)

    draw.polygon(list(numpy.concatenate(boundaries).ravel()), outline=color, width=3)


if __name__ == "__main__":
    if len(sys.argv) >= 1:
        with open(sys.argv[1], "r") as ff:
            content = json.load(ff)
    else:
        x = input("Number of foci: ")
        foci = []
        for i in range(int(x)):
            pnt = input(f"point #{i+1}:  ")

            px, py = pnt.split(",")
            foci.append([float(px), float(py)])

        layers = [
            (1.1, "#e00000"),
            (1.3, "#004080"),
            (1.7, "#800040"),
            (2.1, "#804000"),
        ]

        content = {
            "foci": foci,
            "layers": [{"factor": f, "color": c} for f, c in layers],
        }

    canvas_size = (1000, 1000)

    im = Image.new("RGB", canvas_size, "white")

    for ellipse in content:
        foci = [numpy.array([px, py]) for px, py in ellipse["foci"]]

        Mrep = compute.foci_centroid(foci, None)

        Mdist = compute.foci_f(foci, Mrep)

        mrdefn = ellipse.get("draw_mrep")
        if mrdefn:
            drawpoints(im, [Mrep], mrdefn)

        dfdefn = ellipse.get("draw_foci")
        if dfdefn:
            drawpoints(im, foci, dfdefn)

        for layer in ellipse["layers"]:
            M = layer["factor"] * Mdist
            bound = compute.compute_boundary(foci, M, (0, 0), canvas_size)

            drawbounds(im, bound, layer["color"])

    outfile = "test.png"
    im.save(outfile)

    subprocess.run(["xdg-open", outfile], capture_output=True)
