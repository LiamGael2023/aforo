"""
Operaciones CRUD para el sistema de aforo
"""
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from . import models, schemas
from .calculations import calculate_hydraulic_parameters
from .alerts import (
    determine_alert_level,
    create_alert_for_measurement,
    resolve_alerts_for_station
)


# CRUD para Estaciones
def get_stations(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False
) -> List[models.Station]:
    """Obtiene lista de estaciones"""
    query = db.query(models.Station)
    if active_only:
        query = query.filter(models.Station.is_active == True)
    return query.offset(skip).limit(limit).all()


def get_station(db: Session, station_id: int) -> Optional[models.Station]:
    """Obtiene una estación por ID"""
    return db.query(models.Station).filter(models.Station.id == station_id).first()


def get_station_by_code(db: Session, code: str) -> Optional[models.Station]:
    """Obtiene una estación por código"""
    return db.query(models.Station).filter(models.Station.code == code).first()


def create_station(db: Session, station: schemas.StationCreate) -> models.Station:
    """Crea una nueva estación"""
    db_station = models.Station(**station.model_dump())
    db.add(db_station)
    db.commit()
    db.refresh(db_station)
    return db_station


def update_station(
    db: Session,
    station_id: int,
    station_update: schemas.StationUpdate
) -> Optional[models.Station]:
    """Actualiza una estación existente"""
    db_station = get_station(db, station_id)
    if not db_station:
        return None

    update_data = station_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_station, field, value)

    db_station.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_station)
    return db_station


def delete_station(db: Session, station_id: int) -> bool:
    """Elimina una estación"""
    db_station = get_station(db, station_id)
    if not db_station:
        return False

    db.delete(db_station)
    db.commit()
    return True


def get_stations_with_latest(db: Session) -> List[dict]:
    """Obtiene estaciones con sus últimas mediciones"""
    stations = get_stations(db, active_only=True)
    result = []

    for station in stations:
        # Obtener última medición
        last_measurement = db.query(models.Measurement).filter(
            models.Measurement.station_id == station.id
        ).order_by(desc(models.Measurement.timestamp)).first()

        station_data = {
            "id": station.id,
            "name": station.name,
            "code": station.code,
            "description": station.description,
            "latitude": station.latitude,
            "longitude": station.longitude,
            "altitude": station.altitude,
            "water_body_name": station.water_body_name,
            "channel_type": station.channel_type,
            "is_active": station.is_active,
            "created_at": station.created_at,
            "updated_at": station.updated_at,
            "latest_level": None,
            "latest_flow": None,
            "current_alert_level": "normal",
            "last_measurement": None
        }

        if last_measurement:
            station_data["latest_level"] = last_measurement.water_level
            station_data["latest_flow"] = last_measurement.flow_rate
            station_data["current_alert_level"] = last_measurement.alert_level
            station_data["last_measurement"] = last_measurement.timestamp

        result.append(station_data)

    return result


# CRUD para Mediciones
def create_measurement(
    db: Session,
    measurement: schemas.MeasurementCreate
) -> Optional[models.Measurement]:
    """Crea una nueva medición con cálculos automáticos"""
    # Obtener estación
    station = get_station(db, measurement.station_id)
    if not station:
        return None

    # Calcular parámetros hidráulicos
    flow_rate, velocity, area = calculate_hydraulic_parameters(
        water_level=measurement.water_level,
        channel_width=station.channel_width,
        slope=station.channel_slope,
        manning_n=station.manning_coefficient,
        coef_a=station.curve_coefficient_a,
        coef_b=station.curve_coefficient_b,
        base_level=station.curve_base_level
    )

    # Determinar nivel de alerta
    alert_level = determine_alert_level(
        water_level=measurement.water_level,
        level_low=station.level_low,
        level_normal_min=station.level_normal_min,
        level_normal_max=station.level_normal_max,
        level_high=station.level_high,
        level_critical=station.level_critical
    )

    # Crear medición
    db_measurement = models.Measurement(
        station_id=measurement.station_id,
        water_level=measurement.water_level,
        flow_rate=flow_rate,
        velocity=velocity,
        cross_section_area=area,
        water_temperature=measurement.water_temperature,
        turbidity=measurement.turbidity,
        measurement_method=measurement.measurement_method,
        notes=measurement.notes,
        alert_level=alert_level
    )

    db.add(db_measurement)
    db.commit()
    db.refresh(db_measurement)

    # Crear alerta si es necesario
    create_alert_for_measurement(db, station, measurement.water_level, flow_rate, alert_level)

    # Resolver alertas si el nivel volvió a normal
    resolve_alerts_for_station(db, station.id, alert_level)

    return db_measurement


def get_measurements(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    station_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> List[models.Measurement]:
    """Obtiene mediciones con filtros opcionales"""
    query = db.query(models.Measurement)

    if station_id:
        query = query.filter(models.Measurement.station_id == station_id)

    if start_date:
        query = query.filter(models.Measurement.timestamp >= start_date)

    if end_date:
        query = query.filter(models.Measurement.timestamp <= end_date)

    return query.order_by(desc(models.Measurement.timestamp)).offset(skip).limit(limit).all()


def get_measurement(db: Session, measurement_id: int) -> Optional[models.Measurement]:
    """Obtiene una medición por ID"""
    return db.query(models.Measurement).filter(
        models.Measurement.id == measurement_id
    ).first()


def get_latest_measurements(db: Session, limit: int = 10) -> List[dict]:
    """Obtiene las últimas mediciones con información de estación"""
    measurements = db.query(models.Measurement).order_by(
        desc(models.Measurement.timestamp)
    ).limit(limit).all()

    result = []
    for m in measurements:
        station = get_station(db, m.station_id)
        result.append({
            "id": m.id,
            "station_id": m.station_id,
            "station_name": station.name if station else "Desconocida",
            "station_code": station.code if station else "N/A",
            "timestamp": m.timestamp,
            "water_level": m.water_level,
            "flow_rate": m.flow_rate,
            "velocity": m.velocity,
            "alert_level": m.alert_level
        })

    return result


def get_station_chart_data(
    db: Session,
    station_id: int,
    hours: int = 24
) -> Optional[schemas.ChartData]:
    """Obtiene datos para gráficos de una estación"""
    station = get_station(db, station_id)
    if not station:
        return None

    start_time = datetime.utcnow() - timedelta(hours=hours)

    measurements = db.query(models.Measurement).filter(
        models.Measurement.station_id == station_id,
        models.Measurement.timestamp >= start_time
    ).order_by(models.Measurement.timestamp).all()

    timestamps = [m.timestamp.strftime("%Y-%m-%d %H:%M") for m in measurements]
    levels = [m.water_level for m in measurements]
    flows = [m.flow_rate or 0 for m in measurements]

    return schemas.ChartData(
        timestamps=timestamps,
        levels=levels,
        flows=flows,
        station_name=station.name,
        station_code=station.code
    )


# CRUD para Alertas
def get_alerts(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    station_id: Optional[int] = None
) -> List[models.Alert]:
    """Obtiene alertas con filtros"""
    query = db.query(models.Alert)

    if active_only:
        query = query.filter(models.Alert.is_active == True)

    if station_id:
        query = query.filter(models.Alert.station_id == station_id)

    return query.order_by(desc(models.Alert.created_at)).offset(skip).limit(limit).all()


def get_alerts_with_station(db: Session, active_only: bool = True) -> List[dict]:
    """Obtiene alertas con información de estación"""
    alerts = get_alerts(db, active_only=active_only)
    result = []

    for alert in alerts:
        station = get_station(db, alert.station_id)
        result.append({
            "id": alert.id,
            "station_id": alert.station_id,
            "station_name": station.name if station else "Desconocida",
            "station_code": station.code if station else "N/A",
            "alert_level": alert.alert_level,
            "message": alert.message,
            "water_level": alert.water_level,
            "flow_rate": alert.flow_rate,
            "is_active": alert.is_active,
            "is_acknowledged": alert.is_acknowledged,
            "acknowledged_by": alert.acknowledged_by,
            "acknowledged_at": alert.acknowledged_at,
            "created_at": alert.created_at,
            "resolved_at": alert.resolved_at
        })

    return result


def get_alert(db: Session, alert_id: int) -> Optional[models.Alert]:
    """Obtiene una alerta por ID"""
    return db.query(models.Alert).filter(models.Alert.id == alert_id).first()


# Dashboard
def get_dashboard_summary(db: Session) -> schemas.DashboardSummary:
    """Obtiene resumen para el dashboard"""
    total_stations = db.query(models.Station).count()
    active_stations = db.query(models.Station).filter(
        models.Station.is_active == True
    ).count()

    # Mediciones de hoy
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_measurements = db.query(models.Measurement).filter(
        models.Measurement.timestamp >= today_start
    ).count()

    # Alertas activas
    active_alerts = db.query(models.Alert).filter(
        models.Alert.is_active == True
    ).count()

    critical_alerts = db.query(models.Alert).filter(
        models.Alert.is_active == True,
        models.Alert.alert_level == schemas.AlertLevel.CRITICAL.value
    ).count()

    # Estaciones por nivel de alerta
    stations_with_latest = get_stations_with_latest(db)
    by_level = {"normal": 0, "low": 0, "high": 0, "critical": 0}
    for station in stations_with_latest:
        level = station.get("current_alert_level", "normal")
        if level in by_level:
            by_level[level] += 1

    return schemas.DashboardSummary(
        total_stations=total_stations,
        active_stations=active_stations,
        total_measurements_today=today_measurements,
        active_alerts=active_alerts,
        critical_alerts=critical_alerts,
        stations_by_alert_level=by_level
    )
