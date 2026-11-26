CREATE TABLE institucion (
  institucion_id  INT UNSIGNED NOT NULL AUTO_INCREMENT,
  nombre          VARCHAR(255) NOT NULL COMMENT 'Institución principal extraída de la afiliación',
  pais_id         SMALLINT UNSIGNED NULL,
  PRIMARY KEY (institucion_id),
  UNIQUE KEY uq_institucion_nombre_pais (nombre, pais_id),
  KEY idx_institucion_pais (pais_id),
  CONSTRAINT fk_institucion_pais FOREIGN KEY (pais_id) REFERENCES pais (pais_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Universidades, centros y agencias (una misma institución puede existir en varios países)';