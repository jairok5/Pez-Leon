CREATE TABLE tema (
  tema_id      TINYINT UNSIGNED NOT NULL AUTO_INCREMENT,
  nombre       VARCHAR(80)  NOT NULL,
  descripcion  VARCHAR(255) NULL,
  PRIMARY KEY (tema_id),
  UNIQUE KEY uq_tema_nombre (nombre)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Líneas temáticas de investigación sobre pez león';