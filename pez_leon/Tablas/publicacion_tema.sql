CREATE TABLE publicacion_tema (
  publicacion_id  INT UNSIGNED     NOT NULL,
  tema_id         TINYINT UNSIGNED NOT NULL,
  metodo          ENUM('reglas','ia','manual') NOT NULL DEFAULT 'reglas'
                  COMMENT 'reglas = ETL por palabras clave; ia = clasificación con Claude; manual = validado por CICY',
  confianza       DECIMAL(3,2) NULL COMMENT 'Solo para método ia (0.00 a 1.00)',
  PRIMARY KEY (publicacion_id, tema_id, metodo),
  KEY idx_pt_tema (tema_id),
  CONSTRAINT fk_pt_publicacion FOREIGN KEY (publicacion_id) REFERENCES publicacion (publicacion_id) ON DELETE CASCADE,
  CONSTRAINT fk_pt_tema        FOREIGN KEY (tema_id)        REFERENCES tema (tema_id),
  CONSTRAINT chk_pt_confianza  CHECK (confianza IS NULL OR confianza BETWEEN 0 AND 1)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Clasificación temática; puede coexistir la de reglas, IA y validación manual';