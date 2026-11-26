CREATE OR REPLACE VIEW v_resumen_tema AS
SELECT
  t.nombre      AS tema,
  t.descripcion,
  COUNT(*)      AS publicaciones,
  ROUND(100 * COUNT(*) / (SELECT COUNT(*) FROM publicacion), 1) AS pct_publicaciones,
  SUM(p.citas)           AS citas_totales,
  ROUND(AVG(p.citas), 1) AS citas_promedio,
  MIN(p.anio)            AS primer_anio,
  GROUP_CONCAT(DISTINCT tv.metodo ORDER BY tv.metodo) AS metodos
FROM v_publicacion_tema_vigente tv
JOIN tema t        ON t.tema_id = tv.tema_id
JOIN publicacion p ON p.publicacion_id = tv.publicacion_id
GROUP BY t.tema_id, t.nombre, t.descripcion
UNION ALL
SELECT 'Sin clasificar', 'Publicaciones sin tema asignado', COUNT(*),
       ROUND(100 * COUNT(*) / (SELECT COUNT(*) FROM publicacion), 1),
       SUM(p.citas), ROUND(AVG(p.citas), 1), MIN(p.anio), NULL
FROM publicacion p
WHERE NOT EXISTS (SELECT 1 FROM publicacion_tema pt WHERE pt.publicacion_id = p.publicacion_id)
ORDER BY publicaciones DESC;
