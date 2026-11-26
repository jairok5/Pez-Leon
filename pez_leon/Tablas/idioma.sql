CREATE TABLE idioma (
  idioma_id  TINYINT UNSIGNED NOT NULL AUTO_INCREMENT,
  nombre     VARCHAR(50) NOT NULL COMMENT 'Valor original de Scopus (English, Spanish, ...)',
  nombre_es  VARCHAR(50) NOT NULL,
  PRIMARY KEY (idioma_id),
  UNIQUE KEY uq_idioma_nombre (nombre)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Idioma original del documento';