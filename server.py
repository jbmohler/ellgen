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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, dev=True)
