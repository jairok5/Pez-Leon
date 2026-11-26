CREATE OR REPLACE VIEW v_resumen_region AS
SELECT
  r.nombre AS region,
  (SELECT COUNT(DISTINCT x.pais_id)
     FROM v_publicacion_pais x JOIN pais z2 ON z2.pais_id = x.pais_id
    WHERE z2.region_id = r.region_id) AS paises,
  COUNT(*)               AS publicaciones,
  ROUND(100 * COUNT(*) / (SELECT COUNT(*) FROM publicacion), 1) AS pct_publicaciones,
  SUM(p.citas)           AS citas_totales,
  ROUND(AVG(p.citas), 1) AS citas_promedio
FROM (SELECT DISTINCT x.publicacion_id, z.region_id
        FROM v_publicacion_pais x JOIN pais z ON z.pais_id = x.pais_id) pr
JOIN publicacion p ON p.publicacion_id = pr.publicacion_id
JOIN region r      ON r.region_id = pr.region_id
GROUP BY r.region_id, r.nombre
ORDER BY publicaciones DESC;