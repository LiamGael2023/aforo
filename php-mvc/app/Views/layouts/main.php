<?php
// Detectar base path
$basePath = rtrim(dirname($_SERVER['SCRIPT_NAME']), '/');
if ($basePath === '' || $basePath === '.') {
    $basePath = '';
}
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sistema de Aforo Digital - Ríos y Canales</title>
    <link rel="stylesheet" href="<?php echo $basePath; ?>/css/styles.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <?php echo $content; ?>
    <script src="<?php echo $basePath; ?>/js/dashboard.js"></script>
</body>
</html>
