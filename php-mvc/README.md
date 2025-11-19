# Sistema de Aforo Digital - PHP MVC + MySQL

Sistema integral para el monitoreo y medición del caudal en cuerpos de agua, implementado con arquitectura MVC en PHP y MySQL.

## Características

- **Arquitectura MVC**: Modelos, Vistas y Controladores bien separados
- **API REST**: Endpoints completos para gestión del sistema
- **Cálculos Hidráulicos**: Ecuación de Manning y curvas de aforo
- **Sistema de Alertas**: Niveles bajo, normal, alto y crítico
- **Dashboard Interactivo**: Gráficos con Chart.js
- **Base de Datos MySQL**: Esquema completo con relaciones

## Estructura del Proyecto

```
php-mvc/
├── app/
│   ├── Controllers/
│   │   ├── DashboardController.php
│   │   ├── StationController.php
│   │   ├── MeasurementController.php
│   │   ├── AlertController.php
│   │   └── SeedController.php
│   ├── Models/
│   │   ├── Station.php
│   │   ├── Measurement.php
│   │   └── Alert.php
│   ├── Views/
│   │   ├── layouts/main.php
│   │   └── dashboard/index.php
│   └── Core/
│       ├── Controller.php
│       ├── Model.php
│       ├── Database.php
│       ├── Router.php
│       └── HydraulicCalculator.php
├── config/
│   ├── app.php
│   └── database.php
├── database/
│   └── schema.sql
├── public/
│   ├── index.php
│   ├── .htaccess
│   ├── css/styles.css
│   └── js/dashboard.js
└── README.md
```

## Requisitos

- PHP 7.4 o superior
- MySQL 5.7 o superior
- Apache con mod_rewrite habilitado

## Instalación

### 1. Configurar Base de Datos

```bash
# Conectar a MySQL
mysql -u root -p

# Crear base de datos y tablas
source /path/to/php-mvc/database/schema.sql
```

### 2. Configurar Conexión

Editar `config/database.php`:

```php
return [
    'host' => 'localhost',
    'database' => 'aforo_digital',
    'username' => 'root',
    'password' => 'tu_password',
    'charset' => 'utf8mb4',
    'port' => 3306
];
```

### 3. Configurar Apache

Opción A - Virtual Host:

```apache
<VirtualHost *:80>
    ServerName aforo.local
    DocumentRoot /var/www/aforo/php-mvc/public

    <Directory /var/www/aforo/php-mvc/public>
        AllowOverride All
        Require all granted
    </Directory>
</VirtualHost>
```

Opción B - Servidor embebido PHP:

```bash
cd php-mvc/public
php -S localhost:8000
```

### 4. Acceder al Sistema

```
http://localhost:8000
```

## API Endpoints

### Estaciones
- `GET /api/stations` - Listar estaciones
- `GET /api/stations/with-latest` - Estaciones con última medición
- `POST /api/stations` - Crear estación
- `GET /api/stations/{id}` - Obtener estación
- `PUT /api/stations/{id}` - Actualizar estación
- `DELETE /api/stations/{id}` - Eliminar estación

### Mediciones
- `GET /api/measurements` - Listar mediciones
- `GET /api/measurements/latest` - Últimas mediciones
- `GET /api/measurements/station/{id}` - Por estación
- `POST /api/measurements` - Registrar medición
- `GET /api/measurements/{id}` - Obtener medición

### Alertas
- `GET /api/alerts` - Alertas activas
- `GET /api/alerts/history` - Historial
- `GET /api/alerts/statistics` - Estadísticas
- `PUT /api/alerts/{id}/acknowledge` - Reconocer alerta

### Dashboard
- `GET /api/dashboard/summary` - Resumen del sistema
- `GET /api/dashboard/charts/{id}` - Datos para gráficos

### Utilidades
- `POST /api/seed-data` - Cargar datos de ejemplo
- `GET /api/info` - Información del sistema

## Ejemplos de Uso

### Crear Estación

```bash
curl -X POST http://localhost:8000/api/stations \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Estación Río Grande",
    "code": "RG-001",
    "latitude": -34.6037,
    "longitude": -58.3816,
    "water_body_name": "Río Grande",
    "channel_type": "river",
    "channel_width": 15.0
  }'
```

### Registrar Medición

```bash
curl -X POST http://localhost:8000/api/measurements \
  -H "Content-Type: application/json" \
  -d '{
    "station_id": 1,
    "water_level": 1.85,
    "water_temperature": 18.5,
    "turbidity": 25.0
  }'
```

### Obtener Resumen

```bash
curl http://localhost:8000/api/dashboard/summary
```

## Cálculos Hidráulicos

### Ecuación de Manning
```
Q = (1/n) * A * R^(2/3) * S^(1/2)
```

### Curva de Aforo
```
Q = a * (h - h0)^b
```

## Niveles de Alerta

| Nivel | Color | Acción |
|-------|-------|--------|
| Low | Azul | Monitoreo |
| Normal | Verde | Operación normal |
| High | Amarillo | Precaución |
| Critical | Rojo | Acción inmediata |

## Licencia

MIT License
