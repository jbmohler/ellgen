import sanic
import compute

app = sanic.Sanic(__name__)

app.static('/static', './static', name="get_static_files")
app.static('/index.html', './index.html', name="get_index_html")


@app.post("/api/compute", name="post_api_compute")
def post_api_compute(request):
    foci = [(f['x'], f['y']) for f in request.json]

    if len(foci) == 1:
        return sanic.response.json([])

    maxes = (
            max(f[0] for f in foci),  max(f[1] for f in foci), 
            )

    C = len(foci)* 150

    print(maxes, C)

    b = compute.compute_boundary(foci, C, (0, 0), (maxes[0]*2, maxes[1]*2))

    b = [{'x': bp[0], 'y': bp[1]} for bp in b]
    print(b)
    return sanic.response.json(b)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000, dev=True)
