import sanic
import compute

app = sanic.Sanic(__name__)

app.static("/static", "./static", name="get_static_files")
app.static("/index.html", "./index.html", name="get_index_html")


@app.post("/api/compute", name="post_api_compute")
def post_api_compute(request):
    foci = [(f["x"], f["y"]) for f in request.json]

    maxes = (
        max(f[0] for f in foci),
        max(f[1] for f in foci),
    )

    layers = [
        (100, "#e00000"),
        (150, "#004080"),
        (250, "#800040"),
        (350, "#804000"),
    ]

    boundaries = []

    for cmult, color in layers:
        C = len(foci) * cmult
        btuples = compute.compute_boundary(
            foci, C, (0, 0), (maxes[0] * 2, maxes[1] * 2)
        )

        if len(btuples):
            b = {"points": [{"x": bp[0], "y": bp[1]} for bp in btuples], "color": color}
            boundaries.append(b)

    return sanic.response.json(boundaries)


@app.post("/api/statistics", name="post_api_statistics")
def post_api_statistics(request):
    foci = [(f["x"], f["y"]) for f in request.json]

    if len(foci) == 0:
        raise sanic.exceptions.SanicException("need at least one foci", status_code=400)

    centroid = compute.foci_centroid(foci, lambda: None)

    minlength = compute.foci_f(foci, centroid)

    stats = { 'centroid': {'x': centroid[0], 'y': centroid[1]}, 'minlength': minlength }

    return sanic.response.json(stats)

@app.post("/api/boundary-by-hyperrad", name="post_api_boundary_by_hyperrad")
def post_api_boundary_by_hyperrad(request):
    foci = [(f["x"], f["y"]) for f in request.json['foci']]
    hyperrad = request.json['hyperrad']

    maxes = (
        max(f[0] for f in foci),
        max(f[1] for f in foci),
    )

    btuples = compute.compute_boundary( foci, hyperrad, (0, 0), (maxes[0] * 2, maxes[1] * 2))

    b = {"points": [{"x": bp[0], "y": bp[1]} for bp in btuples]}

    return sanic.response.json(b)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, dev=True)
