-- Schema para Sistema de Aforo Digital de Ríos y Canales
-- MySQL 5.7+

CREATE DATABASE IF NOT EXISTS aforo_digital
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE aforo_digital;

-- Tabla de Estaciones de Aforo
CREATE TABLE IF NOT EXISTS stations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(20) NOT NULL UNIQUE,
    description TEXT,

    -- Ubicación
    latitude DECIMAL(10, 6) NOT NULL,
    longitude DECIMAL(10, 6) NOT NULL,
    altitude DECIMAL(8, 2) DEFAULT 0,

    -- Información del cuerpo de agua
    water_body_name VARCHAR(100) NOT NULL,
    channel_type ENUM('river', 'canal', 'stream', 'irrigation') DEFAULT 'river',

    -- Parámetros hidráulicos
    channel_width DECIMAL(8, 2),
    channel_slope DECIMAL(8, 6) DEFAULT 0.001000,
    manning_coefficient DECIMAL(6, 4) DEFAULT 0.0350,

    -- Parámetros de curva de aforo Q = a * (h - h0)^b
    curve_coefficient_a DECIMAL(10, 4) DEFAULT 1.0000,
    curve_coefficient_b DECIMAL(6, 4) DEFAULT 1.5000,
    curve_base_level DECIMAL(8, 4) DEFAULT 0.0000,

    -- Niveles de alerta (metros)
    level_low DECIMAL(6, 2) DEFAULT 0.30,
    level_normal_min DECIMAL(6, 2) DEFAULT 0.50,
    level_normal_max DECIMAL(6, 2) DEFAULT 2.00,
    level_high DECIMAL(6, 2) DEFAULT 2.50,
    level_critical DECIMAL(6, 2) DEFAULT 3.00,

    -- Estado
    is_active TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_code (code),
    INDEX idx_active (is_active)
) ENGINE=InnoDB;

-- Tabla de Mediciones
CREATE TABLE IF NOT EXISTS measurements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    station_id INT NOT NULL,

    -- Datos de medición
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    water_level DECIMAL(8, 4) NOT NULL,

    -- Datos calculados
    flow_rate DECIMAL(12, 4),
    velocity DECIMAL(8, 4),
    cross_section_area DECIMAL(10, 4),

    -- Datos adicionales
    water_temperature DECIMAL(5, 2),
    turbidity DECIMAL(8, 2),

    -- Metadatos
    measurement_method ENUM('automatic', 'manual') DEFAULT 'automatic',
    notes TEXT,

    -- Estado de alerta
    alert_level ENUM('low', 'normal', 'high', 'critical') DEFAULT 'normal',

    FOREIGN KEY (station_id) REFERENCES stations(id) ON DELETE CASCADE,
    INDEX idx_station (station_id),
    INDEX idx_timestamp (timestamp),
    INDEX idx_alert_level (alert_level)
) ENGINE=InnoDB;

-- Tabla de Alertas
CREATE TABLE IF NOT EXISTS alerts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    station_id INT NOT NULL,

    -- Información de la alerta
    alert_level ENUM('low', 'normal', 'high', 'critical') NOT NULL,
    message TEXT NOT NULL,
    water_level DECIMAL(8, 4),
    flow_rate DECIMAL(12, 4),

    -- Estado
    is_active TINYINT(1) DEFAULT 1,
    is_acknowledged TINYINT(1) DEFAULT 0,
    acknowledged_by VARCHAR(100),
    acknowledged_at TIMESTAMP NULL,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP NULL,

    FOREIGN KEY (station_id) REFERENCES stations(id) ON DELETE CASCADE,
    INDEX idx_station (station_id),
    INDEX idx_active (is_active),
    INDEX idx_level (alert_level)
) ENGINE=InnoDB;

-- Datos de ejemplo
INSERT INTO stations (name, code, description, latitude, longitude, altitude, water_body_name, channel_type, channel_width, channel_slope, manning_coefficient, level_low, level_normal_min, level_normal_max, level_high, level_critical) VALUES
('Estación Río Grande', 'RG-001', 'Estación principal del Río Grande, zona urbana', -34.603700, -58.381600, 25.00, 'Río Grande', 'river', 15.00, 0.001500, 0.0350, 0.50, 0.80, 2.50, 3.00, 4.00),
('Canal de Riego Norte', 'CN-001', 'Canal principal de riego zona norte', -34.587500, -58.417000, 30.00, 'Canal Norte', 'irrigation', 5.00, 0.002000, 0.0250, 0.20, 0.40, 1.20, 1.50, 2.00),
('Arroyo Las Piedras', 'AP-001', 'Arroyo secundario, zona periurbana', -34.620000, -58.350000, 20.00, 'Arroyo Las Piedras', 'stream', 8.00, 0.003000, 0.0400, 0.30, 0.50, 1.80, 2.20, 3.00);
