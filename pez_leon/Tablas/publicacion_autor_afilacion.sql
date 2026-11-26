CREATE TABLE publicacion_autor_afiliacion (
  publicacion_id  INT UNSIGNED     NOT NULL,
  autor_id        INT UNSIGNED     NOT NULL,
  afiliacion_id   INT UNSIGNED     NOT NULL,
  orden           TINYINT UNSIGNED NOT NULL COMMENT 'Orden de la afiliación para ese autor en esa publicación',
  PRIMARY KEY (publicacion_id, autor_id, afiliacion_id),
  KEY idx_paa_afiliacion (afiliacion_id),
  CONSTRAINT fk_paa_publicacion_autor FOREIGN KEY (publicacion_id, autor_id)
    REFERENCES publicacion_autor (publicacion_id, autor_id) ON DELETE CASCADE,
  CONSTRAINT fk_paa_afiliacion FOREIGN KEY (afiliacion_id) REFERENCES afiliacion (afiliacion_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Afiliación declarada por cada autor en cada publicación';
