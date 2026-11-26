CREATE OR REPLACE VIEW v_publicacion_detalle AS
SELECT
  b.*,
  CASE WHEN b.num_paises = 0 THEN 'Sin afiliación registrada'
       WHEN b.num_paises = 1 THEN 'Nacional'
       ELSE 'Internacional' END AS tipo_colaboracion
FROM (
  SELECT
    p.publicacion_id,
    p.eid,
    p.titulo,
    p.anio,
    CONCAT(p.anio - MOD(p.anio, 5), '-', p.anio - MOD(p.anio, 5) + 4) AS quinquenio,
    p.anio - MOD(p.anio, 10) AS decada,
    td.nombre_es AS tipo_documento,
    f.titulo     AS fuente,
    e.nombre     AS editorial,
    p.citas,
    CASE WHEN p.citas = 0   THEN '0'
         WHEN p.citas <= 10  THEN '1-10'
         WHEN p.citas <= 50  THEN '11-50'
         WHEN p.citas <= 100 THEN '51-100'
         ELSE 'Más de 100' END AS rango_citas,
    p.acceso_abierto,
    (SELECT GROUP_CONCAT(i.nombre_es ORDER BY i.nombre_es SEPARATOR ', ')
       FROM publicacion_idioma pi2 JOIN idioma i ON i.idioma_id = pi2.idioma_id
      WHERE pi2.publicacion_id = p.publicacion_id) AS idiomas,
    (SELECT COUNT(*) FROM publicacion_autor pa
      WHERE pa.publicacion_id = p.publicacion_id) AS num_autores,
    (SELECT au.nombre_completo FROM publicacion_autor pa JOIN autor au ON au.autor_id = pa.autor_id
      WHERE pa.publicacion_id = p.publicacion_id AND pa.orden = 1) AS primer_autor,
    (SELECT z.nombre_es
       FROM publicacion_autor pa
       JOIN publicacion_autor_afiliacion paa
         ON paa.publicacion_id = pa.publicacion_id AND paa.autor_id = pa.autor_id AND paa.orden = 1
       JOIN afiliacion a  ON a.afiliacion_id = paa.afiliacion_id
       JOIN institucion i ON i.institucion_id = a.institucion_id
       JOIN pais z        ON z.pais_id = i.pais_id
      WHERE pa.publicacion_id = p.publicacion_id AND pa.orden = 1) AS pais_primer_autor,
    (SELECT GROUP_CONCAT(DISTINCT z.nombre_es ORDER BY z.nombre_es SEPARATOR ', ')
       FROM publicacion_afiliacion pf
       JOIN afiliacion a  ON a.afiliacion_id = pf.afiliacion_id
       JOIN institucion i ON i.institucion_id = a.institucion_id
       JOIN pais z        ON z.pais_id = i.pais_id
      WHERE pf.publicacion_id = p.publicacion_id) AS paises,
    (SELECT COUNT(DISTINCT i.pais_id)
       FROM publicacion_afiliacion pf
       JOIN afiliacion a  ON a.afiliacion_id = pf.afiliacion_id
       JOIN institucion i ON i.institucion_id = a.institucion_id
      WHERE pf.publicacion_id = p.publicacion_id) AS num_paises,
    (SELECT GROUP_CONCAT(t.nombre ORDER BY t.nombre SEPARATOR ', ')
       FROM v_publicacion_tema_vigente tv JOIN tema t ON t.tema_id = tv.tema_id
      WHERE tv.publicacion_id = p.publicacion_id) AS temas,
    p.doi,
    CONCAT('https://doi.org/', p.doi) AS url_doi,
    p.enlace_scopus
  FROM publicacion p
  JOIN tipo_documento td ON td.tipo_documento_id = p.tipo_documento_id
  JOIN fuente f          ON f.fuente_id = p.fuente_id
  LEFT JOIN editorial e  ON e.editorial_id = p.editorial_id
) AS b;