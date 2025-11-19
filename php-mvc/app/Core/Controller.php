<?php
namespace App\Core;

/**
 * Clase base para controladores
 */
abstract class Controller
{
    protected $db;

    public function __construct()
    {
        $this->db = Database::getInstance();
    }

    /**
     * Renderiza una vista
     */
    protected function view(string $view, array $data = []): void
    {
        extract($data);

        $viewPath = __DIR__ . "/../Views/{$view}.php";

        if (!file_exists($viewPath)) {
            throw new \Exception("Vista no encontrada: {$view}");
        }

        ob_start();
        require $viewPath;
        $content = ob_get_clean();

        // Verificar si hay layout
        $layoutPath = __DIR__ . '/../Views/layouts/main.php';
        if (file_exists($layoutPath)) {
            require $layoutPath;
        } else {
            echo $content;
        }
    }

    /**
     * Respuesta JSON
     */
    protected function json($data, int $statusCode = 200): void
    {
        http_response_code($statusCode);
        header('Content-Type: application/json');
        echo json_encode($data);
        exit;
    }

    /**
     * Obtiene datos JSON del request
     */
    protected function getJsonInput(): array
    {
        $input = file_get_contents('php://input');
        return json_decode($input, true) ?? [];
    }

    /**
     * Redirección
     */
    protected function redirect(string $url): void
    {
        header("Location: {$url}");
        exit;
    }
}
