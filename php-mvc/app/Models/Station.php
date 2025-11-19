<?php
namespace App\Models;

use App\Core\Model;

class Station extends Model
{
    protected $table = 'stations';

    /**
     * Obtiene todas las estaciones activas
     */
    public function getActive(): array
    {
        return $this->all(['is_active' => 1], 'name ASC');
    }

    /**
     * Busca estación por código
     */
    public function findByCode(string $code): ?array
    {
        $sql = "SELECT * FROM {$this->table} WHERE code = :code";
        return $this->db->fetch($sql, ['code' => $code]);
    }

    /**
     * Obtiene estaciones con última medición
     */
    public function getWithLatestMeasurement(): array
    {
        $sql = "
            SELECT s.*,
                   m.water_level as latest_level,
                   m.flow_rate as latest_flow,
                   m.alert_level as current_alert_level,
                   m.timestamp as last_measurement
            FROM {$this->table} s
            LEFT JOIN (
                SELECT station_id, water_level, flow_rate, alert_level, timestamp
                FROM measurements m1
                WHERE timestamp = (
                    SELECT MAX(timestamp)
                    FROM measurements m2
                    WHERE m2.station_id = m1.station_id
                )
            ) m ON s.id = m.station_id
            WHERE s.is_active = 1
            ORDER BY s.name
        ";

        return $this->db->fetchAll($sql);
    }

    /**
     * Obtiene estadísticas de estaciones por nivel de alerta
     */
    public function getStatsByAlertLevel(): array
    {
        $sql = "
            SELECT
                COALESCE(m.alert_level, 'normal') as alert_level,
                COUNT(*) as count
            FROM {$this->table} s
            LEFT JOIN (
                SELECT station_id, alert_level
                FROM measurements m1
                WHERE timestamp = (
                    SELECT MAX(timestamp)
                    FROM measurements m2
                    WHERE m2.station_id = m1.station_id
                )
            ) m ON s.id = m.station_id
            WHERE s.is_active = 1
            GROUP BY COALESCE(m.alert_level, 'normal')
        ";

        $results = $this->db->fetchAll($sql);
        $stats = ['normal' => 0, 'low' => 0, 'high' => 0, 'critical' => 0];

        foreach ($results as $row) {
            $stats[$row['alert_level']] = (int) $row['count'];
        }

        return $stats;
    }
}
