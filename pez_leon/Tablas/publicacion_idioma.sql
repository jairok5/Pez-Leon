CREATE TABLE publicacion_idioma (
  publicacion_id  INT UNSIGNED     NOT NULL,
  idioma_id       TINYINT UNSIGNED NOT NULL,
  PRIMARY KEY (publicacion_id, idioma_id),
  KEY idx_pi_idioma (idioma_id),
  CONSTRAINT fk_pi_publicacion FOREIGN KEY (publicacion_id) REFERENCES publicacion (publicacion_id) ON DELETE CASCADE,
  CONSTRAINT fk_pi_idioma      FOREIGN KEY (idioma_id)      REFERENCES idioma (idioma_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;