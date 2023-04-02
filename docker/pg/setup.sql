CREATE TABLE testschema(
    time       TIMESTAMPTZ NOT NULL,
    value      DOUBLE PRECISION NOT NULL,
    sensor_id  INTEGER NOT NULL
);
SELECT create_hypertable('testschema', 'time');
CREATE INDEX ON testschema(sensor_id, time DESC);

ALTER TABLE testschema
  SET (timescaledb.compress,
      timescaledb.compress_orderby = 'time DESC',
      timescaledb.compress_segmentby = 'sensor_id');
SELECT add_compression_policy('testschema', INTERVAL '14 days');
