<?php
namespace App\Controllers;

use App\Core\Controller;
use App\Models\Station;
use App\Models\Measurement;

class SeedController extends Controller
{
    private $stationModel;
    private $measurementModel;

    public function __construct()
    {
        parent::__construct();
        $this->stationModel = new Station();
        $this->measurementModel = new Measurement();
    }

    /**
     * Crea datos de ejemplo
     */
    public function seed(): void
    {
        // Verificar si ya hay datos
        if ($this->stationModel->count() > 0) {
            $this->json(['message' => 'Ya existen datos en el sistema']);
            return;
        }

        // Las estaciones ya están en el schema.sql
        // Obtener estaciones
        $stations = $this->stationModel->all();

        if (empty($stations)) {
            $this->json(['error' => 'No se encontraron estaciones'], 500);
            return;
        }

        $measurementsCreated = 0;

        foreach ($stations as $station) {
            // Nivel base para esta estación
            $baseLevel = ((float) $station['level_normal_min'] + (float) $station['level_normal_max']) / 2;

            // Crear mediciones para las últimas 24 horas
            for ($i = 0; $i < 48; $i++) {
                $minutesAgo = 30 * (47 - $i);
                $timestamp = date('Y-m-d H:i:s', strtotime("-{$minutesAgo} minutes"));

                // Variación del nivel
                $variation = (mt_rand(-30, 30) / 100);
                $waterLevel = max(0.1, $baseLevel + $variation);

                $data = [
                    'station_id' => $station['id'],
                    'water_level' => round($waterLevel, 2),
                    'water_temperature' => round(mt_rand(150, 250) / 10, 1),
                    'turbidity' => round(mt_rand(50, 500) / 10, 1),
                    'measurement_method' => 'automatic'
                ];

                $id = $this->measurementModel->createWithCalculations($data, $station);

                // Actualizar timestamp
                $this->db->query(
                    "UPDATE measurements SET timestamp = :timestamp WHERE id = :id",
                    ['timestamp' => $timestamp, 'id' => $id]
                );

                $measurementsCreated++;
            }
        }

        $this->json([
            'message' => 'Datos de ejemplo creados correctamente',
            'stations_created' => count($stations),
            'measurements_created' => $measurementsCreated
        ]);
    }
}
