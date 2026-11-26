CREATE OR REPLACE VIEW v_resumen_quinquenio AS
SELECT
  d.quinquenio,
  MIN(d.anio) - MOD(MIN(d.anio), 5)                          AS anio_inicio,
  COUNT(*)                                                   AS publicaciones,
  SUM(d.citas)                                               AS citas_totales,
  ROUND(AVG(d.citas), 1)                                     AS citas_promedio,
  ROUND(100 * AVG(d.acceso_abierto), 1)                      AS pct_acceso_abierto,
  ROUND(100 * AVG(d.tipo_colaboracion = 'Internacional'), 1) AS pct_colaboracion_internacional
FROM v_publicacion_detalle d
GROUP BY d.quinquenio
ORDER BY anio_inicio;