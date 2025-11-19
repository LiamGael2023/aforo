"""
Sistema de Aforo Digital de Ríos y Canales
Aplicación principal FastAPI
"""
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.requests import Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from .database import engine, get_db, Base
from . import crud, schemas, models
from .alerts import acknowledge_alert, get_alert_statistics

# Crear tablas
Base.metadata.create_all(bind=engine)

# Crear aplicación
app = FastAPI(
    title="Sistema de Aforo Digital",
    description="Sistema para monitoreo de caudales en ríos y canales",
    version="1.0.0"
)

# Montar archivos estáticos y templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# Ruta principal - Dashboard
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Página principal del dashboard"""
    return templates.TemplateResponse("index.html", {"request": request})


# ============== API de Estaciones ==============

@app.get("/api/stations", response_model=List[schemas.StationResponse])
def list_stations(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
    db: Session = Depends(get_db)
):
    """Lista todas las estaciones de aforo"""
    return crud.get_stations(db, skip=skip, limit=limit, active_only=active_only)


@app.get("/api/stations/with-latest")
def list_stations_with_latest(db: Session = Depends(get_db)):
    """Lista estaciones con sus últimas mediciones"""
    return crud.get_stations_with_latest(db)


@app.post("/api/stations", response_model=schemas.StationResponse, status_code=201)
def create_station(station: schemas.StationCreate, db: Session = Depends(get_db)):
    """Crea una nueva estación de aforo"""
    # Verificar código único
    existing = crud.get_station_by_code(db, station.code)
    if existing:
        raise HTTPException(status_code=400, detail="El código de estación ya existe")

    return crud.create_station(db, station)


@app.get("/api/stations/{station_id}", response_model=schemas.StationResponse)
def get_station(station_id: int, db: Session = Depends(get_db)):
    """Obtiene una estación por ID"""
    station = crud.get_station(db, station_id)
    if not station:
        raise HTTPException(status_code=404, detail="Estación no encontrada")
    return station


@app.put("/api/stations/{station_id}", response_model=schemas.StationResponse)
def update_station(
    station_id: int,
    station_update: schemas.StationUpdate,
    db: Session = Depends(get_db)
):
    """Actualiza una estación existente"""
    station = crud.update_station(db, station_id, station_update)
    if not station:
        raise HTTPException(status_code=404, detail="Estación no encontrada")
    return station


@app.delete("/api/stations/{station_id}")
def delete_station(station_id: int, db: Session = Depends(get_db)):
    """Elimina una estación"""
    if not crud.delete_station(db, station_id):
        raise HTTPException(status_code=404, detail="Estación no encontrada")
    return {"message": "Estación eliminada correctamente"}


# ============== API de Mediciones ==============

@app.get("/api/measurements", response_model=List[schemas.MeasurementResponse])
def list_measurements(
    skip: int = 0,
    limit: int = 100,
    station_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Lista mediciones con filtros opcionales"""
    return crud.get_measurements(
        db, skip=skip, limit=limit,
        station_id=station_id,
        start_date=start_date,
        end_date=end_date
    )


@app.post("/api/measurements", response_model=schemas.MeasurementResponse, status_code=201)
def create_measurement(
    measurement: schemas.MeasurementCreate,
    db: Session = Depends(get_db)
):
    """Registra una nueva medición de aforo"""
    result = crud.create_measurement(db, measurement)
    if not result:
        raise HTTPException(status_code=404, detail="Estación no encontrada")
    return result


@app.get("/api/measurements/latest")
def get_latest_measurements(
    limit: int = Query(default=10, le=100),
    db: Session = Depends(get_db)
):
    """Obtiene las últimas mediciones registradas"""
    return crud.get_latest_measurements(db, limit=limit)


@app.get("/api/measurements/station/{station_id}")
def get_station_measurements(
    station_id: int,
    limit: int = Query(default=100, le=1000),
    db: Session = Depends(get_db)
):
    """Obtiene mediciones de una estación específica"""
    station = crud.get_station(db, station_id)
    if not station:
        raise HTTPException(status_code=404, detail="Estación no encontrada")

    return crud.get_measurements(db, station_id=station_id, limit=limit)


@app.get("/api/measurements/{measurement_id}", response_model=schemas.MeasurementResponse)
def get_measurement(measurement_id: int, db: Session = Depends(get_db)):
    """Obtiene una medición por ID"""
    measurement = crud.get_measurement(db, measurement_id)
    if not measurement:
        raise HTTPException(status_code=404, detail="Medición no encontrada")
    return measurement


# ============== API de Alertas ==============

@app.get("/api/alerts")
def list_alerts(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    station_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Lista alertas activas del sistema"""
    return crud.get_alerts_with_station(db, active_only=active_only)


@app.get("/api/alerts/statistics")
def get_alerts_statistics(db: Session = Depends(get_db)):
    """Obtiene estadísticas de alertas"""
    return get_alert_statistics(db)


@app.get("/api/alerts/history")
def get_alerts_history(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtiene historial completo de alertas"""
    return crud.get_alerts_with_station(db, active_only=False)


@app.put("/api/alerts/{alert_id}/acknowledge")
def acknowledge_alert_endpoint(
    alert_id: int,
    ack_data: schemas.AlertAcknowledge,
    db: Session = Depends(get_db)
):
    """Reconoce una alerta"""
    alert = acknowledge_alert(db, alert_id, ack_data.acknowledged_by)
    if not alert:
        raise HTTPException(status_code=404, detail="Alerta no encontrada")
    return {"message": "Alerta reconocida", "alert_id": alert_id}


@app.get("/api/alerts/{alert_id}")
def get_alert(alert_id: int, db: Session = Depends(get_db)):
    """Obtiene una alerta por ID"""
    alert = crud.get_alert(db, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alerta no encontrada")
    return alert


# ============== API de Dashboard ==============

@app.get("/api/dashboard/summary", response_model=schemas.DashboardSummary)
def get_dashboard_summary(db: Session = Depends(get_db)):
    """Obtiene resumen del sistema para el dashboard"""
    return crud.get_dashboard_summary(db)


@app.get("/api/dashboard/charts/{station_id}")
def get_chart_data(
    station_id: int,
    hours: int = Query(default=24, le=168),
    db: Session = Depends(get_db)
):
    """Obtiene datos para gráficos de una estación"""
    data = crud.get_station_chart_data(db, station_id, hours)
    if not data:
        raise HTTPException(status_code=404, detail="Estación no encontrada")
    return data


# ============== Endpoint para datos de ejemplo ==============

@app.post("/api/seed-data")
def seed_sample_data(db: Session = Depends(get_db)):
    """Crea datos de ejemplo para demostración"""
    from datetime import timedelta
    import random

    # Verificar si ya hay datos
    if crud.get_stations(db):
        return {"message": "Ya existen datos en el sistema"}

    # Crear estaciones de ejemplo
    stations_data = [
        {
            "name": "Estación Río Grande",
            "code": "RG-001",
            "description": "Estación principal del Río Grande, zona urbana",
            "latitude": -34.6037,
            "longitude": -58.3816,
            "altitude": 25,
            "water_body_name": "Río Grande",
            "channel_type": "river",
            "channel_width": 15.0,
            "channel_slope": 0.0015,
            "manning_coefficient": 0.035,
            "level_low": 0.5,
            "level_normal_min": 0.8,
            "level_normal_max": 2.5,
            "level_high": 3.0,
            "level_critical": 4.0
        },
        {
            "name": "Canal de Riego Norte",
            "code": "CN-001",
            "description": "Canal principal de riego zona norte",
            "latitude": -34.5875,
            "longitude": -58.4170,
            "altitude": 30,
            "water_body_name": "Canal Norte",
            "channel_type": "irrigation",
            "channel_width": 5.0,
            "channel_slope": 0.002,
            "manning_coefficient": 0.025,
            "level_low": 0.2,
            "level_normal_min": 0.4,
            "level_normal_max": 1.2,
            "level_high": 1.5,
            "level_critical": 2.0
        },
        {
            "name": "Arroyo Las Piedras",
            "code": "AP-001",
            "description": "Arroyo secundario, zona periurbana",
            "latitude": -34.6200,
            "longitude": -58.3500,
            "altitude": 20,
            "water_body_name": "Arroyo Las Piedras",
            "channel_type": "stream",
            "channel_width": 8.0,
            "channel_slope": 0.003,
            "manning_coefficient": 0.040,
            "level_low": 0.3,
            "level_normal_min": 0.5,
            "level_normal_max": 1.8,
            "level_high": 2.2,
            "level_critical": 3.0
        }
    ]

    created_stations = []
    for station_data in stations_data:
        station = crud.create_station(db, schemas.StationCreate(**station_data))
        created_stations.append(station)

    # Crear mediciones de ejemplo (últimas 24 horas)
    now = datetime.utcnow()
    measurements_created = 0

    for station in created_stations:
        # Nivel base para esta estación
        base_level = (station.level_normal_min + station.level_normal_max) / 2

        for i in range(48):  # Una medición cada 30 minutos
            timestamp = now - timedelta(minutes=30 * (47 - i))

            # Variación del nivel (simulando cambios naturales)
            variation = random.uniform(-0.3, 0.3)
            water_level = base_level + variation

            # Asegurar valores positivos
            water_level = max(0.1, water_level)

            measurement = schemas.MeasurementCreate(
                station_id=station.id,
                water_level=round(water_level, 2),
                water_temperature=round(random.uniform(15, 25), 1),
                turbidity=round(random.uniform(5, 50), 1),
                measurement_method="automatic"
            )

            db_measurement = crud.create_measurement(db, measurement)
            if db_measurement:
                # Actualizar timestamp manualmente
                db_measurement.timestamp = timestamp
                db.commit()
                measurements_created += 1

    return {
        "message": "Datos de ejemplo creados correctamente",
        "stations_created": len(created_stations),
        "measurements_created": measurements_created
    }


# Información del sistema
@app.get("/api/info")
def get_system_info():
    """Información del sistema"""
    return {
        "name": "Sistema de Aforo Digital de Ríos y Canales",
        "version": "1.0.0",
        "description": "Sistema integral para monitoreo de caudales en cuerpos de agua"
    }
