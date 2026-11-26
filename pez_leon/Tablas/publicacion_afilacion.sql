CREATE TABLE publicacion_afiliacion (
  publicacion_id  INT UNSIGNED NOT NULL,
  afiliacion_id   INT UNSIGNED NOT NULL,
  PRIMARY KEY (publicacion_id, afiliacion_id),
  KEY idx_pf_afiliacion (afiliacion_id),
  CONSTRAINT fk_pf_publicacion FOREIGN KEY (publicacion_id) REFERENCES publicacion (publicacion_id) ON DELETE CASCADE,
  CONSTRAINT fk_pf_afiliacion  FOREIGN KEY (afiliacion_id)  REFERENCES afiliacion (afiliacion_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Todas las afiliaciones listadas en el registro (columna Affiliations de Scopus)';