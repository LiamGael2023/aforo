<?php
namespace App\Core;

/**
 * Cálculos hidráulicos para el sistema de aforo
 */
class HydraulicCalculator
{
    /**
     * Calcula el caudal usando la ecuación de Manning para canal rectangular
     * Q = (1/n) * A * R^(2/3) * S^(1/2)
     */
    public static function calculateFlowManning(
        float $waterLevel,
        float $channelWidth,
        float $slope,
        float $manningN,
        float $baseLevel = 0
    ): array {
        $h = $waterLevel - $baseLevel;

        if ($h <= 0) {
            return ['flow_rate' => 0, 'velocity' => 0, 'area' => 0];
        }

        // Área de la sección transversal (rectangular)
        $area = $channelWidth * $h;

        // Perímetro mojado
        $wettedPerimeter = $channelWidth + 2 * $h;

        // Radio hidráulico
        $hydraulicRadius = $area / $wettedPerimeter;

        // Velocidad usando Manning
        $velocity = (1 / $manningN) * pow($hydraulicRadius, 2/3) * pow($slope, 0.5);

        // Caudal
        $flowRate = $area * $velocity;

        return [
            'flow_rate' => round($flowRate, 4),
            'velocity' => round($velocity, 4),
            'area' => round($area, 4)
        ];
    }

    /**
     * Calcula el caudal usando una curva de aforo
     * Q = a * (h - h0)^b
     */
    public static function calculateFlowRatingCurve(
        float $waterLevel,
        float $coeffA,
        float $coeffB,
        float $baseLevel = 0
    ): float {
        $h = $waterLevel - $baseLevel;

        if ($h <= 0) {
            return 0;
        }

        return round($coeffA * pow($h, $coeffB), 4);
    }

    /**
     * Calcula todos los parámetros hidráulicos para una medición
     */
    public static function calculateHydraulicParameters(array $station, float $waterLevel): array
    {
        if (!empty($station['channel_width']) && $station['channel_width'] > 0) {
            // Usar ecuación de Manning
            return self::calculateFlowManning(
                $waterLevel,
                (float) $station['channel_width'],
                (float) $station['channel_slope'],
                (float) $station['manning_coefficient'],
                (float) $station['curve_base_level']
            );
        } else {
            // Usar curva de aforo
            $flowRate = self::calculateFlowRatingCurve(
                $waterLevel,
                (float) $station['curve_coefficient_a'],
                (float) $station['curve_coefficient_b'],
                (float) $station['curve_base_level']
            );

            // Estimar área y velocidad
            $estimatedWidth = 5.0;
            $h = $waterLevel - (float) $station['curve_base_level'];
            $area = $h > 0 ? $estimatedWidth * $h : 0;
            $velocity = $area > 0 ? $flowRate / $area : 0;

            return [
                'flow_rate' => $flowRate,
                'velocity' => round($velocity, 4),
                'area' => round($area, 4)
            ];
        }
    }

    /**
     * Determina el nivel de alerta basado en el nivel de agua
     */
    public static function determineAlertLevel(array $station, float $waterLevel): string
    {
        if ($waterLevel >= (float) $station['level_critical']) {
            return 'critical';
        } elseif ($waterLevel >= (float) $station['level_high']) {
            return 'high';
        } elseif ($waterLevel < (float) $station['level_low']) {
            return 'low';
        } elseif ($waterLevel >= (float) $station['level_normal_min'] &&
                  $waterLevel <= (float) $station['level_normal_max']) {
            return 'normal';
        } elseif ($waterLevel < (float) $station['level_normal_min']) {
            return 'low';
        } else {
            return 'high';
        }
    }

    /**
     * Genera mensaje de alerta
     */
    public static function getAlertMessage(string $alertLevel, float $waterLevel, string $stationName): string
    {
        $messages = [
            'low' => "Nivel bajo detectado en {$stationName}. Nivel actual: " . number_format($waterLevel, 2) . "m. Posible sequía o reducción de flujo.",
            'normal' => "Nivel normal en {$stationName}. Nivel actual: " . number_format($waterLevel, 2) . "m.",
            'high' => "Nivel alto en {$stationName}. Nivel actual: " . number_format($waterLevel, 2) . "m. Se recomienda monitoreo continuo.",
            'critical' => "ALERTA CRÍTICA en {$stationName}. Nivel actual: " . number_format($waterLevel, 2) . "m. Riesgo de desbordamiento. Acción inmediata requerida."
        ];

        return $messages[$alertLevel] ?? "Alerta en {$stationName}: " . number_format($waterLevel, 2) . "m";
    }

    /**
     * Calcula el número de Froude
     */
    public static function getFroudeNumber(float $velocity, float $depth): float
    {
        $g = 9.81;
        if ($depth <= 0) {
            return 0;
        }
        return round($velocity / sqrt($g * $depth), 4);
    }

    /**
     * Clasifica el régimen de flujo
     */
    public static function classifyFlowRegime(float $froudeNumber): string
    {
        if ($froudeNumber < 1) {
            return 'subcrítico';
        } elseif ($froudeNumber == 1) {
            return 'crítico';
        } else {
            return 'supercrítico';
        }
    }
}
