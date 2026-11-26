CREATE TABLE fuente_identificador (
  fuente_id  SMALLINT UNSIGNED NOT NULL,
  tipo       ENUM('ISSN','ISBN') NOT NULL,
  valor      VARCHAR(20) NOT NULL,
  PRIMARY KEY (fuente_id, tipo, valor),
  KEY idx_fuente_identificador_valor (valor),
  CONSTRAINT fk_fuente_identificador_fuente
    FOREIGN KEY (fuente_id) REFERENCES fuente (fuente_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='ISSN/ISBN de cada fuente (una revista puede tener ISSN impreso y electrónico)';