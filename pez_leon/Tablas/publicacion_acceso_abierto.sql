CREATE TABLE publicacion_acceso_abierto (
  publicacion_id  INT UNSIGNED     NOT NULL,
  tipo_acceso_id  TINYINT UNSIGNED NOT NULL,
  PRIMARY KEY (publicacion_id, tipo_acceso_id),
  KEY idx_paab_tipo (tipo_acceso_id),
  CONSTRAINT fk_paab_publicacion FOREIGN KEY (publicacion_id) REFERENCES publicacion (publicacion_id) ON DELETE CASCADE,
  CONSTRAINT fk_paab_tipo        FOREIGN KEY (tipo_acceso_id) REFERENCES tipo_acceso_abierto (tipo_acceso_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
