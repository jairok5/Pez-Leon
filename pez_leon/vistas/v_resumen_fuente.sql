CREATE OR REPLACE VIEW v_resumen_fuente AS
SELECT
  f.fuente_id,
  f.titulo AS fuente,
  f.titulo_abreviado,
  (SELECT GROUP_CONCAT(fi.valor ORDER BY fi.valor SEPARATOR ', ')
     FROM fuente_identificador fi
    WHERE fi.fuente_id = f.fuente_id AND fi.tipo = 'ISSN') AS issn,
  COUNT(*)               AS publicaciones,
  SUM(p.citas)           AS citas_totales,
  ROUND(AVG(p.citas), 1) AS citas_promedio,
  MIN(p.anio)            AS primer_anio,
  MAX(p.anio)            AS ultimo_anio
FROM publicacion p
JOIN fuente f ON f.fuente_id = p.fuente_id
GROUP BY f.fuente_id, f.titulo, f.titulo_abreviado
ORDER BY publicaciones DESC, citas_totales DESC;