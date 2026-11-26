CREATE TABLE afiliacion (
  afiliacion_id   INT UNSIGNED NOT NULL AUTO_INCREMENT,
  texto           VARCHAR(600) NOT NULL COMMENT 'Cadena de afiliación completa de Scopus',
  institucion_id  INT UNSIGNED NOT NULL,
  PRIMARY KEY (afiliacion_id),
  UNIQUE KEY uq_afiliacion_texto (texto),
  KEY idx_afiliacion_institucion (institucion_id),
  CONSTRAINT fk_afiliacion_institucion
    FOREIGN KEY (institucion_id) REFERENCES institucion (institucion_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Afiliación a nivel departamento/unidad; el país se obtiene vía institución';