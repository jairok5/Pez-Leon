CREATE OR REPLACE VIEW v_publicacion_pais AS
SELECT DISTINCT pf.publicacion_id, i.pais_id
FROM publicacion_afiliacion pf
JOIN afiliacion a  ON a.afiliacion_id = pf.afiliacion_id
JOIN institucion i ON i.institucion_id = a.institucion_id
WHERE i.pais_id IS NOT NULL;