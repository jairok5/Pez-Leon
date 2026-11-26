CREATE OR REPLACE VIEW v_publicaciones_mas_citadas AS
SELECT
  RANK() OVER (ORDER BY d.citas DESC) AS posicion,
  d.publicacion_id,
  d.titulo,
  d.anio,
  d.fuente,
  d.primer_autor,
  d.pais_primer_autor,
  d.citas,
  ROUND(d.citas / GREATEST(YEAR(c.fecha_carga) - d.anio + 1, 1), 1) AS citas_por_anio,
  d.url_doi
FROM v_publicacion_detalle d
JOIN publicacion p ON p.publicacion_id = d.publicacion_id
JOIN carga c       ON c.carga_id = p.carga_id
ORDER BY d.citas DESC;