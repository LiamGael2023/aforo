// Dashboard JavaScript para Sistema de Aforo Digital

let mainChart = null;
let selectedStationId = null;

// Inicialización
document.addEventListener('DOMContentLoaded', () => {
    loadDashboard();

    // Actualizar cada 30 segundos
    setInterval(loadDashboard, 30000);
});

// Cargar todos los datos del dashboard
async function loadDashboard() {
    try {
        await Promise.all([
            loadSummary(),
            loadStations(),
            loadAlerts(),
            loadLatestMeasurements()
        ]);
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

// Cargar resumen
async function loadSummary() {
    try {
        const response = await fetch('/api/dashboard/summary');
        const data = await response.json();

        document.getElementById('totalStations').textContent = data.active_stations;
        document.getElementById('todayMeasurements').textContent = data.total_measurements_today;
        document.getElementById('activeAlerts').textContent = data.active_alerts;
        document.getElementById('criticalAlerts').textContent = data.critical_alerts;
    } catch (error) {
        console.error('Error loading summary:', error);
    }
}

// Cargar estaciones
async function loadStations() {
    try {
        const response = await fetch('/api/stations/with-latest');
        const stations = await response.json();

        const container = document.getElementById('stationsList');
        const select = document.getElementById('chartStationSelect');
        const measurementSelect = document.getElementById('measurementStation');

        if (stations.length === 0) {
            container.innerHTML = '<p class="empty-state">No hay estaciones registradas</p>';
            return;
        }

        // Actualizar lista de estaciones
        container.innerHTML = stations.map(station => `
            <div class="station-item ${selectedStationId === station.id ? 'selected' : ''}"
                 onclick="selectStation(${station.id})">
                <div class="station-name">${station.name}</div>
                <div class="station-code">${station.code} - ${station.water_body_name}</div>
                <div class="station-details">
                    <span class="station-level">
                        Nivel: ${station.latest_level ? station.latest_level.toFixed(2) + 'm' : 'N/A'}
                    </span>
                    <span class="station-flow">
                        Caudal: ${station.latest_flow ? station.latest_flow.toFixed(3) + ' m³/s' : 'N/A'}
                    </span>
                    <span class="alert-badge alert-${station.current_alert_level || 'normal'}">
                        ${station.current_alert_level || 'normal'}
                    </span>
                </div>
            </div>
        `).join('');

        // Actualizar selectores
        const options = stations.map(s =>
            `<option value="${s.id}">${s.name} (${s.code})</option>`
        ).join('');

        select.innerHTML = '<option value="">Seleccione estación</option>' + options;
        measurementSelect.innerHTML = '<option value="">Seleccione estación</option>' + options;

        // Si hay una estación seleccionada, mantener la selección
        if (selectedStationId) {
            select.value = selectedStationId;
        }

    } catch (error) {
        console.error('Error loading stations:', error);
        document.getElementById('stationsList').innerHTML =
            '<p class="empty-state">Error al cargar estaciones</p>';
    }
}

// Seleccionar estación
function selectStation(stationId) {
    selectedStationId = stationId;
    document.getElementById('chartStationSelect').value = stationId;

    // Actualizar clase selected
    document.querySelectorAll('.station-item').forEach(item => {
        item.classList.remove('selected');
    });
    event.currentTarget.classList.add('selected');

    loadChartData();
}

// Cargar datos del gráfico
async function loadChartData() {
    const stationId = document.getElementById('chartStationSelect').value;

    if (!stationId) {
        if (mainChart) {
            mainChart.destroy();
            mainChart = null;
        }
        return;
    }

    try {
        const response = await fetch(`/api/dashboard/charts/${stationId}?hours=24`);
        const data = await response.json();

        renderChart(data);
    } catch (error) {
        console.error('Error loading chart data:', error);
    }
}

// Renderizar gráfico
function renderChart(data) {
    const ctx = document.getElementById('mainChart').getContext('2d');

    if (mainChart) {
        mainChart.destroy();
    }

    mainChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.timestamps,
            datasets: [
                {
                    label: 'Nivel (m)',
                    data: data.levels,
                    borderColor: '#2563eb',
                    backgroundColor: 'rgba(37, 99, 235, 0.1)',
                    fill: true,
                    tension: 0.3,
                    yAxisID: 'y'
                },
                {
                    label: 'Caudal (m³/s)',
                    data: data.flows,
                    borderColor: '#22c55e',
                    backgroundColor: 'rgba(34, 197, 94, 0.1)',
                    fill: true,
                    tension: 0.3,
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                title: {
                    display: true,
                    text: `${data.station_name} (${data.station_code})`
                },
                legend: {
                    position: 'top'
                }
            },
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Tiempo'
                    },
                    ticks: {
                        maxRotation: 45,
                        minRotation: 45
                    }
                },
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Nivel (m)'
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Caudal (m³/s)'
                    },
                    grid: {
                        drawOnChartArea: false
                    }
                }
            }
        }
    });
}

// Cargar alertas
async function loadAlerts() {
    try {
        const response = await fetch('/api/alerts?active_only=true');
        const alerts = await response.json();

        const container = document.getElementById('alertsList');

        if (alerts.length === 0) {
            container.innerHTML = '<p class="empty-state">No hay alertas activas</p>';
            return;
        }

        container.innerHTML = alerts.map(alert => `
            <div class="alert-item ${alert.alert_level}">
                <div class="alert-message">${alert.message}</div>
                <div class="alert-time">
                    ${formatDateTime(alert.created_at)}
                    ${alert.is_acknowledged ? ' - Reconocida' : ''}
                </div>
            </div>
        `).join('');

    } catch (error) {
        console.error('Error loading alerts:', error);
        document.getElementById('alertsList').innerHTML =
            '<p class="empty-state">Error al cargar alertas</p>';
    }
}

// Cargar últimas mediciones
async function loadLatestMeasurements() {
    try {
        const response = await fetch('/api/measurements/latest?limit=10');
        const measurements = await response.json();

        const tbody = document.getElementById('measurementsTable');

        if (measurements.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="empty-state">No hay mediciones</td></tr>';
            return;
        }

        tbody.innerHTML = measurements.map(m => `
            <tr>
                <td>
                    <strong>${m.station_name}</strong><br>
                    <small>${m.station_code}</small>
                </td>
                <td>${m.water_level.toFixed(2)}</td>
                <td>${m.flow_rate ? m.flow_rate.toFixed(3) : 'N/A'}</td>
                <td>
                    <span class="alert-badge alert-${m.alert_level}">${m.alert_level}</span>
                </td>
                <td>${formatDateTime(m.timestamp)}</td>
            </tr>
        `).join('');

    } catch (error) {
        console.error('Error loading measurements:', error);
        document.getElementById('measurementsTable').innerHTML =
            '<tr><td colspan="5" class="empty-state">Error al cargar mediciones</td></tr>';
    }
}

// Crear estación
async function createStation(event) {
    event.preventDefault();

    const station = {
        name: document.getElementById('stationName').value,
        code: document.getElementById('stationCode').value,
        description: document.getElementById('stationDesc').value || null,
        water_body_name: document.getElementById('waterBodyName').value,
        channel_type: document.getElementById('channelType').value,
        latitude: parseFloat(document.getElementById('latitude').value),
        longitude: parseFloat(document.getElementById('longitude').value),
        channel_width: parseFloat(document.getElementById('channelWidth').value) || null,
        channel_slope: parseFloat(document.getElementById('channelSlope').value) || 0.001
    };

    try {
        const response = await fetch('/api/stations', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(station)
        });

        if (response.ok) {
            closeModal('stationModal');
            document.getElementById('stationForm').reset();
            loadDashboard();
            alert('Estación creada correctamente');
        } else {
            const error = await response.json();
            alert('Error: ' + (error.detail || 'No se pudo crear la estación'));
        }
    } catch (error) {
        console.error('Error creating station:', error);
        alert('Error al crear la estación');
    }
}

// Crear medición
async function createMeasurement(event) {
    event.preventDefault();

    const measurement = {
        station_id: parseInt(document.getElementById('measurementStation').value),
        water_level: parseFloat(document.getElementById('waterLevel').value),
        water_temperature: parseFloat(document.getElementById('waterTemp').value) || null,
        turbidity: parseFloat(document.getElementById('turbidity').value) || null,
        measurement_method: document.getElementById('measurementMethod').value,
        notes: document.getElementById('measurementNotes').value || null
    };

    try {
        const response = await fetch('/api/measurements', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(measurement)
        });

        if (response.ok) {
            closeModal('measurementModal');
            document.getElementById('measurementForm').reset();
            loadDashboard();
            alert('Medición registrada correctamente');
        } else {
            const error = await response.json();
            alert('Error: ' + (error.detail || 'No se pudo registrar la medición'));
        }
    } catch (error) {
        console.error('Error creating measurement:', error);
        alert('Error al registrar la medición');
    }
}

// Cargar datos de ejemplo
async function seedData() {
    if (!confirm('¿Desea cargar datos de ejemplo para demostración?')) {
        return;
    }

    try {
        const response = await fetch('/api/seed-data', {
            method: 'POST'
        });

        const result = await response.json();
        alert(result.message);
        loadDashboard();
    } catch (error) {
        console.error('Error seeding data:', error);
        alert('Error al cargar datos de ejemplo');
    }
}

// Modales
function openModal(modalId) {
    document.getElementById(modalId).classList.add('active');
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
}

// Cerrar modal al hacer clic fuera
window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.classList.remove('active');
    }
}

// Formatear fecha y hora
function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('es-ES', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}
