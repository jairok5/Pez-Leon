CREATE OR REPLACE VIEW v_resumen_anual AS
SELECT
  p.anio,
  COUNT(*)                              AS publicaciones,
  SUM(COUNT(*)) OVER (ORDER BY p.anio)  AS publicaciones_acumuladas,
  SUM(p.citas)                          AS citas_totales,
  ROUND(AVG(p.citas), 1)                AS citas_promedio,
  SUM(p.acceso_abierto)                 AS en_acceso_abierto,
  ROUND(100 * AVG(p.acceso_abierto), 1) AS pct_acceso_abierto
FROM publicacion p
GROUP BY p.anio
ORDER BY p.anio;
