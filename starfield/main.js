import { starfieldConfig } from "./starfield.config.js";

const CONTOUR_STREAM_URL = `http://${location.hostname}:8001/contours`;
const STROKE_COLOR = "cyan";
const STROKE_WIDTH = 2;
const CENTROID_COLOR = "magenta";
const CENTROID_RADIUS = 6;

// Drawing a shape on the screen by connecting the dots sent from the processed image contours
function drawPolygon(ctx, points, sx, sy, gradient) {
  ctx.beginPath();

  points.forEach(([x, y], i) => {
    const method = i === 0 ? "moveTo" : "lineTo";
    ctx[method](x * sx, y * sy);
  });

  ctx.closePath();
  ctx.strokeStyle = gradient;
  ctx.lineWidth = STROKE_WIDTH;
  ctx.stroke();
}

function drawCentroid(ctx, [x, y], sx, sy) {
  ctx.beginPath();
  ctx.arc(x * sx, y * sy, CENTROID_RADIUS, 0, Math.PI * 2);
  ctx.fillStyle = CENTROID_COLOR;
  ctx.fill();
}

function drawContour(ctx, { points, centroid }, sx, sy, gradient, canvas) {
  if (!points || points.length === 0) {
    return;
  }

  points.forEach(([x, y]) => {
    const gradient = ctx.createLinearGradient(
      0,
      0,
      canvas.width,
      canvas.height,
    );
    gradient.addColorStop(0, "blue");
    gradient.addColorStop(0.5, "purple");
    gradient.addColorStop(1, "white");
    ctx.fillStyle = gradient;

    ctx.fillRect(x * sx, y * sy, 25, 25);
  });

  drawPolygon(ctx, points, sx, sy, gradient);

  // if (centroid) {
  // drawCentroid(ctx, centroid, sx, sy);
  // }
}

function drawContours(ctx, { w, h, contours, gradient, canvas }) {
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  const sx = canvas.width / w;
  const sy = canvas.height / h;

  contours.forEach((contour) => {
    drawContour(ctx, contour, sx, sy, gradient, canvas);
  });
  const container = tsParticles.item(0);
  container.options = starfieldConfig(contours?.length)
  if (container) {
    container.refresh();
  }
}

function connectContourStream(canvas, ctx) {
  const source = new EventSource(CONTOUR_STREAM_URL);
  const gradient = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
  gradient.addColorStop(0, "blue");
  gradient.addColorStop(0.5, "purple");
  gradient.addColorStop(1, "white");

  source.onmessage = (event) => {
    drawContours(ctx, { ...JSON.parse(event.data), gradient, canvas });
  };
}

function setupCanvas() {
  const canvas = document.getElementById("canvas");
  const ctx = canvas.getContext("2d");

  function resize() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  }
  resize();
  window.addEventListener("resize", resize);

  return { canvas, ctx };
}

async function start() {
  await loadSlim(tsParticles);
  await tsParticles.load({ id: "starfield", options: starfieldConfig(2) });

  const { canvas, ctx } = setupCanvas();
  connectContourStream(canvas, ctx);
}

start().catch((error) => console.error("Failed to start starfield:", error));
