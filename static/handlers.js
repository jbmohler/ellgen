function EllipseModel() {
  this.foci = [];
  this.boundaries = null;

  this.appendFoci = function (x, y) {
    this.foci.push({ x, y });
  };
}

const model = new EllipseModel();

function start_things() {
  const viewport = document.getElementById("viewport");
  viewport.addEventListener("click", click_canvas);

  window.onresize = () => resizeCanvasToDisplaySize(viewport);

  resizeCanvasToDisplaySize(viewport);
}

function resizeCanvasToDisplaySize(canvas) {
  // look up the size the canvas is being displayed
  const width = canvas.clientWidth;
  const height = canvas.clientHeight;

  // If it's resolution does not match change it
  if (canvas.width !== width || canvas.height !== height) {
    canvas.width = width;
    canvas.height = height;

    redraw_canvas(model);

    return true;
  }

  return false;
}

function get_ellipse_boundary(model) {
  const request = new Request("/api/compute", {
    method: "POST",
    body: JSON.stringify(model.foci),
  });

  fetch(request)
    .then((response) => response.json())
    .then((boundaries) => {
      model.boundaries = boundaries;
      redraw_canvas(model);
    });
}

function draw_puddle_lines(model) {
  const request = new Request("/api/compute", {
    method: "POST",
    body: JSON.stringify(model.foci),
  });

	await new Promise(r => setTimeout(r, 2000));


  fetch(request)
    .then((response) => response.json())
    .then((boundaries) => {
      model.boundaries = boundaries;
      redraw_canvas(model);
    });
}

function redraw_canvas(model) {
  ctx = viewport.getContext("2d");

  ctx.clearRect(0, 0, viewport.width, viewport.height);

  for (let foci of model.foci) {
    ctx.beginPath();
    ctx.arc(foci.x, foci.y, 5, 0, Math.PI * 2);
    ctx.closePath();
    ctx.fill();
  }

  if (model.boundaries && model.boundaries.length >= 1) {
    for (const boundary of model.boundaries) {
      ctx.beginPath();
      let bp = boundary.points[0];
      ctx.moveTo(bp.x, bp.y);
      for (bp of boundary.points.slice(1)) {
        ctx.lineTo(bp.x, bp.y);
      }
      ctx.closePath();
      ctx.strokeStyle = boundary.color;
      ctx.stroke();
    }
  }
}

function click_canvas(event) {
  const rect = viewport.getBoundingClientRect();
  const x = event.clientX - rect.left;
  const y = event.clientY - rect.top;
  model.appendFoci(x, y);

  redraw_canvas(model);
  // get_ellipse_boundary(model);
  draw_puddle_lines(model);
}
