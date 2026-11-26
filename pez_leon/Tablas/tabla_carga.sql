CREATE TABLE carga (
  carga_id         INT UNSIGNED  NOT NULL AUTO_INCREMENT,
  archivo_origen   VARCHAR(255)  NOT NULL COMMENT 'Nombre del CSV exportado de Scopus',
  base_origen      VARCHAR(50)   NOT NULL DEFAULT 'Scopus',
  consulta         VARCHAR(255)  NULL     COMMENT 'Término de búsqueda usado en la base de origen',
  total_registros  INT UNSIGNED  NOT NULL,
  fecha_carga      DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Fecha en que corrió el ETL',
  PRIMARY KEY (carga_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Cada ejecución del ETL registra aquí su archivo de origen';