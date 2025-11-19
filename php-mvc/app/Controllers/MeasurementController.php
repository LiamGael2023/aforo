<?php
namespace App\Controllers;

use App\Core\Controller;
use App\Models\Station;
use App\Models\Measurement;
use App\Models\Alert;

class MeasurementController extends Controller
{
    private $model;
    private $stationModel;
    private $alertModel;

    public function __construct()
    {
        parent::__construct();
        $this->model = new Measurement();
        $this->stationModel = new Station();
        $this->alertModel = new Alert();
    }

    /**
     * Lista mediciones
     */
    public function index(): void
    {
        $stationId = isset($_GET['station_id']) ? (int) $_GET['station_id'] : null;
        $limit = isset($_GET['limit']) ? (int) $_GET['limit'] : 100;

        if ($stationId) {
            $measurements = $this->model->getByStation($stationId, $limit);
        } else {
            $measurements = $this->model->all([], 'timestamp DESC', $limit);
        }

        $this->json($measurements);
    }

    /**
     * Últimas mediciones con info de estación
     */
    public function latest(): void
    {
        $limit = isset($_GET['limit']) ? (int) $_GET['limit'] : 10;
        $measurements = $this->model->getLatestWithStation($limit);
        $this->json($measurements);
    }

    /**
     * Mediciones de una estación
     */
    public function byStation(string $stationId): void
    {
        $station = $this->stationModel->find((int) $stationId);

        if (!$station) {
            $this->json(['error' => 'Estación no encontrada'], 404);
            return;
        }

        $limit = isset($_GET['limit']) ? (int) $_GET['limit'] : 100;
        $measurements = $this->model->getByStation((int) $stationId, $limit);

        $this->json($measurements);
    }

    /**
     * Obtiene una medición por ID
     */
    public function show(string $id): void
    {
        $measurement = $this->model->find((int) $id);

        if (!$measurement) {
            $this->json(['error' => 'Medición no encontrada'], 404);
            return;
        }

        $this->json($measurement);
    }

    /**
     * Crea una nueva medición
     */
    public function store(): void
    {
        $data = $this->getJsonInput();

        // Validaciones
        if (empty($data['station_id']) || !isset($data['water_level'])) {
            $this->json(['error' => 'station_id y water_level son requeridos'], 400);
            return;
        }

        // Obtener estación
        $station = $this->stationModel->find((int) $data['station_id']);

        if (!$station) {
            $this->json(['error' => 'Estación no encontrada'], 404);
            return;
        }

        // Crear medición con cálculos
        $id = $this->model->createWithCalculations($data, $station);
        $measurement = $this->model->find($id);

        // Crear alerta si es necesario
        $alertLevel = $measurement['alert_level'];
        $this->alertModel->createIfNeeded(
            $station,
            (float) $measurement['water_level'],
            (float) $measurement['flow_rate'],
            $alertLevel
        );

        // Resolver alertas si volvió a normal
        if ($alertLevel === 'normal') {
            $this->alertModel->resolveForStation((int) $data['station_id']);
        }

        $this->json($measurement, 201);
    }
}
