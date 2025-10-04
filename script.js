// Enhanced script using leaflet.heat to match workinh-map.html behavior.

document.addEventListener('DOMContentLoaded', () => {
  // Ensure a loader exists
  let loader = document.querySelector('.loader');
  if (!loader) {
    loader = document.createElement('div');
    loader.className = 'loader';
    loader.textContent = 'Loading heatmap data...';
    document.body.appendChild(loader);
  }

  // Initialize map
  const map = L.map('heatmapContainer').setView([40.4168, -3.7038], 6);

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18,
    attribution: '© OpenStreetMap contributors'
  }).addTo(map);

  // Legend control
  const legendControl = L.control({ position: 'bottomleft' });
  legendControl.onAdd = function () {
    const div = L.DomUtil.create('div', 'legend');
    div.innerHTML = `
      <b>Air Quality Index (AQI)</b><br />
      <span style="background:#2ecc71"></span> Good (0–50)<br />
      <span style="background:#f1c40f"></span> Moderate (51–100)<br />
      <span style="background:#e67e22"></span> Unhealthy (101–150)<br />
      <span style="background:#e74c3c"></span> Very Unhealthy (151–200)<br />
      <span style="background:#800000"></span> Hazardous (&gt;200)
    `;
    L.DomEvent.disableClickPropagation(div);
    return div;
  };
  legendControl.addTo(map);

  // Fallback sample data (lat, lng, aqi)
  const fallback = [
    { lat: 40.4168, lng: -3.7038, aqi: 80 }, // Madrid
    { lat: 41.3851, lng: 2.1734, aqi: 60 }, // Barcelona
    { lat: 37.3891, lng: -5.9845, aqi: 30 }, // Sevilla
    { lat: 39.4699, lng: -0.3763, aqi: 50 } // Valencia
  ];

  function aggregatePoints(raw, precision) {
    const buckets = new Map();
    for (const p of raw) {
      const latR = Number(p.lat.toFixed(precision));
      const lngR = Number(p.lng.toFixed(precision));
      const key = `${latR},${lngR}`;
      if (!buckets.has(key)) buckets.set(key, { latSum: 0, lngSum: 0, metricSum: 0, count: 0 });
      const b = buckets.get(key);
      const metric = Number(p.metric ?? 0);
      b.latSum += p.lat; b.lngSum += p.lng; b.metricSum += metric; b.count += 1;
    }
    const points = [];
    for (const [, b] of buckets) {
      const lat = b.latSum / b.count;
      const lng = b.lngSum / b.count;
      const avgMetric = b.metricSum / b.count;
      // use dataset-specific cap to compute intensity
      const intensity = Math.min(avgMetric / metricCap, 1);
      points.push([lat, lng, intensity]);
    }
    return points;
  }

  let heatLayer = null;
  function createHeatForZoom(rawData, zoom) {
    let precision;
    if (zoom <= 6) precision = 1;
    else if (zoom <= 9) precision = 2;
    else precision = 3;

    const points = aggregatePoints(rawData, precision);

    let radius, blur, minOpacity;
    if (zoom <= 5) {
      radius = 40; blur = 50; minOpacity = 0.4;
    } else {
      radius = 50; blur = 30; minOpacity = 0.5;
    }

    return L.heatLayer(points, {
      radius, blur, minOpacity,
      gradient: {
        0.0: '#2ecc71',
        0.3: '#f1c40f',
        0.55: '#e67e22',
        0.75: '#e74c3c',
        0.95: '#800000'
      }
    });
  }

  // Preload datasets so switching is instant. Store normalized arrays under datasets[file]
  const datasetFiles = ['our_index.json','air_quality.json','poverty.json','water_quality.json'];
  const datasets = {}; // filename -> normalized array

  async function fetchAndNormalize(file) {
    try {
      const res = await fetch('data/' + file);
      if (!res.ok) throw new Error('no data');
      const data = await res.json();
      return normalize(data, file);
    } catch (e) {
      console.warn('Failed to load', file, e);
      // return a normalized fallback using fallback raw and mapping for air_quality
      return normalize(fallback, 'air_quality.json');
    }
  }

  // mapping function: returns array of {lat,lng,metric}
  function normalize(data, file) {
    if (!Array.isArray(data)) return [];
    if (file === 'air_quality.json') return data.map(d => ({ lat: d.lat, lng: d.lng, metric: Number(d.aqi ?? 0) }));
    if (file === 'poverty.json') return data.map(d => ({ lat: d.lat, lng: d.lng, metric: Number((d.value ?? 0) * 100) })); // fraction -> percent
    if (file === 'water_quality.json') return data.map(d => ({ lat: d.lat, lng: d.lng, metric: Number(d.wqi ?? 0) }));
    // our_index.json assumed 0..1 -> scale to 0..100 for visualization
    return data.map(d => ({ lat: d.lat, lng: d.lng, metric: Number((d.index ?? 0) * 100) }));
  }

  // load all datasets once
  async function preloadAll() {
    const promises = datasetFiles.map(f => fetchAndNormalize(f).then(arr => { datasets[f] = arr; }));
    await Promise.all(promises);
  }

  // Current normalized data reference
  let currentNormalized = null;
  let zoomTimeout = null;
  let metricCap = 100;

  function renderNormalized(norm) {
    if (!norm || norm.length === 0) {
      console.warn('No data to render');
      return;
    }
    // Update legend title based on selected dataset
    const sel = document.getElementById('datasetSelect');
    const selVal = sel ? sel.value : 'our_index.json';
    const legendDiv = document.querySelector('.legend');
    if (legendDiv) {
      if (selVal === 'air_quality.json') legendDiv.querySelector('b').textContent = 'Air Quality Index (AQI)';
      else if (selVal === 'poverty.json') legendDiv.querySelector('b').textContent = 'Poverty (%)';
      else if (selVal === 'water_quality.json') legendDiv.querySelector('b').textContent = 'Water Quality Index';
      else legendDiv.querySelector('b').textContent = 'Our index';
    }

    console.log('Rendering dataset:', selVal, 'points:', norm.length);
  // compute min/max of metric for this dataset
  const metrics = norm.map(d => Number(d.metric || 0));
  const minMetric = Math.min(...metrics);
  const maxMetric = Math.max(...metrics);
  // dynamic scaling: map min->0 and max->cap (or 100) to full intensity range
  const cap = (selVal === 'air_quality.json') ? 200 : 100;
  metricCap = cap;
  const scaleMin = minMetric;
  const scaleMax = Math.max(maxMetric, 1);

  // apply dynamic normalization to create a metric field normalized to 0..cap
  const dyn = norm.map(d => ({ lat: d.lat, lng: d.lng, metric: ((Number(d.metric || 0) - scaleMin) / (scaleMax - scaleMin)) * cap }));
  currentNormalized = dyn;
  const newHeat = createHeatForZoom(currentNormalized, map.getZoom());
    if (heatLayer) {
      try { map.removeLayer(heatLayer); } catch (e) { /* ignore */ }
    }
    // ensure map has correct size before adding layer
    try { map.invalidateSize(); } catch (e) { /* ignore */ }
    heatLayer = newHeat.addTo(map);

    // Update legend with stats
    if (legendDiv) {
      const stats = document.createElement('div');
      stats.style.fontSize = '12px';
      stats.style.marginTop = '6px';
      stats.textContent = `min: ${minMetric.toFixed(1)} • max: ${maxMetric.toFixed(1)} • cap: ${metricCap}`;
      // remove old stats if present
      const old = legendDiv.querySelector('.legend-stats');
      if (old) old.remove();
      stats.className = 'legend-stats';
      legendDiv.appendChild(stats);
    }
  }

  // Single zoom handler uses currentNormalized
  function onZoomEnd() {
    if (zoomTimeout) clearTimeout(zoomTimeout);
    zoomTimeout = setTimeout(() => {
      if (!currentNormalized) return;
      const z = map.getZoom();
      const h = createHeatForZoom(currentNormalized, z);
      if (heatLayer) map.removeLayer(heatLayer);
      heatLayer = h.addTo(map);
    }, 200);
  }

  map.on('zoomend', onZoomEnd);

  // initial preload and render
  preloadAll().then(() => {
    // hide loader
    if (loader) loader.style.display = 'none';
    console.log('Datasets preloaded:', Object.keys(datasets));
    const sel = document.getElementById('datasetSelect');
    const start = sel ? sel.value : 'our_index.json';
    renderNormalized(datasets[start] || []);
  });

  // Re-load when dataset selection changes (instant because data is preloaded)
  const selector = document.getElementById('datasetSelect');
  if (selector) {
    selector.addEventListener('change', () => {
      // show loader briefly
      if (loader) loader.style.display = 'block';
      const v = selector.value;
      console.log('Dataset switched to', v);
      // if dataset already loaded use it, otherwise fetch and normalize
      if (datasets[v]) {
        // small timeout to allow loader to be visible
        setTimeout(() => {
          if (loader) loader.style.display = 'none';
          renderNormalized(datasets[v]);
        }, 120);
      } else {
        fetchAndNormalize(v).then(arr => {
          datasets[v] = arr;
          if (loader) loader.style.display = 'none';
          renderNormalized(arr);
        });
      }
    });
  }

  // Optional: poll current dataset for live updates every 15s
  let pollInterval = 5000; // ms (faster for testing)
  setInterval(() => {
    const sel = document.getElementById('datasetSelect');
    const v = sel ? sel.value : 'our_index.json';
    fetch('data/' + v).then(r => { if (r.ok) return r.json(); throw new Error('no'); }).then(data => {
      const arr = normalize(data, v);
      datasets[v] = arr;
      // if currently displayed dataset, re-render with fresh values
      if (currentNormalized && sel && sel.value === v) renderNormalized(arr);
    }).catch(() => { /* ignore polling errors */ });
  }, pollInterval);

  // Refresh button
  const refreshBtn = document.getElementById('refreshDataset');
  if (refreshBtn) {
    refreshBtn.addEventListener('click', () => {
      const sel = document.getElementById('datasetSelect');
      const v = sel ? sel.value : 'our_index.json';
      console.log('Manual refresh requested for', v);
      fetch('data/' + v).then(r => { if (r.ok) return r.json(); throw new Error('no'); }).then(data => {
        const arr = normalize(data, v);
        datasets[v] = arr;
        renderNormalized(arr);
      }).catch(err => { console.warn('Refresh failed', err); });
    });
  }
});





// (FAQ handling continued below)

// --- FAQ desplegable ---
const faqItems = document.querySelectorAll('.faq-item');
faqItems.forEach((item) => {
  const question = item.querySelector('.faq-question');
  if (!question) return;
  question.addEventListener('click', () => {
    faqItems.forEach((other) => { if (other !== item) other.classList.remove('active'); });
    item.classList.toggle('active');
  });
});

// Safe GSAP usage
if (typeof gsap !== 'undefined') {
  try {
    gsap.from('#video-section .video-overlay-text', {
      opacity: 0, y: 50, duration: 1.5,
      scrollTrigger: { trigger: '#video-section', start: 'top 80%', toggleActions: 'play none none reverse' }
    });
  } catch (e) { /* ignore */ }
}

// Report form handling
const reportForm = document.querySelector('.report-form');
if (reportForm) {
  reportForm.addEventListener('submit', (e) => {
    e.preventDefault();
    alert('¡Gracias! Tu reporte ha sido enviado correctamente.');
    reportForm.reset();
  });
}
