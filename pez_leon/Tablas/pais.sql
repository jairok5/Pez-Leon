CREATE TABLE pais (
  pais_id    SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
  nombre     VARCHAR(100) NOT NULL COMMENT 'Nombre tal como lo reporta Scopus (inglés)',
  nombre_es  VARCHAR(100) NOT NULL,
  iso3       CHAR(3)      NULL     COMMENT 'Código ISO 3166-1 alfa-3 (para mapas)',
  region_id  TINYINT UNSIGNED NOT NULL,
  PRIMARY KEY (pais_id),
  UNIQUE KEY uq_pais_nombre (nombre),
  UNIQUE KEY uq_pais_iso3 (iso3),
  KEY idx_pais_region (region_id),
  CONSTRAINT fk_pais_region FOREIGN KEY (region_id) REFERENCES region (region_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Países o territorios de las afiliaciones';