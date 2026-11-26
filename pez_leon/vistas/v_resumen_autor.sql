CREATE OR REPLACE VIEW v_resumen_autor AS
SELECT
  au.autor_id,
  au.scopus_id,
  au.nombre_completo         AS autor,
  COUNT(*)                   AS publicaciones,
  SUM(r.orden = 1)           AS como_primer_autor,
  SUM(r.citas)               AS citas_totales,
  ROUND(AVG(r.citas), 1)     AS citas_promedio,
  SUM(r.citas >= r.posicion) AS indice_h_corpus,
  MIN(r.anio)                AS primer_anio,
  MAX(r.anio)                AS ultimo_anio
FROM (
  SELECT pa.autor_id, pa.orden, p.citas, p.anio,
         ROW_NUMBER() OVER (PARTITION BY pa.autor_id ORDER BY p.citas DESC) AS posicion
  FROM publicacion_autor pa
  JOIN publicacion p ON p.publicacion_id = pa.publicacion_id
) r
JOIN autor au ON au.autor_id = r.autor_id
GROUP BY au.autor_id, au.scopus_id, au.nombre_completo
ORDER BY publicaciones DESC, citas_totales DESC;