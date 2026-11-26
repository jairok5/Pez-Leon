CREATE OR REPLACE VIEW v_resumen_acceso_abierto AS
SELECT 'General' AS categoria, 'Con acceso abierto' AS modalidad,
       SUM(acceso_abierto) AS publicaciones, ROUND(100 * AVG(acceso_abierto), 1) AS pct_publicaciones
FROM publicacion
UNION ALL
SELECT 'General', 'Sin acceso abierto',
       SUM(1 - acceso_abierto), ROUND(100 * AVG(1 - acceso_abierto), 1)
FROM publicacion
UNION ALL
SELECT 'Por modalidad', ta.nombre_corto,
       COUNT(*), ROUND(100 * COUNT(*) / (SELECT COUNT(*) FROM publicacion), 1)
FROM publicacion_acceso_abierto paa
JOIN tipo_acceso_abierto ta ON ta.tipo_acceso_id = paa.tipo_acceso_id
GROUP BY ta.tipo_acceso_id, ta.nombre_corto;