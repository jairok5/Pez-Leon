CREATE TABLE fuente (
  fuente_id         SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
  titulo            VARCHAR(255) NOT NULL,
  titulo_abreviado  VARCHAR(150) NULL,
  coden             VARCHAR(10)  NULL,
  PRIMARY KEY (fuente_id),
  UNIQUE KEY uq_fuente_titulo (titulo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Revista, libro o actas donde se publicó el documento';