CREATE OR REPLACE VIEW v_resumen_palabra_clave AS
SELECT
  k.palabra_clave_id,
  k.termino,
  k.es_generica,
  (SELECT COUNT(*) FROM palabra_clave v WHERE v.canonica_id = k.palabra_clave_id) AS variantes_unidas,
  COUNT(*)               AS publicaciones,
  SUM(d.es_autor)        AS como_palabra_autor,
  SUM(d.es_indice)       AS como_palabra_indice,
  SUM(p.citas)           AS citas_totales,
  ROUND(AVG(p.citas), 1) AS citas_promedio,
  MIN(p.anio)            AS primer_anio,
  MAX(p.anio)            AS ultimo_anio
FROM (
  SELECT pk.publicacion_id,
         COALESCE(kk.canonica_id, kk.palabra_clave_id) AS palabra_clave_id,
         MAX(pk.origen = 'autor')  AS es_autor,
         MAX(pk.origen = 'indice') AS es_indice
  FROM publicacion_palabra_clave pk
  JOIN palabra_clave kk ON kk.palabra_clave_id = pk.palabra_clave_id
  GROUP BY pk.publicacion_id, COALESCE(kk.canonica_id, kk.palabra_clave_id)
) d
JOIN palabra_clave k ON k.palabra_clave_id = d.palabra_clave_id
JOIN publicacion p   ON p.publicacion_id = d.publicacion_id
GROUP BY k.palabra_clave_id, k.termino, k.es_generica
ORDER BY publicaciones DESC;