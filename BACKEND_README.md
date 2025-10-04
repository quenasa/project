# Climate and Social Justice Map - Backend API

Backend API for the Climate and Social Justice Map project (NASA Space Apps Challenge 2025).

## 🚀 Overview

This Flask-based REST API provides endpoints for integrating and serving environmental, socioeconomic, and democratic data to visualize climate and social justice vulnerabilities.

## 📋 Features

- **Environmental Data API**: Air quality, temperature, vegetation coverage, CO2 emissions
- **Socioeconomic Data API**: Income levels, poverty index, basic services access
- **Democratic Data API**: Electoral participation, citizen spaces, transparency
- **Vulnerability Index (IVSA)**: Composite index combining all data sources
- **Citizen Reports**: Allow citizens to report environmental issues
- **CORS Enabled**: Ready for frontend integration

## 🛠️ Installation

1. **Clone the repository**:
```bash
git clone https://github.com/quenasa/project.git
cd project
```

2. **Create a virtual environment** (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

## 🏃 Running the Application

### Development Mode

```bash
python app.py
```

The API will be available at `http://localhost:5000`

### Production Mode

```bash
export FLASK_DEBUG=False
export PORT=8080
python app.py
```

Or use a production server like Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8080 app:app
```

## 📡 API Endpoints

### Root Endpoint
```
GET /
```
Returns API information and available endpoints.

### Health Check
```
GET /api/health
```
Returns server health status.

### Environmental Data
```
GET /api/environmental?location=<location_name>
```
Returns environmental data (air quality, temperature, vegetation, etc.)

**Response Example**:
```json
{
  "data": [
    {
      "id": 1,
      "location": {"lat": 40.4168, "lon": -3.7038, "name": "Madrid Sur"},
      "air_quality": {"pm25": 45.2, "no2": 38.5, "ozone": 62.1},
      "temperature": 28.5,
      "vegetation_coverage": 15.3,
      "flood_risk": "medium",
      "co2_emissions": 8.2
    }
  ],
  "count": 1
}
```

### Socioeconomic Data
```
GET /api/socioeconomic?location=<location_name>
```
Returns socioeconomic data (income, poverty, services access, etc.)

**Response Example**:
```json
{
  "data": [
    {
      "id": 1,
      "location": {"lat": 40.4168, "lon": -3.7038, "name": "Madrid Sur"},
      "average_income": 18500,
      "poverty_index": 28.5,
      "basic_services_access": {"water": 95, "health": 82, "education": 88},
      "human_development_index": 0.72
    }
  ],
  "count": 1
}
```

### Democratic Data
```
GET /api/democratic?location=<location_name>
```
Returns democratic participation data.

**Response Example**:
```json
{
  "data": [
    {
      "id": 1,
      "location": {"lat": 40.4168, "lon": -3.7038, "name": "Madrid Sur"},
      "electoral_participation": 58.2,
      "citizen_participation_spaces": 3,
      "transparency_index": 65,
      "active_organizations": 12
    }
  ],
  "count": 1
}
```

### Vulnerability Index (IVSA)
```
GET /api/vulnerability
```
Calculates and returns the Socio-environmental Vulnerability Index for all areas.

**Response Example**:
```json
{
  "data": [
    {
      "location": {"lat": 40.4168, "lon": -3.7038, "name": "Madrid Sur"},
      "vulnerability_score": 48.73,
      "vulnerability_level": "medium",
      "color": "#FFA500",
      "factors": {
        "environmental": 43.1,
        "socioeconomic": 28.5,
        "democratic": 41.8
      }
    }
  ],
  "count": 1
}
```

**Vulnerability Levels**:
- 🟥 **High** (score ≥ 60): Red color `#FF4444`
- 🟧 **Medium** (35 ≤ score < 60): Orange color `#FFA500`
- 🟩 **Low** (score < 35): Green color `#44FF44`

### Citizen Reports

#### Get All Reports
```
GET /api/reports?type=<report_type>
```
Returns all citizen environmental reports (optionally filtered by type).

#### Submit a Report
```
POST /api/reports
Content-Type: application/json

{
  "type": "illegal_dump",
  "location": {"lat": 40.4168, "lon": -3.7038, "name": "Madrid Sur"},
  "description": "Illegal waste dump near residential area",
  "reporter": "citizen123"
}
```

**Report Types**:
- `illegal_dump`: Illegal waste disposal
- `deforestation`: Tree cutting or forest loss
- `fire`: Fires or burn areas
- `water_issue`: Water supply problems
- `lack_green_space`: Insufficient parks or green areas

#### Get/Update Specific Report
```
GET /api/reports/<report_id>
PUT /api/reports/<report_id>
```

## 🗄️ Data Integration

Currently, the API uses mock data for demonstration. In production, you should:

1. **Connect to external APIs**:
   - OpenAQ for air quality data
   - NASA Earthdata for satellite data
   - World Bank API for socioeconomic indicators
   - Government open data portals

2. **Add database support**:
   - PostgreSQL + PostGIS for spatial data
   - Store citizen reports
   - Cache API responses

3. **Environment variables** (create a `.env` file):
```env
FLASK_DEBUG=False
PORT=5000
DATABASE_URL=postgresql://user:pass@localhost/climatedb
OPENAQ_API_KEY=your_key_here
NASA_API_KEY=your_key_here
```

## 🧪 Testing

Run the API and test endpoints:

```bash
# Test root endpoint
curl http://localhost:5000/

# Test environmental data
curl http://localhost:5000/api/environmental

# Test vulnerability index
curl http://localhost:5000/api/vulnerability

# Submit a citizen report
curl -X POST http://localhost:5000/api/reports \
  -H "Content-Type: application/json" \
  -d '{
    "type": "illegal_dump",
    "location": {"lat": 40.4, "lon": -3.7, "name": "Test Area"},
    "description": "Test report"
  }'
```

## 📦 Dependencies

- **Flask**: Web framework
- **Flask-CORS**: Cross-origin resource sharing support
- **requests**: HTTP library for external API calls
- **python-dotenv**: Environment variable management

## 🌍 Deployment

### Local Development
```bash
python app.py
```

### Production (Gunicorn)
```bash
gunicorn -w 4 -b 0.0.0.0:8080 app:app
```

### Docker (Optional)
Create a `Dockerfile`:
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app.py .
EXPOSE 5000
CMD ["python", "app.py"]
```

Build and run:
```bash
docker build -t climate-justice-api .
docker run -p 5000:5000 climate-justice-api
```

## 🚀 Future Enhancements

- [ ] Integration with real external APIs
- [ ] Database implementation (PostgreSQL + PostGIS)
- [ ] Authentication and authorization
- [ ] Rate limiting
- [ ] Caching layer (Redis)
- [ ] Machine Learning models for predictive analysis
- [ ] WebSocket support for real-time updates
- [ ] API documentation with Swagger/OpenAPI
- [ ] Monitoring and logging
- [ ] Automated testing suite

## 📄 License

This project is part of NASA Space Apps Challenge 2025.

## 👥 Contributors

Team: Quenasa Project

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
