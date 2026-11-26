CREATE TABLE publicacion_palabra_clave (
  publicacion_id    INT UNSIGNED NOT NULL,
  palabra_clave_id  INT UNSIGNED NOT NULL,
  origen            ENUM('autor','indice') NOT NULL COMMENT 'autor = Author Keywords; indice = Index Keywords',
  PRIMARY KEY (publicacion_id, palabra_clave_id, origen),
  KEY idx_ppk_palabra (palabra_clave_id),
  CONSTRAINT fk_ppk_publicacion FOREIGN KEY (publicacion_id)   REFERENCES publicacion (publicacion_id) ON DELETE CASCADE,
  CONSTRAINT fk_ppk_palabra     FOREIGN KEY (palabra_clave_id) REFERENCES palabra_clave (palabra_clave_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;