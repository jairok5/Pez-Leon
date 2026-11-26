CREATE OR REPLACE VIEW v_publicacion_pais_primer_autor AS
SELECT pa.publicacion_id, i.pais_id
FROM publicacion_autor pa
JOIN publicacion_autor_afiliacion paa
  ON paa.publicacion_id = pa.publicacion_id AND paa.autor_id = pa.autor_id AND paa.orden = 1
JOIN afiliacion a  ON a.afiliacion_id = paa.afiliacion_id
JOIN institucion i ON i.institucion_id = a.institucion_id
WHERE pa.orden = 1 AND i.pais_id IS NOT NULL;