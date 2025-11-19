<?php
/**
 * Sistema de Aforo Digital de Ríos y Canales
 * Punto de entrada principal
 */

// Configuración de errores
error_reporting(E_ALL);
ini_set('display_errors', 1);

// Autoloader
spl_autoload_register(function ($class) {
    $prefix = 'App\\';
    $baseDir = __DIR__ . '/../app/';

    $len = strlen($prefix);
    if (strncmp($prefix, $class, $len) !== 0) {
        return;
    }

    $relativeClass = substr($class, $len);
    $file = $baseDir . str_replace('\\', '/', $relativeClass) . '.php';

    if (file_exists($file)) {
        require $file;
    }
});

// Timezone
date_default_timezone_set('America/Argentina/Buenos_Aires');

// Router
use App\Core\Router;
use App\Controllers\DashboardController;
use App\Controllers\StationController;
use App\Controllers\MeasurementController;
use App\Controllers\AlertController;
use App\Controllers\SeedController;

$router = new Router();

// Rutas del Dashboard
$router->get('/', [DashboardController::class, 'index']);
$router->get('/api/dashboard/summary', [DashboardController::class, 'summary']);
$router->get('/api/dashboard/charts/{stationId}', [DashboardController::class, 'chartData']);

// Rutas de Estaciones
$router->get('/api/stations', [StationController::class, 'index']);
$router->get('/api/stations/with-latest', [StationController::class, 'withLatest']);
$router->get('/api/stations/{id}', [StationController::class, 'show']);
$router->post('/api/stations', [StationController::class, 'store']);
$router->put('/api/stations/{id}', [StationController::class, 'update']);
$router->delete('/api/stations/{id}', [StationController::class, 'destroy']);

// Rutas de Mediciones
$router->get('/api/measurements', [MeasurementController::class, 'index']);
$router->get('/api/measurements/latest', [MeasurementController::class, 'latest']);
$router->get('/api/measurements/station/{stationId}', [MeasurementController::class, 'byStation']);
$router->get('/api/measurements/{id}', [MeasurementController::class, 'show']);
$router->post('/api/measurements', [MeasurementController::class, 'store']);

// Rutas de Alertas
$router->get('/api/alerts', [AlertController::class, 'index']);
$router->get('/api/alerts/history', [AlertController::class, 'history']);
$router->get('/api/alerts/statistics', [AlertController::class, 'statistics']);
$router->get('/api/alerts/{id}', [AlertController::class, 'show']);
$router->put('/api/alerts/{id}/acknowledge', [AlertController::class, 'acknowledge']);

// Ruta para datos de ejemplo
$router->post('/api/seed-data', [SeedController::class, 'seed']);

// Información del sistema
$router->get('/api/info', function () {
    header('Content-Type: application/json');
    echo json_encode([
        'name' => 'Sistema de Aforo Digital de Ríos y Canales',
        'version' => '1.0.0',
        'description' => 'Sistema integral para monitoreo de caudales en cuerpos de agua',
        'framework' => 'PHP MVC',
        'database' => 'MySQL'
    ]);
});

// 404
$router->notFound(function () {
    http_response_code(404);
    header('Content-Type: application/json');
    echo json_encode(['error' => 'Ruta no encontrada']);
});

// Ejecutar router
$router->dispatch();
