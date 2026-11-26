CREATE TABLE tipo_acceso_abierto (
  tipo_acceso_id  TINYINT UNSIGNED NOT NULL AUTO_INCREMENT,
  nombre          VARCHAR(50) NOT NULL COMMENT 'Gold Open Access, Green Open Access, ...',
  nombre_corto    VARCHAR(20) NOT NULL COMMENT 'Gold, Green, Bronze, Hybrid Gold',
  PRIMARY KEY (tipo_acceso_id),
  UNIQUE KEY uq_tipo_acceso_nombre (nombre)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Modalidades de acceso abierto reportadas por Scopus';