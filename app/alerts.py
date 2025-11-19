"""
Sistema de alertas para el monitoreo de niveles de agua
"""
from datetime import datetime
from typing import Optional, Tuple
from sqlalchemy.orm import Session

from . import models, schemas


def determine_alert_level(
    water_level: float,
    level_low: float,
    level_normal_min: float,
    level_normal_max: float,
    level_high: float,
    level_critical: float
) -> str:
    """
    Determina el nivel de alerta basado en el nivel de agua.

    Args:
        water_level: Nivel de agua actual (m)
        level_low: Umbral de nivel bajo
        level_normal_min: Umbral mínimo normal
        level_normal_max: Umbral máximo normal
        level_high: Umbral de nivel alto
        level_critical: Umbral de nivel crítico

    Returns:
        Nivel de alerta como string
    """
    if water_level >= level_critical:
        return schemas.AlertLevel.CRITICAL.value
    elif water_level >= level_high:
        return schemas.AlertLevel.HIGH.value
    elif water_level < level_low:
        return schemas.AlertLevel.LOW.value
    elif level_normal_min <= water_level <= level_normal_max:
        return schemas.AlertLevel.NORMAL.value
    elif water_level < level_normal_min:
        return schemas.AlertLevel.LOW.value
    else:
        return schemas.AlertLevel.HIGH.value


def get_alert_message(alert_level: str, water_level: float, station_name: str) -> str:
    """
    Genera un mensaje descriptivo para la alerta.

    Args:
        alert_level: Nivel de alerta
        water_level: Nivel de agua actual
        station_name: Nombre de la estación

    Returns:
        Mensaje de alerta
    """
    messages = {
        schemas.AlertLevel.LOW.value: (
            f"Nivel bajo detectado en {station_name}. "
            f"Nivel actual: {water_level:.2f}m. "
            "Posible sequía o reducción de flujo."
        ),
        schemas.AlertLevel.NORMAL.value: (
            f"Nivel normal en {station_name}. "
            f"Nivel actual: {water_level:.2f}m."
        ),
        schemas.AlertLevel.HIGH.value: (
            f"Nivel alto en {station_name}. "
            f"Nivel actual: {water_level:.2f}m. "
            "Se recomienda monitoreo continuo."
        ),
        schemas.AlertLevel.CRITICAL.value: (
            f"ALERTA CRÍTICA en {station_name}. "
            f"Nivel actual: {water_level:.2f}m. "
            "Riesgo de desbordamiento. Acción inmediata requerida."
        )
    }
    return messages.get(alert_level, f"Alerta en {station_name}: {water_level:.2f}m")


def should_create_alert(
    current_level: str,
    previous_level: Optional[str],
    db: Session,
    station_id: int
) -> bool:
    """
    Determina si se debe crear una nueva alerta.

    Se crea alerta si:
    - El nivel cambió a uno más crítico
    - Es nivel CRÍTICO o HIGH y no hay alerta activa

    Args:
        current_level: Nivel de alerta actual
        previous_level: Nivel de alerta anterior
        db: Sesión de base de datos
        station_id: ID de la estación

    Returns:
        True si se debe crear alerta
    """
    # Prioridad de niveles (mayor número = más crítico)
    priority = {
        schemas.AlertLevel.NORMAL.value: 0,
        schemas.AlertLevel.LOW.value: 1,
        schemas.AlertLevel.HIGH.value: 2,
        schemas.AlertLevel.CRITICAL.value: 3
    }

    # Solo alertar para niveles no normales
    if current_level == schemas.AlertLevel.NORMAL.value:
        return False

    # Verificar si ya hay una alerta activa del mismo nivel
    existing_alert = db.query(models.Alert).filter(
        models.Alert.station_id == station_id,
        models.Alert.alert_level == current_level,
        models.Alert.is_active == True
    ).first()

    if existing_alert:
        return False

    # Crear alerta si el nivel es crítico o alto
    if current_level in [schemas.AlertLevel.CRITICAL.value, schemas.AlertLevel.HIGH.value]:
        return True

    # Crear alerta si el nivel cambió a uno más crítico
    if previous_level:
        if priority.get(current_level, 0) > priority.get(previous_level, 0):
            return True
    else:
        # Primera medición con nivel no normal
        return True

    return False


def create_alert_for_measurement(
    db: Session,
    station: models.Station,
    water_level: float,
    flow_rate: Optional[float],
    alert_level: str
) -> Optional[models.Alert]:
    """
    Crea una alerta basada en una medición.

    Args:
        db: Sesión de base de datos
        station: Estación de aforo
        water_level: Nivel de agua
        flow_rate: Caudal calculado
        alert_level: Nivel de alerta determinado

    Returns:
        Alerta creada o None
    """
    # Obtener última medición para comparar
    last_measurement = db.query(models.Measurement).filter(
        models.Measurement.station_id == station.id
    ).order_by(models.Measurement.timestamp.desc()).first()

    previous_level = last_measurement.alert_level if last_measurement else None

    if not should_create_alert(alert_level, previous_level, db, station.id):
        return None

    # Generar mensaje
    message = get_alert_message(alert_level, water_level, station.name)

    # Crear alerta
    alert = models.Alert(
        station_id=station.id,
        alert_level=alert_level,
        message=message,
        water_level=water_level,
        flow_rate=flow_rate,
        is_active=True
    )

    db.add(alert)
    db.commit()
    db.refresh(alert)

    return alert


def resolve_alerts_for_station(db: Session, station_id: int, current_level: str):
    """
    Resuelve alertas activas si el nivel volvió a normal.

    Args:
        db: Sesión de base de datos
        station_id: ID de la estación
        current_level: Nivel de alerta actual
    """
    if current_level != schemas.AlertLevel.NORMAL.value:
        return

    # Resolver todas las alertas activas de la estación
    active_alerts = db.query(models.Alert).filter(
        models.Alert.station_id == station_id,
        models.Alert.is_active == True
    ).all()

    for alert in active_alerts:
        alert.is_active = False
        alert.resolved_at = datetime.utcnow()

    db.commit()


def acknowledge_alert(
    db: Session,
    alert_id: int,
    acknowledged_by: str
) -> Optional[models.Alert]:
    """
    Reconoce una alerta.

    Args:
        db: Sesión de base de datos
        alert_id: ID de la alerta
        acknowledged_by: Usuario que reconoce

    Returns:
        Alerta actualizada o None
    """
    alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()

    if not alert:
        return None

    alert.is_acknowledged = True
    alert.acknowledged_by = acknowledged_by
    alert.acknowledged_at = datetime.utcnow()

    db.commit()
    db.refresh(alert)

    return alert


def get_alert_statistics(db: Session) -> dict:
    """
    Obtiene estadísticas de alertas.

    Args:
        db: Sesión de base de datos

    Returns:
        Diccionario con estadísticas
    """
    total_active = db.query(models.Alert).filter(
        models.Alert.is_active == True
    ).count()

    critical_count = db.query(models.Alert).filter(
        models.Alert.is_active == True,
        models.Alert.alert_level == schemas.AlertLevel.CRITICAL.value
    ).count()

    high_count = db.query(models.Alert).filter(
        models.Alert.is_active == True,
        models.Alert.alert_level == schemas.AlertLevel.HIGH.value
    ).count()

    low_count = db.query(models.Alert).filter(
        models.Alert.is_active == True,
        models.Alert.alert_level == schemas.AlertLevel.LOW.value
    ).count()

    unacknowledged = db.query(models.Alert).filter(
        models.Alert.is_active == True,
        models.Alert.is_acknowledged == False
    ).count()

    return {
        "total_active": total_active,
        "critical": critical_count,
        "high": high_count,
        "low": low_count,
        "unacknowledged": unacknowledged
    }
