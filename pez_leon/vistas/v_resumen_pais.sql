CREATE OR REPLACE VIEW v_resumen_pais AS
SELECT
  z.pais_id,
  z.nombre_es AS pais,
  z.iso3,
  r.nombre    AS region,
  COUNT(*)    AS publicaciones,
  ROUND(100 * COUNT(*) / (SELECT COUNT(*) FROM publicacion), 1) AS pct_publicaciones,
  (SELECT COUNT(*) FROM v_publicacion_pais_primer_autor x WHERE x.pais_id = z.pais_id) AS como_pais_primer_autor,
  SUM(p.citas)           AS citas_totales,
  ROUND(AVG(p.citas), 1) AS citas_promedio,
  MIN(p.anio)            AS primer_anio
FROM v_publicacion_pais pp
JOIN publicacion p ON p.publicacion_id = pp.publicacion_id
JOIN pais z        ON z.pais_id = pp.pais_id
JOIN region r      ON r.region_id = z.region_id
GROUP BY z.pais_id, z.nombre_es, z.iso3, r.nombre
ORDER BY publicaciones DESC, citas_totales DESC;
