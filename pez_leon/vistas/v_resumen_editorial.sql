CREATE OR REPLACE VIEW v_resumen_editorial AS
SELECT
  COALESCE(e.nombre, '(Sin editorial registrada)') AS editorial,
  COUNT(*)     AS publicaciones,
  SUM(p.citas) AS citas_totales
FROM publicacion p
LEFT JOIN editorial e ON e.editorial_id = p.editorial_id
GROUP BY e.editorial_id, e.nombre
ORDER BY publicaciones DESC;
