<?php
namespace App\Core;

/**
 * Router simple para manejo de rutas
 */
class Router
{
    private $routes = [];
    private $notFoundCallback;

    public function get(string $path, $callback): self
    {
        $this->addRoute('GET', $path, $callback);
        return $this;
    }

    public function post(string $path, $callback): self
    {
        $this->addRoute('POST', $path, $callback);
        return $this;
    }

    public function put(string $path, $callback): self
    {
        $this->addRoute('PUT', $path, $callback);
        return $this;
    }

    public function delete(string $path, $callback): self
    {
        $this->addRoute('DELETE', $path, $callback);
        return $this;
    }

    private function addRoute(string $method, string $path, $callback): void
    {
        $path = $this->normalizePath($path);
        $this->routes[$method][$path] = $callback;
    }

    private function normalizePath(string $path): string
    {
        $path = trim($path, '/');
        $path = "/{$path}";
        $path = preg_replace('#[/]{2,}#', '/', $path);
        return $path;
    }

    public function notFound($callback): self
    {
        $this->notFoundCallback = $callback;
        return $this;
    }

    public function dispatch(): void
    {
        $method = $_SERVER['REQUEST_METHOD'];
        $path = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);

        // Remover base path si existe
        $basePath = dirname($_SERVER['SCRIPT_NAME']);
        if ($basePath !== '/' && strpos($path, $basePath) === 0) {
            $path = substr($path, strlen($basePath));
        }

        $path = $this->normalizePath($path);

        // Buscar ruta exacta
        if (isset($this->routes[$method][$path])) {
            $this->executeCallback($this->routes[$method][$path]);
            return;
        }

        // Buscar ruta con parámetros
        foreach ($this->routes[$method] ?? [] as $route => $callback) {
            $pattern = preg_replace('/\{([a-zA-Z_]+)\}/', '(?P<$1>[^/]+)', $route);
            $pattern = "#^{$pattern}$#";

            if (preg_match($pattern, $path, $matches)) {
                $params = array_filter($matches, 'is_string', ARRAY_FILTER_USE_KEY);
                $this->executeCallback($callback, $params);
                return;
            }
        }

        // 404 Not Found
        http_response_code(404);
        if ($this->notFoundCallback) {
            $this->executeCallback($this->notFoundCallback);
        } else {
            echo json_encode(['error' => 'Not Found']);
        }
    }

    private function executeCallback($callback, array $params = []): void
    {
        if (is_array($callback)) {
            [$controller, $method] = $callback;
            $controller = new $controller();
            call_user_func_array([$controller, $method], $params);
        } elseif (is_callable($callback)) {
            call_user_func_array($callback, $params);
        }
    }
}
