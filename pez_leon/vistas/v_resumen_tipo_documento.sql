CREATE OR REPLACE VIEW v_resumen_tipo_documento AS
SELECT
  td.nombre_es AS tipo_documento,
  td.nombre    AS tipo_documento_scopus,
  COUNT(*)     AS publicaciones,
  ROUND(100 * COUNT(*) / (SELECT COUNT(*) FROM publicacion), 1) AS pct_publicaciones,
  SUM(p.citas)           AS citas_totales,
  ROUND(AVG(p.citas), 1) AS citas_promedio
FROM publicacion p
JOIN tipo_documento td ON td.tipo_documento_id = p.tipo_documento_id
GROUP BY td.tipo_documento_id, td.nombre_es, td.nombre
ORDER BY publicaciones DESC;