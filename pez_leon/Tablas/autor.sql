CREATE TABLE autor (
  autor_id         INT UNSIGNED    NOT NULL AUTO_INCREMENT,
  scopus_id        BIGINT UNSIGNED NOT NULL COMMENT 'Author ID de Scopus (identificador estable)',
  nombre_completo  VARCHAR(255)    NOT NULL,
  nombre_corto     VARCHAR(150)    NOT NULL,
  PRIMARY KEY (autor_id),
  UNIQUE KEY uq_autor_scopus (scopus_id),
  KEY idx_autor_nombre (nombre_completo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Autores identificados por su Author ID de Scopus';