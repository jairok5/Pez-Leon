CREATE OR REPLACE VIEW v_publicacion_tema_vigente AS
SELECT pt.publicacion_id, pt.tema_id, pt.metodo
FROM publicacion_tema pt
WHERE FIELD(pt.metodo, 'manual', 'ia', 'reglas') = (
  SELECT MIN(FIELD(x.metodo, 'manual', 'ia', 'reglas'))
  FROM publicacion_tema x
  WHERE x.publicacion_id = pt.publicacion_id);