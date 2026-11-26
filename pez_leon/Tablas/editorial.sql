CREATE TABLE editorial (
  editorial_id  SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
  nombre        VARCHAR(255) NOT NULL,
  PRIMARY KEY (editorial_id),
  UNIQUE KEY uq_editorial_nombre (nombre)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Editoriales tal como aparecen en Scopus';
