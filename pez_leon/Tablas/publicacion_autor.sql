CREATE TABLE publicacion_autor (
  publicacion_id  INT UNSIGNED      NOT NULL,
  autor_id        INT UNSIGNED      NOT NULL,
  orden           SMALLINT UNSIGNED NOT NULL COMMENT 'Posición en la lista de autores (1 = primer autor)',
  PRIMARY KEY (publicacion_id, autor_id),
  UNIQUE KEY uq_publicacion_autor_orden (publicacion_id, orden),
  KEY idx_publicacion_autor_autor (autor_id),
  CONSTRAINT fk_pa_publicacion FOREIGN KEY (publicacion_id) REFERENCES publicacion (publicacion_id) ON DELETE CASCADE,
  CONSTRAINT fk_pa_autor       FOREIGN KEY (autor_id)       REFERENCES autor (autor_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Autoría: quién firmó cada publicación y en qué posición';