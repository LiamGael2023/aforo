from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class AlertLevel(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class ChannelType(str, Enum):
    RIVER = "river"
    CANAL = "canal"
    STREAM = "stream"
    IRRIGATION = "irrigation"


# Esquemas de Estación
class StationBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    code: str = Field(..., min_length=1, max_length=20)
    description: Optional[str] = None
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    altitude: Optional[float] = 0
    water_body_name: str = Field(..., min_length=1, max_length=100)
    channel_type: Optional[ChannelType] = ChannelType.RIVER
    channel_width: Optional[float] = None
    channel_slope: Optional[float] = 0.001
    manning_coefficient: Optional[float] = 0.035
    curve_coefficient_a: Optional[float] = 1.0
    curve_coefficient_b: Optional[float] = 1.5
    curve_base_level: Optional[float] = 0.0
    level_low: Optional[float] = 0.3
    level_normal_min: Optional[float] = 0.5
    level_normal_max: Optional[float] = 2.0
    level_high: Optional[float] = 2.5
    level_critical: Optional[float] = 3.0


class StationCreate(StationBase):
    pass


class StationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    altitude: Optional[float] = None
    water_body_name: Optional[str] = None
    channel_type: Optional[ChannelType] = None
    channel_width: Optional[float] = None
    channel_slope: Optional[float] = None
    manning_coefficient: Optional[float] = None
    curve_coefficient_a: Optional[float] = None
    curve_coefficient_b: Optional[float] = None
    curve_base_level: Optional[float] = None
    level_low: Optional[float] = None
    level_normal_min: Optional[float] = None
    level_normal_max: Optional[float] = None
    level_high: Optional[float] = None
    level_critical: Optional[float] = None
    is_active: Optional[bool] = None


class StationResponse(StationBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StationWithLatest(StationResponse):
    latest_level: Optional[float] = None
    latest_flow: Optional[float] = None
    current_alert_level: Optional[str] = None
    last_measurement: Optional[datetime] = None


# Esquemas de Medición
class MeasurementBase(BaseModel):
    water_level: float = Field(..., ge=0)
    water_temperature: Optional[float] = None
    turbidity: Optional[float] = None
    measurement_method: Optional[str] = "automatic"
    notes: Optional[str] = None


class MeasurementCreate(MeasurementBase):
    station_id: int


class MeasurementResponse(MeasurementBase):
    id: int
    station_id: int
    timestamp: datetime
    flow_rate: Optional[float] = None
    velocity: Optional[float] = None
    cross_section_area: Optional[float] = None
    alert_level: str

    class Config:
        from_attributes = True


class MeasurementWithStation(MeasurementResponse):
    station_name: str
    station_code: str


# Esquemas de Alerta
class AlertBase(BaseModel):
    alert_level: AlertLevel
    message: str
    water_level: Optional[float] = None
    flow_rate: Optional[float] = None


class AlertCreate(AlertBase):
    station_id: int


class AlertResponse(AlertBase):
    id: int
    station_id: int
    is_active: bool
    is_acknowledged: bool
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    created_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AlertWithStation(AlertResponse):
    station_name: str
    station_code: str


class AlertAcknowledge(BaseModel):
    acknowledged_by: str


# Esquemas de Dashboard
class DashboardSummary(BaseModel):
    total_stations: int
    active_stations: int
    total_measurements_today: int
    active_alerts: int
    critical_alerts: int
    stations_by_alert_level: dict


class ChartData(BaseModel):
    timestamps: List[str]
    levels: List[float]
    flows: List[float]
    station_name: str
    station_code: str
