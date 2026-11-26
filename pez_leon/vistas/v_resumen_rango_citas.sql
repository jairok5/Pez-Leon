CREATE OR REPLACE VIEW v_resumen_rango_citas AS
SELECT
  CASE WHEN citas = 0   THEN '0'
       WHEN citas <= 10  THEN '1-10'
       WHEN citas <= 50  THEN '11-50'
       WHEN citas <= 100 THEN '51-100'
       ELSE 'Más de 100' END AS rango_citas,
  MIN(citas) AS citas_minimas,
  MAX(citas) AS citas_maximas,
  COUNT(*)   AS publicaciones,
  ROUND(100 * COUNT(*) / (SELECT COUNT(*) FROM publicacion), 1) AS pct_publicaciones
FROM publicacion
GROUP BY rango_citas
ORDER BY citas_minimas;