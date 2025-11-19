from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from .database import Base


class AlertLevel(str, enum.Enum):
    """Niveles de alerta para estaciones"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class ChannelType(str, enum.Enum):
    """Tipos de canal/cuerpo de agua"""
    RIVER = "river"
    CANAL = "canal"
    STREAM = "stream"
    IRRIGATION = "irrigation"


class Station(Base):
    """Modelo para estaciones de aforo"""
    __tablename__ = "stations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(20), unique=True, index=True, nullable=False)
    description = Column(String(500))

    # Ubicación
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    altitude = Column(Float, default=0)

    # Información del cuerpo de agua
    water_body_name = Column(String(100), nullable=False)
    channel_type = Column(String(20), default=ChannelType.RIVER.value)

    # Parámetros hidráulicos
    channel_width = Column(Float)  # Ancho del canal (m)
    channel_slope = Column(Float, default=0.001)  # Pendiente
    manning_coefficient = Column(Float, default=0.035)  # Coeficiente de Manning

    # Parámetros de curva de aforo Q = a * (h - h0)^b
    curve_coefficient_a = Column(Float, default=1.0)
    curve_coefficient_b = Column(Float, default=1.5)
    curve_base_level = Column(Float, default=0.0)  # h0

    # Niveles de alerta (m)
    level_low = Column(Float, default=0.3)
    level_normal_min = Column(Float, default=0.5)
    level_normal_max = Column(Float, default=2.0)
    level_high = Column(Float, default=2.5)
    level_critical = Column(Float, default=3.0)

    # Estado
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    measurements = relationship("Measurement", back_populates="station", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="station", cascade="all, delete-orphan")


class Measurement(Base):
    """Modelo para mediciones de aforo"""
    __tablename__ = "measurements"

    id = Column(Integer, primary_key=True, index=True)
    station_id = Column(Integer, ForeignKey("stations.id"), nullable=False)

    # Datos de medición
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    water_level = Column(Float, nullable=False)  # Nivel de agua (m)

    # Datos calculados
    flow_rate = Column(Float)  # Caudal (m³/s)
    velocity = Column(Float)  # Velocidad (m/s)
    cross_section_area = Column(Float)  # Área sección transversal (m²)

    # Datos adicionales
    water_temperature = Column(Float)  # Temperatura del agua (°C)
    turbidity = Column(Float)  # Turbidez (NTU)

    # Metadatos
    measurement_method = Column(String(50), default="automatic")
    notes = Column(String(500))

    # Estado de alerta al momento de la medición
    alert_level = Column(String(20), default=AlertLevel.NORMAL.value)

    # Relación
    station = relationship("Station", back_populates="measurements")


class Alert(Base):
    """Modelo para alertas del sistema"""
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    station_id = Column(Integer, ForeignKey("stations.id"), nullable=False)

    # Información de la alerta
    alert_level = Column(String(20), nullable=False)
    message = Column(String(500), nullable=False)
    water_level = Column(Float)
    flow_rate = Column(Float)

    # Estado
    is_active = Column(Boolean, default=True)
    is_acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(String(100))
    acknowledged_at = Column(DateTime)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime)

    # Relación
    station = relationship("Station", back_populates="alerts")
