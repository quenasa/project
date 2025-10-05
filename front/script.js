// @ts-nocheck
/* global L */
// Leaflet (L) is loaded via CDN in index.html

// Ensure a loader exists
let loader = document.querySelector(".loader")
if (!loader) {
  loader = document.createElement("div")
  loader.className = "loader"
  loader.textContent = "Loading heatmap data..."
  document.body.appendChild(loader)
}

// Declare the L variable before using it
const L = window.L

// Initialize map
const map = L.map("heatmapContainer").setView([40.4168, -3.7038], 6)

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 18,
  attribution: "© OpenStreetMap contributors",
}).addTo(map)

// Legend control
const legendControl = L.control({ position: "bottomleft" })
legendControl.onAdd = () => {
  const div = L.DomUtil.create("div", "legend")
  div.innerHTML = `
    <b>Air Quality Index (AQI)</b><br />
    <span style="background:#440154"></span> Very low<br />
    <span style="background:#31688e"></span> Low–moderate<br />
    <span style="background:#35b779"></span> Moderate–high<br />
    <span style="background:#fde725"></span> High<br />
    <span style="background:#f0f921"></span> Very high
  `
  L.DomEvent.disableClickPropagation(div)
  return div
}
legendControl.addTo(map)

// Fallback sample data (lat, lng, aqi)
const fallback = [
  { lat: 40.4168, lng: -3.7038, aqi: 80 }, // Madrid
  { lat: 41.3851, lng: 2.1734, aqi: 60 }, // Barcelona
  { lat: 37.3891, lng: -5.9845, aqi: 30 }, // Sevilla
  { lat: 39.4699, lng: -0.3763, aqi: 50 }, // Valencia
]

function aggregatePoints(raw, precision) {
  const buckets = new Map()
  for (const p of raw) {
    const latR = Number(p.lat.toFixed(precision))
    const lngR = Number(p.lng.toFixed(precision))
    const key = `${latR},${lngR}`
    if (!buckets.has(key)) buckets.set(key, { latSum: 0, lngSum: 0, metricSum: 0, count: 0 })
    const b = buckets.get(key)
    const metric = Number(p.metric ?? 0)
    b.latSum += p.lat
    b.lngSum += p.lng
    b.metricSum += metric
    b.count += 1
  }
  const points = []
  for (const [, b] of buckets) {
    const lat = b.latSum / b.count
    const lng = b.lngSum / b.count
    const avgMetric = b.metricSum / b.count
    // use dataset-specific cap to compute intensity
    const intensity = Math.min(avgMetric / metricCap, 1)
    points.push([lat, lng, intensity])
  }
  return points
}

let heatLayer = null
function createHeatForZoom(rawData, zoom) {
  let precision
  if (zoom <= 6) precision = 1
  else if (zoom <= 9) precision = 2
  else precision = 3

  const points = aggregatePoints(rawData, precision)

  let radius, blur, minOpacity
  if (zoom <= 5) {
    radius = 30
    blur = 20
    minOpacity = 0.4
  } else {
    radius = 50
    blur = 20
    minOpacity = 0.5
  }

  // Viridis palette (perceptually-uniform) - 5 stops
  return L.heatLayer(points, {
    radius,
    blur,
    minOpacity,
    gradient: {
      1.0: "#440154", // deep purple
      0.75: "#31688e",
      0.5: "#35b779",
      0.25: "#fde725",
      0.0: "#f0f921", // bright yellow (top)
    },
  })
}

// Preload datasets so switching is instant. Store normalized arrays under datasets[file]
const datasetFiles = ["our_index.json", "air_quality.json", "poverty.json", "water_quality.json"]
const datasets = {} // filename -> normalized array

async function fetchAndNormalize(file) {
  try {
  const res = await fetch("/data/" + file)
    if (!res.ok) throw new Error("no data")
    const data = await res.json()
    return normalize(data, file)
  } catch (e) {
    console.warn("Failed to load", file, e)
    // return a normalized fallback using fallback raw and mapping for air_quality
    return normalize(fallback, "air_quality.json")
  }
}

// mapping function: returns array of {lat,lng,metric}
function normalize(data, file) {
  if (!Array.isArray(data)) return []
  if (file === "air_quality.json") return data.map((d) => ({ lat: d.lat, lng: d.lng, metric: Number(d.aqi ?? 0) }))
  if (file === "poverty.json")
    return data.map((d) => ({ lat: d.lat, lng: d.lng, metric: Number((d.value ?? 0) * 100) })) // fraction -> percent
  if (file === "water_quality.json") return data.map((d) => ({ lat: d.lat, lng: d.lng, metric: Number(d.wqi ?? 0) }))
  // our_index.json assumed 0..1 -> scale to 0..100 for visualization
  return data.map((d) => ({ lat: d.lat, lng: d.lng, metric: Number((d.index ?? 0) * 100) }))
}

// load all datasets once
async function preloadAll() {
  const promises = datasetFiles.map((f) =>
    fetchAndNormalize(f).then((arr) => {
      datasets[f] = arr
    }),
  )
  await Promise.all(promises)
}

// Current normalized data reference
let currentNormalized = null
let zoomTimeout = null
let metricCap = 100

function renderNormalized(norm) {
  if (!norm || norm.length === 0) {
    console.warn("No data to render")
    return
  }
  // Update legend title based on selected dataset
  const sel = document.getElementById("datasetSelect")
  const selVal = sel ? sel.value : "our_index.json"
  const legendDiv = document.querySelector(".legend")
  if (legendDiv) {
    if (selVal === "air_quality.json") legendDiv.querySelector("b").textContent = "Air Quality Index (AQI)"
    else if (selVal === "poverty.json") legendDiv.querySelector("b").textContent = "Poverty (%)"
    else if (selVal === "water_quality.json") legendDiv.querySelector("b").textContent = "Water Quality Index"
    else legendDiv.querySelector("b").textContent = "Our index"
  }

  console.log("Rendering dataset:", selVal, "points:", norm.length)
  // compute min/max of metric for this dataset
  const metrics = norm.map((d) => Number(d.metric || 0))
  const minMetric = Math.min(...metrics)
  const maxMetric = Math.max(...metrics)
  // dynamic scaling: map min->0 and max->cap (or 100) to full intensity range
  const cap = selVal === "air_quality.json" ? 200 : 100
  metricCap = cap
  const scaleMin = minMetric
  const scaleMax = Math.max(maxMetric, 1)

  // apply dynamic normalization to create a metric field normalized to 0..cap
  const dyn = norm.map((d) => ({
    lat: d.lat,
    lng: d.lng,
    metric: ((Number(d.metric || 0) - scaleMin) / (scaleMax - scaleMin)) * cap,
  }))
  currentNormalized = dyn
  const newHeat = createHeatForZoom(currentNormalized, map.getZoom())
  if (heatLayer) {
    try {
      map.removeLayer(heatLayer)
    } catch (e) {
      /* ignore */
    }
  }
  // ensure map has correct size before adding layer
  try {
    map.invalidateSize()
  } catch (e) {
    /* ignore */
  }
  heatLayer = newHeat.addTo(map)

  // Update legend with stats
  if (legendDiv) {
    const stats = document.createElement("div")
    stats.style.fontSize = "12px"
    stats.style.marginTop = "6px"
    stats.textContent = `min: ${minMetric.toFixed(1)} • max: ${maxMetric.toFixed(1)} • cap: ${metricCap}`
    // remove old stats if present
    const old = legendDiv.querySelector(".legend-stats")
    if (old) old.remove()
    stats.className = "legend-stats"
    legendDiv.appendChild(stats)
  }
}

// Single zoom handler uses currentNormalized
function onZoomEnd() {
  if (zoomTimeout) clearTimeout(zoomTimeout)
  zoomTimeout = setTimeout(() => {
    if (!currentNormalized) return
    const z = map.getZoom()
    const h = createHeatForZoom(currentNormalized, z)
    if (heatLayer) map.removeLayer(heatLayer)
    heatLayer = h.addTo(map)
  }, 200)
}

map.on("zoomend", onZoomEnd)

// --- City search / geocoding (Nominatim) ---
const cityForm = document.getElementById("cityForm")
const cityInput = document.getElementById("cityInput")
const cityGoBtn = document.getElementById("cityGoBtn")
let cityMarker = null

async function searchCity(q) {
  if (!q) return
  const params = new URLSearchParams({ q, format: "json", addressdetails: "1", limit: "1" })
  const url = "https://nominatim.openstreetmap.org/search?" + params.toString()
  console.log("Geocoding query:", q, url)
  try {
    cityInput.disabled = true
    if (cityGoBtn) cityGoBtn.disabled = true
    const res = await fetch(url, { headers: { "Accept-Language": "en" } })
    console.log("Geocode response status:", res.status)
    if (!res.ok) throw new Error("Geocode request failed: " + res.status)
    const results = await res.json()
    console.log("Geocode results:", results)
    if (!results || results.length === 0) {
      alert('No results found for "' + q + '"')
      return
    }
    const first = results[0]
    const lat = Number(first.lat)
    const lon = Number(first.lon)
    if (Number.isNaN(lat) || Number.isNaN(lon)) {
      alert('Received invalid coordinates for "' + q + '"')
      return
    }
    map.flyTo([lat, lon], 12, { animate: true })
    if (cityMarker)
      try {
        map.removeLayer(cityMarker)
      } catch (err) {
        /* ignore */
      }
    cityMarker = L.marker([lat, lon]).addTo(map)
    const displayName = first.display_name || q
    cityMarker.bindPopup("<strong>" + displayName + "</strong>").openPopup()
  } catch (err) {
    console.error("Geocoding error", err)
    alert("Could not geocode the city. Check your network or open the browser console for details.")
  } finally {
    if (cityInput) cityInput.disabled = false
    if (cityGoBtn) cityGoBtn.disabled = false
  }
}

if (cityForm && cityInput) {
  // ensure form won't cause navigation even if JS binding fails
  cityForm.addEventListener("submit", (e) => {
    e.preventDefault()
  })
}
if (cityGoBtn && cityInput) {
  cityGoBtn.addEventListener("click", () => {
    const q = cityInput.value && cityInput.value.trim()
    if (!q) return
    searchCity(q)
  })
  // also allow Enter key inside the input to trigger the search
  cityInput.addEventListener("keydown", (ev) => {
    if (ev.key === "Enter") {
      ev.preventDefault()
      const q = cityInput.value && cityInput.value.trim()
      if (!q) return
      searchCity(q)
    }
  })
}

// initial preload and render
preloadAll().then(() => {
  // hide loader
  if (loader) loader.style.display = "none"
  console.log("Datasets preloaded:", Object.keys(datasets))
  const sel = document.getElementById("datasetSelect")
  const start = sel ? sel.value : "our_index.json"
  renderNormalized(datasets[start] || [])
})

// Re-load when dataset selection changes (instant because data is preloaded)
const selector = document.getElementById("datasetSelect")
if (selector) {
  selector.addEventListener("change", () => {
    // show loader briefly
    if (loader) loader.style.display = "block"
    const v = selector.value
    console.log("Dataset switched to", v)
    // if dataset already loaded use it, otherwise fetch and normalize
    if (datasets[v]) {
      // small timeout to allow loader to be visible
      setTimeout(() => {
        if (loader) loader.style.display = "none"
        renderNormalized(datasets[v])
      }, 120)
    } else {
      fetchAndNormalize(v).then((arr) => {
        datasets[v] = arr
        if (loader) loader.style.display = "none"
        renderNormalized(arr)
      })
    }
  })
}

// Optional: poll current dataset for live updates every 15s
const pollInterval = 5000 // ms (faster for testing)
setInterval(() => {
  const sel = document.getElementById("datasetSelect")
  const v = sel ? sel.value : "our_index.json"
  fetch("/data/" + v)
    .then((r) => {
      if (r.ok) return r.json()
      throw new Error("no")
    })
    .then((data) => {
      const arr = normalize(data, v)
      datasets[v] = arr
      // if currently displayed dataset, re-render with fresh values
      if (currentNormalized && sel && sel.value === v) renderNormalized(arr)
    })
    .catch(() => {
      /* ignore polling errors */
    })
}, pollInterval)

// Refresh button
const refreshBtn = document.getElementById("refreshDataset")
if (refreshBtn) {
  refreshBtn.addEventListener("click", () => {
    const sel = document.getElementById("datasetSelect")
    const v = sel ? sel.value : "our_index.json"
    console.log("Manual refresh requested for", v)
  fetch("/data/" + v)
      .then((r) => {
        if (r.ok) return r.json()
        throw new Error("no")
      })
      .then((data) => {
        const arr = normalize(data, v)
        datasets[v] = arr
        renderNormalized(arr)
      })
      .catch((err) => {
        console.warn("Refresh failed", err)
      })
  })
}

// --- FAQ desplegable ---
const faqItems = document.querySelectorAll(".faq-item")
faqItems.forEach((item) => {
  const question = item.querySelector(".faq-question")
  if (!question) return
  question.addEventListener("click", () => {
    faqItems.forEach((other) => {
      if (other !== item) other.classList.remove("active")
    })
    item.classList.toggle("active")
  })
})

// Report form handling
const reportForm = document.querySelector(".report-form")
if (reportForm) {
  reportForm.addEventListener("submit", (e) => {
    e.preventDefault()
    alert("¡Gracias! Tu reporte ha sido enviado correctamente.")
    reportForm.reset()
  })
}

const hero = document.querySelector(".hero")
if (hero) {
  hero.addEventListener("mousemove", (e) => {
    const rect = hero.getBoundingClientRect()
    const x = e.clientX - rect.left
    const y = e.clientY - rect.top

    // Calculate percentages (0-100)
    const xPercent = (x / rect.width) * 100
    const yPercent = (y / rect.height) * 100

    // Create dynamic gradient based on mouse position
    // Shift hue and position based on cursor location (subtler range)
    // Use narrower offsets so the gradient changes more gently
    const hue1 = 175 + (xPercent / 100) * 20 // 180-200 (teal to cyan subtle)
    const hue2 = 195 + (yPercent / 100) * 20 // 195-215 (cyan to blue subtle)
    const hue3 = 205 + ((xPercent + yPercent) / 200) * 20 // 205-225 (blue to purple subtle)

    hero.style.background = `
      radial-gradient(circle at ${xPercent}% ${yPercent}%, 
        hsla(${hue1}, 70%, 35%, 1) 0%, 
        hsla(${hue2}, 65%, 40%, 1) 30%, 
        hsla(${hue3}, 60%, 30%, 1) 100%
      )
    `
  })

  // Reset to default gradient when mouse leaves
  hero.addEventListener("mouseleave", () => {
    hero.style.background = ""
  })
}