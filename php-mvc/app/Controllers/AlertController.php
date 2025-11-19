<?php
namespace App\Controllers;

use App\Core\Controller;
use App\Models\Alert;

class AlertController extends Controller
{
    private $model;

    public function __construct()
    {
        parent::__construct();
        $this->model = new Alert();
    }

    /**
     * Lista alertas activas
     */
    public function index(): void
    {
        $activeOnly = !isset($_GET['active_only']) || $_GET['active_only'] !== 'false';

        if ($activeOnly) {
            $alerts = $this->model->getActive();
        } else {
            $alerts = $this->model->getHistory();
        }

        $this->json($alerts);
    }

    /**
     * Historial de alertas
     */
    public function history(): void
    {
        $limit = isset($_GET['limit']) ? (int) $_GET['limit'] : 100;
        $alerts = $this->model->getHistory($limit);
        $this->json($alerts);
    }

    /**
     * Estadísticas de alertas
     */
    public function statistics(): void
    {
        $stats = $this->model->getStatistics();
        $this->json($stats);
    }

    /**
     * Obtiene una alerta por ID
     */
    public function show(string $id): void
    {
        $alert = $this->model->find((int) $id);

        if (!$alert) {
            $this->json(['error' => 'Alerta no encontrada'], 404);
            return;
        }

        $this->json($alert);
    }

    /**
     * Reconoce una alerta
     */
    public function acknowledge(string $id): void
    {
        $alert = $this->model->find((int) $id);

        if (!$alert) {
            $this->json(['error' => 'Alerta no encontrada'], 404);
            return;
        }

        $data = $this->getJsonInput();

        if (empty($data['acknowledged_by'])) {
            $this->json(['error' => 'acknowledged_by es requerido'], 400);
            return;
        }

        $this->model->acknowledge((int) $id, $data['acknowledged_by']);

        $this->json([
            'message' => 'Alerta reconocida',
            'alert_id' => (int) $id
        ]);
    }
}
