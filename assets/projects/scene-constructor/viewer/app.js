const state = {
  metadata: null,
  images: [],
  imageUrls: [],
  playing: false,
  speed: 4,
  opacity: 0.9,
  time: 0,
  previousFrame: performance.now(),
  activeSegment: -1,
  completedCount: -1,
  ready: false,
  animationHandle: null,
};

const ui = {
  play: document.querySelector("#play"),
  reverse: document.querySelector("#reverse"),
  timeline: document.querySelector("#timeline"),
  speed: document.querySelector("#speed"),
  speedValue: document.querySelector("#speed-value"),
  opacity: document.querySelector("#opacity"),
  opacityValue: document.querySelector("#opacity-value"),
  follow: document.querySelector("#follow"),
  reset: document.querySelector("#reset"),
  clock: document.querySelector("#clock"),
  utc: document.querySelector("#utc"),
  canvas: document.querySelector("#active-canvas"),
};
const context = ui.canvas.getContext("2d");

const map = new maplibregl.Map({
  container: "map",
  center: [-79, 35],
  zoom: 4,
  attributionControl: false,
  style: {
    version: 8,
    sources: {
      osm: {
        type: "raster",
        tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
        tileSize: 256,
        attribution: "© OpenStreetMap contributors",
      },
    },
    layers: [{ id: "osm", type: "raster", source: "osm" }],
  },
});
map.addControl(new maplibregl.NavigationControl(), "top-right");
map.addControl(new maplibregl.AttributionControl({ compact: true }), "bottom-right");
// Register immediately so image preloading cannot race past MapLibre's
// one-time load event.
const mapReady = new Promise(resolve => {
  if (map.loaded()) resolve();
  else map.once("load", resolve);
});

const markerElement = document.createElement("div");
markerElement.className = "satellite-marker";
const marker = new maplibregl.Marker({ element: markerElement, anchor: "center" });

function loadImage(url) {
  return new Promise((resolve, reject) => {
    const image = new Image();
    image.onload = () => resolve(image);
    image.onerror = () => reject(new Error(`Unable to load ${url}`));
    image.src = url;
  });
}

function formatElapsed(seconds) {
  const minutes = Math.floor(seconds / 60).toString().padStart(2, "0");
  const remainder = (seconds % 60).toFixed(2).padStart(5, "0");
  return `${minutes}:${remainder}`;
}

function interpolateTrack(seconds) {
  const track = state.metadata.track;
  const step = track[1][0] - track[0][0];
  const lowerIndex = Math.min(track.length - 2, Math.max(0, Math.floor(seconds / step)));
  const lower = track[lowerIndex];
  const upper = track[lowerIndex + 1];
  const fraction = Math.max(0, Math.min(1, (seconds - lower[0]) / (upper[0] - lower[0])));
  return lower.map((value, index) => index === 0 ? seconds : value + (upper[index] - value) * fraction);
}

function setCompletedLayers(count) {
  if (count === state.completedCount) return;
  state.metadata.segments.forEach((segment, index) => {
    map.setPaintProperty(
      `segment-layer-${index}`,
      "raster-opacity",
      index < count ? state.opacity : 0,
    );
  });
  state.completedCount = count;
}

function setActiveSegment(index) {
  if (index === state.activeSegment) return;
  state.activeSegment = index;
  context.clearRect(0, 0, ui.canvas.width, ui.canvas.height);
  if (index < 0 || index >= state.metadata.segments.length) return;
  const image = state.images[index];
  ui.canvas.width = image.naturalWidth;
  ui.canvas.height = image.naturalHeight;
  map.getSource("active-acquisition").setCoordinates(
    state.metadata.segments[index].coordinates,
  );
}

function render() {
  const metadata = state.metadata;
  if (!metadata) return;
  const atEnd = state.time >= metadata.duration_seconds;
  const segmentIndex = atEnd
    ? metadata.segments.length
    : Math.max(0, Math.floor(state.time / metadata.slice_seconds));
  setCompletedLayers(segmentIndex);

  if (atEnd) {
    setActiveSegment(-1);
    context.clearRect(0, 0, ui.canvas.width, ui.canvas.height);
  } else {
    setActiveSegment(segmentIndex);
    const segment = metadata.segments[segmentIndex];
    const image = state.images[segmentIndex];
    const fraction = Math.max(0, Math.min(1, (state.time - segment.start) / (segment.end - segment.start)));
    const rows = Math.round(image.naturalHeight * fraction);
    context.clearRect(0, 0, ui.canvas.width, ui.canvas.height);
    if (rows > 0) {
      context.drawImage(image, 0, 0, image.naturalWidth, rows, 0, 0, ui.canvas.width, rows);
    }
    map.setPaintProperty("active-layer", "raster-opacity", state.opacity);
  }

  const track = interpolateTrack(state.time);
  const center = [track[1], track[2]];
  const scanLine = [[track[3], track[4]], [track[5], track[6]]];
  marker.setLngLat(center);
  map.getSource("scan-line").setData({
    type: "Feature",
    geometry: { type: "LineString", coordinates: scanLine },
    properties: {},
  });
  if (ui.follow.checked) map.easeTo({ center, duration: 0 });

  ui.timeline.value = state.time;
  ui.clock.value = formatElapsed(state.time);
  ui.utc.value = new Date(new Date(metadata.start_time).getTime() + state.time * 1000)
    .toISOString().replace(".000Z", "Z");
}

function animationFrame(now) {
  if (!state.ready) {
    state.animationHandle = null;
    return;
  }
  const elapsed = Math.min(0.1, Math.max(0, (now - state.previousFrame) / 1000));
  state.previousFrame = now;
  if (state.playing) {
    state.time += elapsed * state.speed;
    if (state.time <= 0 || state.time >= state.metadata.duration_seconds) {
      state.time = Math.max(0, Math.min(state.metadata.duration_seconds, state.time));
      state.playing = false;
      ui.play.textContent = "▶";
    }
  }
  render();
  state.animationHandle = state.playing
    ? requestAnimationFrame(animationFrame)
    : null;
}

function startPlayback() {
  if (!state.ready || !state.playing || state.animationHandle !== null) return;
  state.previousFrame = performance.now();
  state.animationHandle = requestAnimationFrame(animationFrame);
}

function fullRoute() {
  map.fitBounds(state.metadata.bounds, { padding: 65, duration: 700 });
}

function initialFollowView() {
  // Three zoom levels equal eight times the original linear map scale.
  map.fitBounds(state.metadata.bounds, { padding: 65, duration: 0 });
  const routeZoom = map.getZoom();
  const initialTrack = state.metadata.track[0];
  map.jumpTo({
    center: [initialTrack[1], initialTrack[2]],
    zoom: Math.min(map.getMaxZoom(), routeZoom + 3),
  });
}

ui.play.addEventListener("click", () => {
  if (!state.ready) return;
  if (state.speed === 0) {
    state.speed = 1;
    ui.speed.value = 1;
    ui.speedValue.value = "1×";
  }
  if (state.time >= state.metadata.duration_seconds && state.speed > 0) {
    state.time = 0;
  }
  state.playing = !state.playing;
  ui.play.textContent = state.playing ? "❚❚" : "▶";
  startPlayback();
});
ui.reverse.addEventListener("click", () => {
  if (!state.ready) return;
  if (state.time <= 0) state.time = state.metadata.duration_seconds;
  state.speed = -Math.max(1, Math.abs(state.speed));
  ui.speed.value = state.speed;
  ui.speedValue.value = `${state.speed}×`;
  state.playing = true;
  ui.play.textContent = "❚❚";
  startPlayback();
});
ui.timeline.addEventListener("input", event => {
  state.time = Number(event.target.value);
  render();
});
ui.speed.addEventListener("input", event => {
  state.speed = Number(event.target.value);
  ui.speedValue.value = `${state.speed}×`;
});
ui.opacity.addEventListener("input", event => {
  state.opacity = Number(event.target.value);
  ui.opacityValue.value = `${Math.round(state.opacity * 100)}%`;
  state.completedCount = -1;
  render();
});
ui.follow.addEventListener("change", () => {
  if (ui.follow.checked) render();
});
ui.reset.addEventListener("click", () => {
  ui.follow.checked = false;
  fullRoute();
});

async function initialize() {
  const [response, indexResponse, imageryResponse] = await Promise.all([
    fetch("acquisition.json"),
    fetch("imagery-index.json"),
    fetch("imagery.bin"),
  ]);
  if (!response.ok) throw new Error(`Unable to load acquisition.json (${response.status})`);
  if (!indexResponse.ok) throw new Error(`Unable to load imagery-index.json (${indexResponse.status})`);
  if (!imageryResponse.ok) throw new Error(`Unable to load imagery.bin (${imageryResponse.status})`);
  state.metadata = await response.json();
  const imageIndex = await indexResponse.json();
  const imagery = await imageryResponse.arrayBuffer();
  state.imageUrls = imageIndex.map(item => URL.createObjectURL(new Blob(
    [imagery.slice(item.offset, item.offset + item.length)],
    { type: item.type },
  )));
  ui.timeline.max = state.metadata.duration_seconds;
  state.images = await Promise.all(state.imageUrls.map(loadImage));

  await mapReady;
  state.metadata.segments.forEach((segment, index) => {
    map.addSource(`segment-${index}`, {
      type: "image",
      url: state.imageUrls[index],
      coordinates: segment.coordinates,
    });
    map.addLayer({
      id: `segment-layer-${index}`,
      type: "raster",
      source: `segment-${index}`,
      paint: { "raster-opacity": 0, "raster-fade-duration": 0 },
    });
  });
  const firstImage = state.images[0];
  ui.canvas.width = firstImage.naturalWidth;
  ui.canvas.height = firstImage.naturalHeight;
  map.addSource("active-acquisition", {
    type: "canvas",
    canvas: "active-canvas",
    animate: true,
    coordinates: state.metadata.segments[0].coordinates,
  });
  map.addLayer({
    id: "active-layer",
    type: "raster",
    source: "active-acquisition",
    paint: { "raster-opacity": state.opacity, "raster-fade-duration": 0 },
  });
  const initialTrack = state.metadata.track[0];
  map.addSource("scan-line", {
    type: "geojson",
    data: {
      type: "Feature",
      geometry: {
        type: "LineString",
        coordinates: [
          [initialTrack[3], initialTrack[4]],
          [initialTrack[5], initialTrack[6]],
        ],
      },
      properties: {},
    },
  });
  map.addLayer({
    id: "scan-line-layer",
    type: "line",
    source: "scan-line",
    paint: { "line-color": "#6effac", "line-width": 3, "line-opacity": 0.95 },
  });
  // A marker must have a valid LngLat before addTo(); otherwise MapLibre
  // attempts to read .lng from an undefined position.
  marker.setLngLat([initialTrack[1], initialTrack[2]]).addTo(map);
  initialFollowView();
  state.ready = true;
  ui.play.disabled = false;
  ui.reverse.disabled = false;
  ui.timeline.disabled = false;
  state.completedCount = -1;
  render();
}

initialize().catch(error => {
  console.error(error);
});
