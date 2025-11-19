"""
Módulo de cálculos hidráulicos para el sistema de aforo
"""
import math
from typing import Tuple, Optional


def calculate_flow_manning(
    water_level: float,
    channel_width: float,
    slope: float,
    manning_n: float,
    base_level: float = 0
) -> Tuple[float, float, float]:
    """
    Calcula el caudal usando la ecuación de Manning para canal rectangular.

    Q = (1/n) * A * R^(2/3) * S^(1/2)

    Args:
        water_level: Nivel de agua medido (m)
        channel_width: Ancho del canal (m)
        slope: Pendiente del canal (m/m)
        manning_n: Coeficiente de rugosidad de Manning
        base_level: Nivel base del canal (m)

    Returns:
        Tuple con (caudal m³/s, velocidad m/s, área m²)
    """
    # Altura efectiva del agua
    h = water_level - base_level
    if h <= 0:
        return 0.0, 0.0, 0.0

    # Área de la sección transversal (rectangular)
    area = channel_width * h

    # Perímetro mojado
    wetted_perimeter = channel_width + 2 * h

    # Radio hidráulico
    hydraulic_radius = area / wetted_perimeter

    # Velocidad usando Manning
    velocity = (1 / manning_n) * (hydraulic_radius ** (2/3)) * (slope ** 0.5)

    # Caudal
    flow_rate = area * velocity

    return round(flow_rate, 4), round(velocity, 4), round(area, 4)


def calculate_flow_rating_curve(
    water_level: float,
    coefficient_a: float,
    coefficient_b: float,
    base_level: float = 0
) -> float:
    """
    Calcula el caudal usando una curva de aforo (rating curve).

    Q = a * (h - h0)^b

    Args:
        water_level: Nivel de agua medido (m)
        coefficient_a: Coeficiente 'a' de la curva
        coefficient_b: Exponente 'b' de la curva
        base_level: Nivel base h0 (m)

    Returns:
        Caudal en m³/s
    """
    h = water_level - base_level
    if h <= 0:
        return 0.0

    flow_rate = coefficient_a * (h ** coefficient_b)
    return round(flow_rate, 4)


def calculate_velocity_from_flow(flow_rate: float, area: float) -> float:
    """
    Calcula la velocidad a partir del caudal y área.

    V = Q / A

    Args:
        flow_rate: Caudal (m³/s)
        area: Área de sección transversal (m²)

    Returns:
        Velocidad en m/s
    """
    if area <= 0:
        return 0.0
    return round(flow_rate / area, 4)


def estimate_cross_section_area(
    water_level: float,
    channel_width: float,
    base_level: float = 0
) -> float:
    """
    Estima el área de sección transversal para canal rectangular.

    Args:
        water_level: Nivel de agua (m)
        channel_width: Ancho del canal (m)
        base_level: Nivel base (m)

    Returns:
        Área en m²
    """
    h = water_level - base_level
    if h <= 0:
        return 0.0
    return round(channel_width * h, 4)


def calculate_hydraulic_parameters(
    water_level: float,
    channel_width: Optional[float],
    slope: float,
    manning_n: float,
    coef_a: float,
    coef_b: float,
    base_level: float
) -> Tuple[float, float, float]:
    """
    Calcula todos los parámetros hidráulicos para una medición.

    Usa la ecuación de Manning si hay ancho de canal disponible,
    de lo contrario usa la curva de aforo.

    Args:
        water_level: Nivel de agua medido (m)
        channel_width: Ancho del canal (m), puede ser None
        slope: Pendiente del canal
        manning_n: Coeficiente de Manning
        coef_a: Coeficiente 'a' de curva de aforo
        coef_b: Coeficiente 'b' de curva de aforo
        base_level: Nivel base

    Returns:
        Tuple con (caudal, velocidad, área)
    """
    if channel_width and channel_width > 0:
        # Usar ecuación de Manning
        flow_rate, velocity, area = calculate_flow_manning(
            water_level, channel_width, slope, manning_n, base_level
        )
    else:
        # Usar curva de aforo
        flow_rate = calculate_flow_rating_curve(
            water_level, coef_a, coef_b, base_level
        )
        # Estimar área y velocidad usando valores típicos
        # Asumimos un ancho típico de 5m si no se especifica
        estimated_width = 5.0
        area = estimate_cross_section_area(water_level, estimated_width, base_level)
        velocity = calculate_velocity_from_flow(flow_rate, area) if area > 0 else 0.0

    return flow_rate, velocity, area


def convert_units(value: float, from_unit: str, to_unit: str) -> float:
    """
    Convierte unidades comunes en hidrología.

    Args:
        value: Valor a convertir
        from_unit: Unidad de origen
        to_unit: Unidad de destino

    Returns:
        Valor convertido
    """
    # Conversiones de caudal
    flow_conversions = {
        ('m3/s', 'l/s'): 1000,
        ('l/s', 'm3/s'): 0.001,
        ('m3/s', 'm3/h'): 3600,
        ('m3/h', 'm3/s'): 1/3600,
        ('m3/s', 'ft3/s'): 35.3147,
        ('ft3/s', 'm3/s'): 0.0283168,
    }

    # Conversiones de longitud
    length_conversions = {
        ('m', 'cm'): 100,
        ('cm', 'm'): 0.01,
        ('m', 'ft'): 3.28084,
        ('ft', 'm'): 0.3048,
    }

    all_conversions = {**flow_conversions, **length_conversions}

    key = (from_unit, to_unit)
    if key in all_conversions:
        return value * all_conversions[key]

    return value


def calculate_daily_volume(flow_rate: float, hours: float = 24) -> float:
    """
    Calcula el volumen de agua para un período dado.

    Args:
        flow_rate: Caudal promedio (m³/s)
        hours: Número de horas

    Returns:
        Volumen en m³
    """
    return round(flow_rate * hours * 3600, 2)


def get_froude_number(velocity: float, depth: float) -> float:
    """
    Calcula el número de Froude.

    Fr = V / sqrt(g * h)

    Args:
        velocity: Velocidad del flujo (m/s)
        depth: Profundidad del agua (m)

    Returns:
        Número de Froude (adimensional)
    """
    g = 9.81  # Aceleración gravitacional
    if depth <= 0:
        return 0.0
    return round(velocity / math.sqrt(g * depth), 4)


def classify_flow_regime(froude_number: float) -> str:
    """
    Clasifica el régimen de flujo basado en el número de Froude.

    Args:
        froude_number: Número de Froude

    Returns:
        Clasificación del flujo
    """
    if froude_number < 1:
        return "subcrítico"
    elif froude_number == 1:
        return "crítico"
    else:
        return "supercrítico"
