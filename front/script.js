// Clean, single-script implementation
// @ts-nocheck
/* global L */

const L = window.L

// loader
let loaderElem = document.querySelector('.loader')
if (!loaderElem) {
  loaderElem = document.createElement('div')
  loaderElem.className = 'loader'
  loaderElem.textContent = 'Loading heatmap data...'
  document.body.appendChild(loaderElem)
}

const map = L.map('heatmapContainer').setView([20, 0], 2)
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  maxZoom: 18,
  attribution: '© OpenStreetMap contributors',
}).addTo(map)

const legendControl2 = L.control({ position: 'bottomleft' })
legendControl2.onAdd = () => {
  const div = L.DomUtil.create('div', 'legend')
  div.innerHTML = '<b>Value</b>'
  L.DomEvent.disableClickPropagation(div)
  return div
}
legendControl2.addTo(map)

let heatLayerMain = null
let currentNormalized = []
let metricCap = 100

function aggregatePointsMain(raw, precision = 1) {
  const buckets = new Map()
  for (const p of raw) {
    if (!p || typeof p.lat !== 'number' || typeof p.lng !== 'number') continue
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
    const intensity = Math.max(0, Math.min(avgMetric / metricCap, 1))
    points.push([lat, lng, intensity])
  }
  return points
}

function createHeatMain(rawData, zoom) {
  let precision = 1
  if (zoom <= 3) precision = 0
  else if (zoom <= 6) precision = 1
  else if (zoom <= 9) precision = 2
  else precision = 3

  const points = aggregatePointsMain(rawData, precision)
  const radius = zoom <= 5 ? 25 : 40
  const blur = 20
  const minOpacity = 0.4
  return L.heatLayer(points, {
    radius,
    blur,
    minOpacity,
    gradient: {
      0.0: '#f0f921',
      0.25: '#fde725',
      0.5: '#35b779',
      0.75: '#31688e',
      1.0: '#440154',
    },
  })
}

function clearHeatMain() {
  if (heatLayerMain) {
    try { map.removeLayer(heatLayerMain) } catch (e) {}
    heatLayerMain = null
  }
}

function renderNormalizedMain(norm, label) {
  if (!Array.isArray(norm) || norm.length === 0) {
    console.warn('No data to render for', label)
    clearHeatMain()
    return
  }
  const metrics = norm.map(d => Number(d.metric || 0)).filter(n => Number.isFinite(n))
  if (metrics.length === 0) {
    console.warn('No numeric metrics to render for', label)
    clearHeatMain()
    return
  }
  const minMetric = Math.min(...metrics)
  const maxMetric = Math.max(...metrics)
  metricCap = Math.max(1, maxMetric)

  currentNormalized = norm.map(d => ({ lat: d.lat, lng: d.lng, metric: Number(d.metric || 0) }))

  const newHeat = createHeatMain(currentNormalized, map.getZoom())
  clearHeatMain()
  try { map.invalidateSize() } catch (e) {}
  heatLayerMain = newHeat.addTo(map)

  const legendDiv = document.querySelector('.legend')
  if (legendDiv) {
    legendDiv.innerHTML = `<b>${label}</b>`
    const stats = document.createElement('div')
    stats.className = 'legend-stats'
    stats.style.fontSize = '12px'
    stats.style.marginTop = '6px'
    stats.textContent = `min: ${minMetric.toFixed(2)} • max: ${maxMetric.toFixed(2)} • cap: ${metricCap}`
    legendDiv.appendChild(stats)
  }
}

map.on('zoomend', () => {
  if (!currentNormalized || currentNormalized.length === 0) return
  const z = map.getZoom()
  const h = createHeatMain(currentNormalized, z)
  clearHeatMain()
  heatLayerMain = h.addTo(map)
})

// Load heatmap.json and build datasets
let countriesIndex = {}
let datasetsMain = { temperature: [], co2: [], poverty: [], education: [] }
let countriesLayer = null

function buildDatasetsMain(json) {
  const arr = Array.isArray(json.countries) ? json.countries : []
  countriesIndex = {}
  datasetsMain = { temperature: [], co2: [], poverty: [], education: [] }
  // remove old countries layer if present
  if (countriesLayer) {
    try { map.removeLayer(countriesLayer) } catch (e) {}
    countriesLayer = null
  }
  const markers = []
  for (const c of arr) {
    const name = (c.country || '').trim()
    const iso3 = (c.iso3 || '').trim()
    if (!name && !iso3) continue
    const lat = Array.isArray(c.coordinates) && typeof c.coordinates[0] === 'number' ? c.coordinates[0] : null
    const lng = Array.isArray(c.coordinates) && typeof c.coordinates[1] === 'number' ? c.coordinates[1] : null
    // store both name and iso3 indexed lowercase for flexible search
    if (name) countriesIndex[name.toLowerCase()] = c
    if (iso3) countriesIndex[iso3.toLowerCase()] = c

    // helper to coerce numbers safely
    const num = (v) => {
      if (v === null || v === undefined) return NaN
      const n = Number(v)
      return Number.isFinite(n) ? n : NaN
    }

    // temperature
    if (c.environmental && c.environmental.temperature) {
      const t = num(c.environmental.temperature.value)
      if (!Number.isNaN(t) && lat !== null && lng !== null) datasetsMain.temperature.push({ lat, lng, metric: t })
    }
    // co2
    if (c.environmental && c.environmental.co2) {
      const x = num(c.environmental.co2.value)
      if (!Number.isNaN(x) && lat !== null && lng !== null) datasetsMain.co2.push({ lat, lng, metric: x })
    }
    // poverty (socioeconomic.poverty_index.value)
    if (c.socioeconomic && c.socioeconomic.poverty_index) {
      const p = num(c.socioeconomic.poverty_index.value)
      if (!Number.isNaN(p) && lat !== null && lng !== null) datasetsMain.poverty.push({ lat, lng, metric: p })
    }
    // education (school_enrollment)
    if (c.socioeconomic && c.socioeconomic.school_enrollment) {
      const e = num(c.socioeconomic.school_enrollment.value)
      if (!Number.isNaN(e) && lat !== null && lng !== null) datasetsMain.education.push({ lat, lng, metric: e })
    }

    // create an invisible interactive marker for hover tooltip (use country-level data)
    if (lat !== null && lng !== null) {
      const m = L.circleMarker([lat, lng], {
        radius: 6,
        color: '#000',
        weight: 0,
        opacity: 0,
        fillOpacity: 0,
        interactive: true,
      })
      // prepare tooltip content dynamically on hover
      m.on('mouseover', (ev) => {
        const lines = []
        const nameDisplay = (c.country || c.iso3 || 'Unknown')
        lines.push(`<strong>${nameDisplay}</strong>`)
        const t = c.environmental && c.environmental.temperature && c.environmental.temperature.value
        if (Number.isFinite(Number(t)) && Number(t) !== 0) lines.push(`Temperature: ${Number(t).toFixed(1)} °C`)
        const co2 = c.environmental && c.environmental.co2 && c.environmental.co2.value
        if (Number.isFinite(Number(co2)) && Number(co2) !== 0) lines.push(`CO2: ${Number(co2).toFixed(1)} ppm`)
        const pov = c.socioeconomic && c.socioeconomic.poverty_index && c.socioeconomic.poverty_index.value
        if (Number.isFinite(Number(pov)) && Number(pov) !== 0) lines.push(`Poverty: ${Number(pov).toFixed(1)} %`)
        const edu = c.socioeconomic && c.socioeconomic.school_enrollment && c.socioeconomic.school_enrollment.value
        if (Number.isFinite(Number(edu)) && Number(edu) !== 0) lines.push(`Education: ${Number(edu).toFixed(1)}`)
        const html = lines.join('<br/>') || `<strong>${nameDisplay}</strong><br/>No data available`
        m.bindTooltip(html, { direction: 'top', offset: [0, -8], opacity: 0.95 }).openTooltip()
      })
      m.on('mouseout', () => {
        try { m.closeTooltip() } catch (e) {}
      })
      markers.push(m)
    }
  }
  if (markers.length > 0) {
    countriesLayer = L.layerGroup(markers)
    countriesLayer.addTo(map)
  }
}

async function loadHeatmapMain() {
  try {
    const res = await fetch('/data/world_heatmap.json')
    if (!res.ok) throw new Error('Failed to load heatmap.json: ' + res.status)
    const json = await res.json()
    buildDatasetsMain(json)
    if (loaderElem) loaderElem.style.display = 'none'
  if (datasetsMain.temperature.length > 0) renderNormalizedMain(datasetsMain.temperature, 'Temperature (°C)')
  else if (datasetsMain.co2.length > 0) renderNormalizedMain(datasetsMain.co2, 'CO2 (ppm)')
  else if (datasetsMain.poverty.length > 0) renderNormalizedMain(datasetsMain.poverty, 'Poverty Index (%)')
  else if (datasetsMain.education.length > 0) renderNormalizedMain(datasetsMain.education, 'Education (school enrollment)')
  } catch (e) {
    console.error(e)
    if (loaderElem) loaderElem.textContent = 'Failed to load data.'
  }
}

loadHeatmapMain()

// Country-only search
const cityInputElem = document.getElementById('cityInput')
const cityGoBtnElem = document.getElementById('cityGoBtn')
let countryMarker = null

function findCountryByNameMain(q) {
  if (!q) return null
  const name = q.trim().toLowerCase()
  if (countriesIndex[name]) return countriesIndex[name]
  for (const k of Object.keys(countriesIndex)) {
    if (k.includes(name)) return countriesIndex[k]
  }
  return null
}

function searchCountryMain(q) {
  if (!q) return
  const c = findCountryByNameMain(q)
  if (!c) { alert('Country not found in data: ' + q); return }
  const lat = Array.isArray(c.coordinates) ? c.coordinates[0] : null
  const lng = Array.isArray(c.coordinates) ? c.coordinates[1] : null
  if (typeof lat !== 'number' || typeof lng !== 'number') { alert('Country coordinates not available for ' + c.country); return }
  map.flyTo([lat, lng], 5, { animate: true })
  if (countryMarker) try { map.removeLayer(countryMarker) } catch (e) {}
  countryMarker = L.marker([lat, lng]).addTo(map)
  countryMarker.bindPopup(`<strong>${c.country}</strong>`).openPopup()
}

if (cityGoBtnElem && cityInputElem) cityGoBtnElem.addEventListener('click', () => searchCountryMain(cityInputElem.value))
if (cityInputElem) cityInputElem.addEventListener('keydown', (ev) => { if (ev.key === 'Enter') { ev.preventDefault(); searchCountryMain(cityInputElem.value) } })

const selectorElem = document.getElementById('datasetSelect')
if (selectorElem) selectorElem.addEventListener('change', () => {
  const v = selectorElem.value
  if (v === 'temperature') renderNormalizedMain(datasetsMain.temperature, 'Temperature (°C)')
  else if (v === 'co2') renderNormalizedMain(datasetsMain.co2, 'CO2 (ppm)')
  else if (v === 'poverty') renderNormalizedMain(datasetsMain.poverty, 'Poverty Index (%)')
  else if (v === 'education') renderNormalizedMain(datasetsMain.education, 'Education (school enrollment)')
})

// FAQ toggle
document.querySelectorAll('.faq-item').forEach(item => {
  const q = item.querySelector('.faq-question')
  if (!q) return
  q.addEventListener('click', () => item.classList.toggle('active'))
})

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

function smoothScroll(target, duration = 1500) { // 1500 ms = 1.5s
  const start = window.scrollY;
  const end = target.getBoundingClientRect().top + start;
  const distance = end - start;
  let startTime = null;

  function animation(currentTime) {
    if (!startTime) startTime = currentTime;
    const timeElapsed = currentTime - startTime;
    const run = easeInOutQuad(timeElapsed, start, distance, duration);
    window.scrollTo(0, run);
    if (timeElapsed < duration) requestAnimationFrame(animation);
  }

  // Easing para que se vea más natural
  function easeInOutQuad(t, b, c, d) {
    t /= d / 2;
    if (t < 1) return (c / 2) * t * t + b;
    t--;
    return (-c / 2) * (t * (t - 2) - 1) + b;
  }

  requestAnimationFrame(animation);
}

// Usa este en lugar del comportamiento nativo:
document.querySelectorAll('a[href^="#"]').forEach(link => {
  link.addEventListener('click', e => {
    e.preventDefault();
    const target = document.querySelector(link.getAttribute('href'));
    if (target) smoothScroll(target, 2000); // puedes cambiar 2000 para más o menos tiempo
  });
});
