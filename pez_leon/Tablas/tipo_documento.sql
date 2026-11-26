CREATE TABLE tipo_documento (
  tipo_documento_id  TINYINT UNSIGNED NOT NULL AUTO_INCREMENT,
  nombre             VARCHAR(50) NOT NULL COMMENT 'Valor original de Scopus (Article, Review, ...)',
  nombre_es          VARCHAR(50) NOT NULL COMMENT 'Etiqueta en español para el reporte',
  PRIMARY KEY (tipo_documento_id),
  UNIQUE KEY uq_tipo_documento_nombre (nombre)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Tipos de documento de Scopus';