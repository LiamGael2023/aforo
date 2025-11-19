<?php
namespace App\Models;

use App\Core\Model;
use App\Core\HydraulicCalculator;

class Alert extends Model
{
    protected $table = 'alerts';

    /**
     * Crea alerta si es necesario
     */
    public function createIfNeeded(array $station, float $waterLevel, float $flowRate, string $alertLevel): ?int
    {
        // No crear alerta para nivel normal
        if ($alertLevel === 'normal') {
            return null;
        }

        // Verificar si ya hay una alerta activa del mismo nivel
        $existing = $this->db->fetch(
            "SELECT id FROM {$this->table}
             WHERE station_id = :station_id
               AND alert_level = :alert_level
               AND is_active = 1",
            [
                'station_id' => $station['id'],
                'alert_level' => $alertLevel
            ]
        );

        if ($existing) {
            return null;
        }

        // Generar mensaje
        $message = HydraulicCalculator::getAlertMessage($alertLevel, $waterLevel, $station['name']);

        // Crear alerta
        return $this->create([
            'station_id' => $station['id'],
            'alert_level' => $alertLevel,
            'message' => $message,
            'water_level' => $waterLevel,
            'flow_rate' => $flowRate
        ]);
    }

    /**
     * Resuelve alertas activas de una estación
     */
    public function resolveForStation(int $stationId): void
    {
        $this->db->query(
            "UPDATE {$this->table}
             SET is_active = 0, resolved_at = NOW()
             WHERE station_id = :station_id AND is_active = 1",
            ['station_id' => $stationId]
        );
    }

    /**
     * Obtiene alertas activas
     */
    public function getActive(): array
    {
        $sql = "
            SELECT a.*, s.name as station_name, s.code as station_code
            FROM {$this->table} a
            JOIN stations s ON a.station_id = s.id
            WHERE a.is_active = 1
            ORDER BY
                FIELD(a.alert_level, 'critical', 'high', 'low', 'normal'),
                a.created_at DESC
        ";

        return $this->db->fetchAll($sql);
    }

    /**
     * Obtiene historial de alertas
     */
    public function getHistory(int $limit = 100): array
    {
        $sql = "
            SELECT a.*, s.name as station_name, s.code as station_code
            FROM {$this->table} a
            JOIN stations s ON a.station_id = s.id
            ORDER BY a.created_at DESC
            LIMIT {$limit}
        ";

        return $this->db->fetchAll($sql);
    }

    /**
     * Reconoce una alerta
     */
    public function acknowledge(int $id, string $acknowledgedBy): bool
    {
        return $this->update($id, [
            'is_acknowledged' => 1,
            'acknowledged_by' => $acknowledgedBy,
            'acknowledged_at' => date('Y-m-d H:i:s')
        ]);
    }

    /**
     * Cuenta alertas activas
     */
    public function countActive(): int
    {
        return $this->count(['is_active' => 1]);
    }

    /**
     * Cuenta alertas críticas activas
     */
    public function countCritical(): int
    {
        $sql = "SELECT COUNT(*) as count FROM {$this->table}
                WHERE is_active = 1 AND alert_level = 'critical'";
        $result = $this->db->fetch($sql);
        return (int) $result['count'];
    }

    /**
     * Obtiene estadísticas de alertas
     */
    public function getStatistics(): array
    {
        $sql = "
            SELECT
                alert_level,
                COUNT(*) as count
            FROM {$this->table}
            WHERE is_active = 1
            GROUP BY alert_level
        ";

        $results = $this->db->fetchAll($sql);
        $stats = [
            'total_active' => 0,
            'critical' => 0,
            'high' => 0,
            'low' => 0,
            'unacknowledged' => 0
        ];

        foreach ($results as $row) {
            $stats[$row['alert_level']] = (int) $row['count'];
            $stats['total_active'] += (int) $row['count'];
        }

        // Contar no reconocidas
        $sql = "SELECT COUNT(*) as count FROM {$this->table}
                WHERE is_active = 1 AND is_acknowledged = 0";
        $result = $this->db->fetch($sql);
        $stats['unacknowledged'] = (int) $result['count'];

        return $stats;
    }
}
