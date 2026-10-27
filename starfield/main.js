import { starfieldConfig } from "./starfield.config.js";

const CONTOUR_STREAM_URL = `http://${location.hostname}:8001/contours`;
const IMAGE_BYTES_STREAM_URL = `http://${location.hostname}:8001/image_bytes`;

const STROKE_COLOR = "cyan";
const STROKE_WIDTH = 2;
const CENTROID_COLOR = "magenta";
const CENTROID_RADIUS = 6;

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

  if (centroid) {
    drawCentroid(ctx, centroid, sx, sy);
  }
}

function drawContours(ctx, { w, h, contours, gradient, canvas }) {
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  const sx = canvas.width / w;
  const sy = canvas.height / h;

  contours.forEach((contour) => {
    drawContour(ctx, contour, sx, sy, gradient, canvas);
  });
  const container = tsParticles.item(0);
  container.options = starfieldConfig(contours?.length);
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

const FRAME_HEADER_SIZE = 12;
const STREAM_RETRY_MS = 1000;

function drawMask(ctx, canvas, offscreen, gray, w, h) {
  if (offscreen.width !== w || offscreen.height !== h) {
    offscreen.width = w;
    offscreen.height = h;
  }

  const rgba = new Uint8ClampedArray(w * h * 4);
  for (let i = 0; i < gray.length; i++) {
    rgba[i * 4] = rgba[i * 4 + 1] = rgba[i * 4 + 2] = gray[i];
    rgba[i * 4 + 3] = gray[i];
  }

  offscreen.getContext("2d").putImageData(new ImageData(rgba, w, h), 0, 0);
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.drawImage(offscreen, 0, 0, canvas.width, canvas.height);
}

async function connectImageBytesStream(canvas, ctx) {
  const response = await fetch(IMAGE_BYTES_STREAM_URL);
  const reader = response.body.getReader();
  const offscreen = document.createElement("canvas");
  let buffer = new Uint8Array(0);

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;

    const merged = new Uint8Array(buffer.length + value.length);
    merged.set(buffer);
    merged.set(value, buffer.length);
    buffer = merged;

    while (buffer.length >= FRAME_HEADER_SIZE) {
      const view = new DataView(buffer.buffer, buffer.byteOffset);
      const w = view.getUint32(0, true);
      const h = view.getUint32(4, true);
      const len = view.getUint32(8, true);
      if (buffer.length < FRAME_HEADER_SIZE + len) break;

      const gray = buffer.subarray(FRAME_HEADER_SIZE, FRAME_HEADER_SIZE + len);
      drawMask(ctx, canvas, offscreen, gray, w, h);
      buffer = buffer.slice(FRAME_HEADER_SIZE + len);
    }
  }
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
  await tsParticles.load({ id: "starfield", options: starfieldConfig(250) });

  const { canvas, ctx } = setupCanvas();
  // connectContourStream(canvas, ctx);
  keepImageBytesStreamConnected(canvas, ctx);
}

// The Python server may not be listening yet when the page loads, or may restart,
// so keep reconnecting the way EventSource does on its own
async function keepImageBytesStreamConnected(canvas, ctx) {
  while (true) {
    try {
      await connectImageBytesStream(canvas, ctx);
    } catch (error) {
      console.warn("Image bytes stream unavailable, retrying:", error.message);
    }
    await new Promise((resolve) => setTimeout(resolve, STREAM_RETRY_MS));
  }
}

start().catch((error) => console.error("Failed to start starfield:", error));
