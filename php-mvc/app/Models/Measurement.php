<?php
namespace App\Models;

use App\Core\Model;
use App\Core\HydraulicCalculator;

class Measurement extends Model
{
    protected $table = 'measurements';

    /**
     * Crea una nueva medición con cálculos automáticos
     */
    public function createWithCalculations(array $data, array $station): int
    {
        // Calcular parámetros hidráulicos
        $params = HydraulicCalculator::calculateHydraulicParameters(
            $station,
            (float) $data['water_level']
        );

        // Determinar nivel de alerta
        $alertLevel = HydraulicCalculator::determineAlertLevel(
            $station,
            (float) $data['water_level']
        );

        // Preparar datos para inserción
        $measurementData = [
            'station_id' => $data['station_id'],
            'water_level' => $data['water_level'],
            'flow_rate' => $params['flow_rate'],
            'velocity' => $params['velocity'],
            'cross_section_area' => $params['area'],
            'water_temperature' => $data['water_temperature'] ?? null,
            'turbidity' => $data['turbidity'] ?? null,
            'measurement_method' => $data['measurement_method'] ?? 'automatic',
            'notes' => $data['notes'] ?? null,
            'alert_level' => $alertLevel
        ];

        return $this->create($measurementData);
    }

    /**
     * Obtiene mediciones por estación
     */
    public function getByStation(int $stationId, int $limit = 100): array
    {
        $sql = "SELECT * FROM {$this->table}
                WHERE station_id = :station_id
                ORDER BY timestamp DESC
                LIMIT {$limit}";

        return $this->db->fetchAll($sql, ['station_id' => $stationId]);
    }

    /**
     * Obtiene últimas mediciones con info de estación
     */
    public function getLatestWithStation(int $limit = 10): array
    {
        $sql = "
            SELECT m.*, s.name as station_name, s.code as station_code
            FROM {$this->table} m
            JOIN stations s ON m.station_id = s.id
            ORDER BY m.timestamp DESC
            LIMIT {$limit}
        ";

        return $this->db->fetchAll($sql);
    }

    /**
     * Obtiene datos para gráficos
     */
    public function getChartData(int $stationId, int $hours = 24): array
    {
        $sql = "
            SELECT timestamp, water_level, flow_rate
            FROM {$this->table}
            WHERE station_id = :station_id
              AND timestamp >= DATE_SUB(NOW(), INTERVAL :hours HOUR)
            ORDER BY timestamp ASC
        ";

        return $this->db->fetchAll($sql, [
            'station_id' => $stationId,
            'hours' => $hours
        ]);
    }

    /**
     * Cuenta mediciones de hoy
     */
    public function countToday(): int
    {
        $sql = "SELECT COUNT(*) as count FROM {$this->table}
                WHERE DATE(timestamp) = CURDATE()";
        $result = $this->db->fetch($sql);
        return (int) $result['count'];
    }

    /**
     * Obtiene última medición de una estación
     */
    public function getLatestByStation(int $stationId): ?array
    {
        $sql = "SELECT * FROM {$this->table}
                WHERE station_id = :station_id
                ORDER BY timestamp DESC
                LIMIT 1";

        return $this->db->fetch($sql, ['station_id' => $stationId]);
    }
}
