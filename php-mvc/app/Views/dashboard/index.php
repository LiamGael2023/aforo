<div class="app-container">
    <!-- Header -->
    <header class="header">
        <div class="header-content">
            <h1>Sistema de Aforo Digital</h1>
            <p>Monitoreo de Ríos y Canales - PHP MVC</p>
        </div>
        <div class="header-actions">
            <button class="btn btn-primary" onclick="openModal('stationModal')">
                + Nueva Estación
            </button>
            <button class="btn btn-secondary" onclick="openModal('measurementModal')">
                + Nueva Medición
            </button>
        </div>
    </header>

    <!-- Main Content -->
    <main class="main-content">
        <!-- Summary Cards -->
        <section class="summary-section">
            <div class="card summary-card">
                <div class="card-icon stations-icon">
                    <svg viewBox="0 0 24 24" fill="currentColor">
                        <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
                    </svg>
                </div>
                <div class="card-info">
                    <h3 id="totalStations">0</h3>
                    <p>Estaciones Activas</p>
                </div>
            </div>
            <div class="card summary-card">
                <div class="card-icon measurements-icon">
                    <svg viewBox="0 0 24 24" fill="currentColor">
                        <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17H7v-7h2v7zm4 0h-2V7h2v10zm4 0h-2v-4h2v4z"/>
                    </svg>
                </div>
                <div class="card-info">
                    <h3 id="todayMeasurements">0</h3>
                    <p>Mediciones Hoy</p>
                </div>
            </div>
            <div class="card summary-card">
                <div class="card-icon alerts-icon">
                    <svg viewBox="0 0 24 24" fill="currentColor">
                        <path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/>
                    </svg>
                </div>
                <div class="card-info">
                    <h3 id="activeAlerts">0</h3>
                    <p>Alertas Activas</p>
                </div>
            </div>
            <div class="card summary-card critical">
                <div class="card-icon critical-icon">
                    <svg viewBox="0 0 24 24" fill="currentColor">
                        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                    </svg>
                </div>
                <div class="card-info">
                    <h3 id="criticalAlerts">0</h3>
                    <p>Alertas Críticas</p>
                </div>
            </div>
        </section>

        <!-- Content Grid -->
        <div class="content-grid">
            <!-- Stations Panel -->
            <section class="card stations-panel">
                <div class="card-header">
                    <h2>Estaciones de Monitoreo</h2>
                    <button class="btn btn-sm" onclick="loadStations()">Actualizar</button>
                </div>
                <div class="stations-list" id="stationsList">
                    <p class="loading">Cargando estaciones...</p>
                </div>
            </section>

            <!-- Chart Panel -->
            <section class="card chart-panel">
                <div class="card-header">
                    <h2>Niveles y Caudales</h2>
                    <select id="chartStationSelect" onchange="loadChartData()">
                        <option value="">Seleccione estación</option>
                    </select>
                </div>
                <div class="chart-container">
                    <canvas id="mainChart"></canvas>
                </div>
            </section>

            <!-- Alerts Panel -->
            <section class="card alerts-panel">
                <div class="card-header">
                    <h2>Alertas Activas</h2>
                </div>
                <div class="alerts-list" id="alertsList">
                    <p class="loading">Cargando alertas...</p>
                </div>
            </section>

            <!-- Latest Measurements Panel -->
            <section class="card measurements-panel">
                <div class="card-header">
                    <h2>Últimas Mediciones</h2>
                </div>
                <div class="measurements-table-container">
                    <table class="measurements-table">
                        <thead>
                            <tr>
                                <th>Estación</th>
                                <th>Nivel (m)</th>
                                <th>Caudal (m³/s)</th>
                                <th>Estado</th>
                                <th>Hora</th>
                            </tr>
                        </thead>
                        <tbody id="measurementsTable">
                            <tr>
                                <td colspan="5" class="loading">Cargando mediciones...</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </section>
        </div>
    </main>

    <!-- Footer -->
    <footer class="footer">
        <p>Sistema de Aforo Digital de Ríos y Canales v1.0.0 - PHP MVC + MySQL</p>
    </footer>
</div>

<!-- Modal: Nueva Estación -->
<div id="stationModal" class="modal">
    <div class="modal-content">
        <div class="modal-header">
            <h2>Nueva Estación de Aforo</h2>
            <button class="close-btn" onclick="closeModal('stationModal')">&times;</button>
        </div>
        <form id="stationForm" onsubmit="createStation(event)">
            <div class="form-grid">
                <div class="form-group">
                    <label for="stationName">Nombre *</label>
                    <input type="text" id="stationName" required>
                </div>
                <div class="form-group">
                    <label for="stationCode">Código *</label>
                    <input type="text" id="stationCode" required>
                </div>
                <div class="form-group full-width">
                    <label for="stationDesc">Descripción</label>
                    <textarea id="stationDesc" rows="2"></textarea>
                </div>
                <div class="form-group">
                    <label for="waterBodyName">Cuerpo de Agua *</label>
                    <input type="text" id="waterBodyName" required>
                </div>
                <div class="form-group">
                    <label for="channelType">Tipo</label>
                    <select id="channelType">
                        <option value="river">Río</option>
                        <option value="canal">Canal</option>
                        <option value="stream">Arroyo</option>
                        <option value="irrigation">Riego</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="latitude">Latitud *</label>
                    <input type="number" id="latitude" step="0.000001" required>
                </div>
                <div class="form-group">
                    <label for="longitude">Longitud *</label>
                    <input type="number" id="longitude" step="0.000001" required>
                </div>
                <div class="form-group">
                    <label for="channelWidth">Ancho del Canal (m)</label>
                    <input type="number" id="channelWidth" step="0.1" value="10">
                </div>
                <div class="form-group">
                    <label for="channelSlope">Pendiente</label>
                    <input type="number" id="channelSlope" step="0.0001" value="0.001">
                </div>
            </div>
            <div class="form-actions">
                <button type="button" class="btn btn-secondary" onclick="closeModal('stationModal')">
                    Cancelar
                </button>
                <button type="submit" class="btn btn-primary">Crear Estación</button>
            </div>
        </form>
    </div>
</div>

<!-- Modal: Nueva Medición -->
<div id="measurementModal" class="modal">
    <div class="modal-content">
        <div class="modal-header">
            <h2>Nueva Medición</h2>
            <button class="close-btn" onclick="closeModal('measurementModal')">&times;</button>
        </div>
        <form id="measurementForm" onsubmit="createMeasurement(event)">
            <div class="form-grid">
                <div class="form-group full-width">
                    <label for="measurementStation">Estación *</label>
                    <select id="measurementStation" required>
                        <option value="">Seleccione estación</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="waterLevel">Nivel de Agua (m) *</label>
                    <input type="number" id="waterLevel" step="0.01" required>
                </div>
                <div class="form-group">
                    <label for="waterTemp">Temperatura (°C)</label>
                    <input type="number" id="waterTemp" step="0.1">
                </div>
                <div class="form-group">
                    <label for="turbidity">Turbidez (NTU)</label>
                    <input type="number" id="turbidity" step="0.1">
                </div>
                <div class="form-group">
                    <label for="measurementMethod">Método</label>
                    <select id="measurementMethod">
                        <option value="automatic">Automático</option>
                        <option value="manual">Manual</option>
                    </select>
                </div>
                <div class="form-group full-width">
                    <label for="measurementNotes">Notas</label>
                    <textarea id="measurementNotes" rows="2"></textarea>
                </div>
            </div>
            <div class="form-actions">
                <button type="button" class="btn btn-secondary" onclick="closeModal('measurementModal')">
                    Cancelar
                </button>
                <button type="submit" class="btn btn-primary">Registrar Medición</button>
            </div>
        </form>
    </div>
</div>

<!-- Seed Data Button -->
<button id="seedDataBtn" class="seed-data-btn" onclick="seedData()" title="Crear datos de ejemplo">
    Cargar Datos Demo
</button>
