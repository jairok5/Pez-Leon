CREATE OR REPLACE VIEW v_tema_quinquenio AS
SELECT
  t.nombre AS tema,
  p.anio - MOD(p.anio, 5) AS anio_inicio,
  CONCAT(p.anio - MOD(p.anio, 5), '-', p.anio - MOD(p.anio, 5) + 4) AS quinquenio,
  COUNT(*) AS publicaciones
FROM v_publicacion_tema_vigente tv
JOIN tema t        ON t.tema_id = tv.tema_id
JOIN publicacion p ON p.publicacion_id = tv.publicacion_id
GROUP BY t.tema_id, t.nombre, anio_inicio, quinquenio;