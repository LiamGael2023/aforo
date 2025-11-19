<?php
namespace App\Controllers;

use App\Core\Controller;
use App\Models\Station;
use App\Models\Measurement;
use App\Models\Alert;

class DashboardController extends Controller
{
    private $stationModel;
    private $measurementModel;
    private $alertModel;

    public function __construct()
    {
        parent::__construct();
        $this->stationModel = new Station();
        $this->measurementModel = new Measurement();
        $this->alertModel = new Alert();
    }

    /**
     * Página principal del dashboard
     */
    public function index(): void
    {
        $this->view('dashboard/index');
    }

    /**
     * API: Resumen del dashboard
     */
    public function summary(): void
    {
        $summary = [
            'total_stations' => $this->stationModel->count(),
            'active_stations' => $this->stationModel->count(['is_active' => 1]),
            'total_measurements_today' => $this->measurementModel->countToday(),
            'active_alerts' => $this->alertModel->countActive(),
            'critical_alerts' => $this->alertModel->countCritical(),
            'stations_by_alert_level' => $this->stationModel->getStatsByAlertLevel()
        ];

        $this->json($summary);
    }

    /**
     * API: Datos para gráficos
     */
    public function chartData(string $stationId): void
    {
        $station = $this->stationModel->find((int) $stationId);

        if (!$station) {
            $this->json(['error' => 'Estación no encontrada'], 404);
            return;
        }

        $hours = isset($_GET['hours']) ? (int) $_GET['hours'] : 24;
        $measurements = $this->measurementModel->getChartData((int) $stationId, $hours);

        $data = [
            'timestamps' => [],
            'levels' => [],
            'flows' => [],
            'station_name' => $station['name'],
            'station_code' => $station['code']
        ];

        foreach ($measurements as $m) {
            $data['timestamps'][] = date('Y-m-d H:i', strtotime($m['timestamp']));
            $data['levels'][] = (float) $m['water_level'];
            $data['flows'][] = (float) $m['flow_rate'];
        }

        $this->json($data);
    }
}
