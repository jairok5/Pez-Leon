CREATE OR REPLACE VIEW v_resumen_colaboracion AS
SELECT
  d.quinquenio,
  MIN(d.anio) - MOD(MIN(d.anio), 5)                     AS anio_inicio,
  SUM(d.tipo_colaboracion = 'Nacional')                 AS nacional,
  SUM(d.tipo_colaboracion = 'Internacional')            AS internacional,
  SUM(d.tipo_colaboracion = 'Sin afiliación registrada') AS sin_afiliacion,
  COUNT(*)                                              AS total,
  ROUND(100 * AVG(d.tipo_colaboracion = 'Internacional'), 1) AS pct_internacional
FROM v_publicacion_detalle d
GROUP BY d.quinquenio
ORDER BY anio_inicio;