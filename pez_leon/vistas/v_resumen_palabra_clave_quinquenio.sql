CREATE OR REPLACE VIEW v_palabra_clave_quinquenio AS
SELECT
  k.termino,
  p.anio - MOD(p.anio, 5) AS anio_inicio,
  CONCAT(p.anio - MOD(p.anio, 5), '-', p.anio - MOD(p.anio, 5) + 4) AS quinquenio,
  COUNT(DISTINCT p.publicacion_id) AS publicaciones
FROM publicacion_palabra_clave pk
JOIN palabra_clave kk ON kk.palabra_clave_id = pk.palabra_clave_id
JOIN palabra_clave k  ON k.palabra_clave_id = COALESCE(kk.canonica_id, kk.palabra_clave_id)
JOIN publicacion p    ON p.publicacion_id = pk.publicacion_id
WHERE pk.origen = 'autor' AND k.es_generica = 0
GROUP BY k.palabra_clave_id, k.termino, anio_inicio, quinquenio;
