CREATE OR REPLACE VIEW v_resumen_idioma AS
SELECT
  i.nombre_es AS idioma,
  COUNT(*)    AS publicaciones,
  ROUND(100 * COUNT(*) / (SELECT COUNT(*) FROM publicacion), 1) AS pct_publicaciones
FROM publicacion_idioma pi2
JOIN idioma i ON i.idioma_id = pi2.idioma_id
GROUP BY i.idioma_id, i.nombre_es
ORDER BY publicaciones DESC;