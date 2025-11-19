# Sistema de Aforo Digital de Ríos y Canales

Sistema integral para el monitoreo y medición del caudal en cuerpos de agua, diseñado para estaciones de aforo hidrológico.

## Características

- **Gestión de Estaciones**: Registro y administración de estaciones de monitoreo
- **Mediciones en Tiempo Real**: Registro de niveles de agua y cálculo automático de caudales
- **Alertas Inteligentes**: Sistema de alertas por niveles críticos (bajo, normal, alto, crítico)
- **Cálculos Hidráulicos**: Fórmulas de Manning y relaciones nivel-caudal
- **Dashboard Interactivo**: Visualización de datos con gráficos y mapas
- **Histórico de Datos**: Consulta y exportación de mediciones históricas
- **Reportes**: Generación de informes de caudales y niveles

## Estructura del Proyecto

```
aforo/
├── app/
│   ├── __init__.py
│   ├── main.py              # Aplicación FastAPI principal
│   ├── models.py            # Modelos de base de datos
│   ├── schemas.py           # Esquemas Pydantic
│   ├── database.py          # Configuración de BD
│   ├── crud.py              # Operaciones CRUD
│   ├── calculations.py      # Cálculos hidráulicos
│   └── alerts.py            # Sistema de alertas
├── static/
│   ├── css/
│   │   └── styles.css
│   └── js/
│       └── dashboard.js
├── templates/
│   └── index.html
├── requirements.txt
└── README.md
```

## Instalación

1. Clonar el repositorio:
```bash
git clone <repository-url>
cd aforo
```

2. Crear entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Ejecutar la aplicación:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

5. Acceder al dashboard:
```
http://localhost:8000
```

## API Endpoints

### Estaciones
- `GET /api/stations` - Listar todas las estaciones
- `POST /api/stations` - Crear nueva estación
- `GET /api/stations/{id}` - Obtener estación por ID
- `PUT /api/stations/{id}` - Actualizar estación
- `DELETE /api/stations/{id}` - Eliminar estación

### Mediciones
- `GET /api/measurements` - Listar mediciones
- `POST /api/measurements` - Registrar nueva medición
- `GET /api/measurements/station/{station_id}` - Mediciones por estación
- `GET /api/measurements/latest` - Últimas mediciones

### Alertas
- `GET /api/alerts` - Listar alertas activas
- `GET /api/alerts/history` - Historial de alertas
- `PUT /api/alerts/{id}/acknowledge` - Reconocer alerta

### Dashboard
- `GET /api/dashboard/summary` - Resumen del sistema
- `GET /api/dashboard/charts/{station_id}` - Datos para gráficos

## Conceptos Hidráulicos

### Cálculo de Caudal
El sistema utiliza la ecuación de Manning para calcular el caudal:

```
Q = (1/n) * A * R^(2/3) * S^(1/2)
```

Donde:
- Q = Caudal (m³/s)
- n = Coeficiente de rugosidad de Manning
- A = Área de la sección transversal (m²)
- R = Radio hidráulico (m)
- S = Pendiente del canal

### Curva de Aforo
También se puede usar una curva de aforo (relación nivel-caudal):

```
Q = a * (h - h0)^b
```

Donde:
- h = Nivel de agua medido (m)
- h0 = Nivel base (m)
- a, b = Coeficientes de la curva

## Niveles de Alerta

| Nivel | Descripción | Color |
|-------|-------------|-------|
| Bajo | Nivel inferior al mínimo operativo | Azul |
| Normal | Nivel dentro del rango operativo | Verde |
| Alto | Nivel elevado, precaución | Amarillo |
| Crítico | Nivel peligroso, acción inmediata | Rojo |

## Licencia

MIT License
