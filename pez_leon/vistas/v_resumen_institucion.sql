CREATE OR REPLACE VIEW v_resumen_institucion AS
SELECT
  i.institucion_id,
  i.nombre    AS institucion,
  z.nombre_es AS pais,
  z.iso3,
  COUNT(*)     AS publicaciones,
  SUM(p.citas) AS citas_totales,
  MIN(p.anio)  AS primer_anio,
  MAX(p.anio)  AS ultimo_anio
FROM (SELECT DISTINCT pf.publicacion_id, a.institucion_id
        FROM publicacion_afiliacion pf
        JOIN afiliacion a ON a.afiliacion_id = pf.afiliacion_id) ip
JOIN publicacion p ON p.publicacion_id = ip.publicacion_id
JOIN institucion i ON i.institucion_id = ip.institucion_id
LEFT JOIN pais z   ON z.pais_id = i.pais_id
GROUP BY i.institucion_id, i.nombre, z.nombre_es, z.iso3
ORDER BY publicaciones DESC, citas_totales DESC;
