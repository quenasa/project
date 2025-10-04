document.addEventListener("DOMContentLoaded", () => {
  const baseMap = L.map("heatmapContainer").setView([40.4168, -3.7038], 6);

  // Capa base OSM
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "&copy; OpenStreetMap contributors"
  }).addTo(baseMap);

  // Datos simulados (valores = calidad del aire; 100 = contaminación alta)
  const testData = {
    max: 100,
    data: [
      { lat: 40.4168, lng: -3.7038, value: 80 }, // Madrid
      { lat: 41.3851, lng: 2.1734, value: 60 }, // Barcelona
      { lat: 37.3891, lng: -5.9845, value: 30 }, // Sevilla
      { lat: 39.4699, lng: -0.3763, value: 50 } // Valencia
    ]
  };

  // Configuración del heatmap
  const heatmapLayer = new HeatmapOverlay({
    radius: 35,
    maxOpacity: 0.6,
    scaleRadius: true,
    useLocalExtrema: false,
    latField: "lat",
    lngField: "lng",
    valueField: "value"
  });

  heatmapLayer.setData(testData);
  heatmapLayer.addTo(baseMap);

  // --- Leyenda personalizada ---
  const legend = L.control({ position: "bottomright" });

  legend.onAdd = function () {
    const div = L.DomUtil.create("div", "info legend");
    div.innerHTML = `
      <h4>Calidad del aire</h4>
      <i style="background:#ff0000"></i> Alta contaminación<br>
      <i style="background:#ff8800"></i> Moderada<br>
      <i style="background:#00ff00"></i> Buena<br>
    `;
    return div;
  };

  legend.addTo(baseMap);
});





// --- FAQ desplegable ---
const faqItems = document.querySelectorAll(".faq-item");

faqItems.forEach((item) => {
  const question = item.querySelector(".faq-question");
  question.addEventListener("click", () => {
    // Cerrar otros
    faqItems.forEach((other) => {
      if (other !== item) other.classList.remove("active");
    });
    // Alternar actual
    item.classList.toggle("active");
  });
});




gsap.from("#video-section .video-overlay-text", {
    opacity: 0,
    y: 50,
    duration: 1.5,
    scrollTrigger: {
      trigger: "#video-section",
      start: "top 80%",
      toggleActions: "play none none reverse"
    }
  });
  

  const reportForm = document.getElementById("reportForm");

reportForm.addEventListener("submit", (e) => {
  e.preventDefault();

  // Aquí podrías enviar los datos a un backend
  alert("¡Gracias! Tu reporte ha sido enviado correctamente.");

  // Reiniciar formulario
  reportForm.reset();
});
