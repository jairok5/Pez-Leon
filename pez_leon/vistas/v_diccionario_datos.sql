CREATE OR REPLACE VIEW v_diccionario_datos AS
SELECT
  c.TABLE_NAME       AS tabla,
  t.TABLE_COMMENT    AS descripcion_tabla,
  c.ORDINAL_POSITION AS posicion,
  c.COLUMN_NAME      AS columna,
  c.COLUMN_TYPE      AS tipo,
  c.IS_NULLABLE      AS acepta_nulos,
  c.COLUMN_KEY       AS llave,
  c.COLUMN_COMMENT   AS descripcion
FROM information_schema.COLUMNS c
JOIN information_schema.TABLES t
  ON t.TABLE_SCHEMA = c.TABLE_SCHEMA AND t.TABLE_NAME = c.TABLE_NAME
WHERE c.TABLE_SCHEMA = 'pez_leon_bibliometria' AND t.TABLE_TYPE = 'BASE TABLE'
ORDER BY c.TABLE_NAME, c.ORDINAL_POSITION;