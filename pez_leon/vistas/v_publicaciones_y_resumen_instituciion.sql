CREATE OR REPLACE VIEW v_publicaciones_mexico AS
SELECT d.*
FROM v_publicacion_detalle d
WHERE EXISTS (
  SELECT 1
  FROM publicacion_afiliacion pf
  JOIN afiliacion a  ON a.afiliacion_id = pf.afiliacion_id
  JOIN institucion i ON i.institucion_id = a.institucion_id
  JOIN pais z        ON z.pais_id = i.pais_id
  WHERE pf.publicacion_id = d.publicacion_id AND z.iso3 = 'MEX');

CREATE OR REPLACE VIEW v_resumen_institucion_mexico AS
SELECT r.institucion_id, r.institucion, r.publicaciones, r.citas_totales, r.primer_anio, r.ultimo_anio
FROM v_resumen_institucion r
WHERE r.iso3 = 'MEX'
ORDER BY r.publicaciones DESC, r.citas_totales DESC;