CREATE TABLE data(
    time       TIMESTAMPTZ NOT NULL,
    value      DOUBLE PRECISION NOT NULL,
    id  INTEGER NOT NULL
);
SELECT create_hypertable('data', 'time');
CREATE INDEX ON data(id, time DESC);

ALTER TABLE data
  SET (timescaledb.compress,
      timescaledb.compress_orderby = 'time DESC',
      timescaledb.compress_segmentby = 'id');
SELECT add_compression_policy('data', INTERVAL '14 days');
