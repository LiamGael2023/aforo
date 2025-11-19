<?php
namespace App\Controllers;

use App\Core\Controller;
use App\Models\Station;

class StationController extends Controller
{
    private $model;

    public function __construct()
    {
        parent::__construct();
        $this->model = new Station();
    }

    /**
     * Lista todas las estaciones
     */
    public function index(): void
    {
        $activeOnly = isset($_GET['active_only']) && $_GET['active_only'] === 'true';

        if ($activeOnly) {
            $stations = $this->model->getActive();
        } else {
            $stations = $this->model->all([], 'name ASC');
        }

        $this->json($stations);
    }

    /**
     * Estaciones con última medición
     */
    public function withLatest(): void
    {
        $stations = $this->model->getWithLatestMeasurement();
        $this->json($stations);
    }

    /**
     * Obtiene una estación por ID
     */
    public function show(string $id): void
    {
        $station = $this->model->find((int) $id);

        if (!$station) {
            $this->json(['error' => 'Estación no encontrada'], 404);
            return;
        }

        $this->json($station);
    }

    /**
     * Crea una nueva estación
     */
    public function store(): void
    {
        $data = $this->getJsonInput();

        // Validaciones básicas
        if (empty($data['name']) || empty($data['code'])) {
            $this->json(['error' => 'Nombre y código son requeridos'], 400);
            return;
        }

        // Verificar código único
        if ($this->model->findByCode($data['code'])) {
            $this->json(['error' => 'El código de estación ya existe'], 400);
            return;
        }

        // Crear estación
        $id = $this->model->create([
            'name' => $data['name'],
            'code' => $data['code'],
            'description' => $data['description'] ?? null,
            'latitude' => $data['latitude'],
            'longitude' => $data['longitude'],
            'altitude' => $data['altitude'] ?? 0,
            'water_body_name' => $data['water_body_name'],
            'channel_type' => $data['channel_type'] ?? 'river',
            'channel_width' => $data['channel_width'] ?? null,
            'channel_slope' => $data['channel_slope'] ?? 0.001,
            'manning_coefficient' => $data['manning_coefficient'] ?? 0.035,
            'curve_coefficient_a' => $data['curve_coefficient_a'] ?? 1.0,
            'curve_coefficient_b' => $data['curve_coefficient_b'] ?? 1.5,
            'curve_base_level' => $data['curve_base_level'] ?? 0,
            'level_low' => $data['level_low'] ?? 0.3,
            'level_normal_min' => $data['level_normal_min'] ?? 0.5,
            'level_normal_max' => $data['level_normal_max'] ?? 2.0,
            'level_high' => $data['level_high'] ?? 2.5,
            'level_critical' => $data['level_critical'] ?? 3.0
        ]);

        $station = $this->model->find($id);
        $this->json($station, 201);
    }

    /**
     * Actualiza una estación
     */
    public function update(string $id): void
    {
        $station = $this->model->find((int) $id);

        if (!$station) {
            $this->json(['error' => 'Estación no encontrada'], 404);
            return;
        }

        $data = $this->getJsonInput();

        // Filtrar solo campos permitidos
        $allowed = [
            'name', 'description', 'latitude', 'longitude', 'altitude',
            'water_body_name', 'channel_type', 'channel_width', 'channel_slope',
            'manning_coefficient', 'curve_coefficient_a', 'curve_coefficient_b',
            'curve_base_level', 'level_low', 'level_normal_min', 'level_normal_max',
            'level_high', 'level_critical', 'is_active'
        ];

        $updateData = array_intersect_key($data, array_flip($allowed));

        if (empty($updateData)) {
            $this->json(['error' => 'No hay datos para actualizar'], 400);
            return;
        }

        $this->model->update((int) $id, $updateData);
        $station = $this->model->find((int) $id);

        $this->json($station);
    }

    /**
     * Elimina una estación
     */
    public function destroy(string $id): void
    {
        $station = $this->model->find((int) $id);

        if (!$station) {
            $this->json(['error' => 'Estación no encontrada'], 404);
            return;
        }

        $this->model->delete((int) $id);
        $this->json(['message' => 'Estación eliminada correctamente']);
    }
}
