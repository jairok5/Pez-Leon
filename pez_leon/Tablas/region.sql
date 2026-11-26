CREATE TABLE region (
  region_id  TINYINT UNSIGNED NOT NULL AUTO_INCREMENT,
  nombre     VARCHAR(50) NOT NULL,
  PRIMARY KEY (region_id),
  UNIQUE KEY uq_region_nombre (nombre)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Regiones geográficas (basadas en la clasificación M49 de la ONU)';