# Climate and Social Justice Map

NASA Space Apps Challenge 2025

## 🗺️ Project Overview

The Climate and Social Justice Map is a digital platform that integrates environmental, socioeconomic, and democratic data to identify, visualize, and prioritize vulnerable areas facing the climate crisis.

## 🎯 Objectives

- **Visualize inequalities**: Show how climate change and environmental degradation affect different populations unequally
- **Empower citizens**: Provide tools for communities to demand fairer policies
- **Support policy decisions**: Tool for designing public policies integrating social equity and environmental sustainability
- **Foster democratic participation**: Integrate channels for citizens to report environmental problems and participate in solutions

## 🚀 Backend API

The backend is built with Flask and provides RESTful API endpoints for data integration.

### Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python app.py
```

The API will be available at `http://localhost:5000`

### API Endpoints

- `GET /` - API information
- `GET /api/health` - Health check
- `GET /api/environmental` - Environmental data (air quality, temperature, vegetation)
- `GET /api/socioeconomic` - Socioeconomic data (income, poverty, services)
- `GET /api/democratic` - Democratic participation data
- `GET /api/vulnerability` - Vulnerability Index (IVSA)
- `POST /api/reports` - Submit citizen environmental reports
- `GET /api/reports` - Get citizen reports

### Documentation

- [Backend README](BACKEND_README.md) - Detailed backend documentation
- [API Integration Guide](API_INTEGRATION_GUIDE.md) - How to integrate external APIs

### Testing

Run the test script to verify all endpoints:

```bash
python test_api.py
```

## 📊 Data Integration

The platform combines multiple data layers:

### 🌍 Environmental Data
- Air quality (PM2.5, NO₂, ozone)
- Water pollution levels
- Temperature and heat waves
- Flood and drought risk
- Vegetation coverage / green spaces
- CO₂ emissions by area

### 🏘️ Socioeconomic Data
- Average income levels
- Poverty index
- Access to basic services (water, health, education)
- Local human development index

### 🗳️ Democratic Data
- Electoral participation
- Active citizen participation spaces
- Transparency and access to public data
- Presence of community or environmental organizations

## 🧭 Key Features

1. **Interactive Map with Dynamic Layers** - Combine different data layers to discover patterns
2. **Vulnerability Index (IVSA)** - Composite index classifying areas by vulnerability level
3. **Citizen Reporting Channel** - Allow citizens to report environmental issues
4. **Participation Section** - Propose and support local solutions

## 🛠️ Technologies

- **Backend**: Flask (Python)
- **Data Sources**: OpenAQ, NASA Earthdata, World Bank API, Copernicus
- **Database** (planned): PostgreSQL + PostGIS
- **Frontend** (planned): React, Leaflet/Mapbox, D3.js

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines before submitting pull requests.

## 📄 License

NASA Space Apps Challenge 2025 Project