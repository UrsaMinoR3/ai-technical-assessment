CREATE TABLE IF NOT EXISTS request_logs (
    id          SERIAL PRIMARY KEY,
    timestamp   TIMESTAMP NOT NULL DEFAULT NOW(),
    endpoint    VARCHAR(100) NOT NULL,
    input_data  TEXT,
    output_ref  TEXT,
    external_usage VARCHAR(500),
    latency_ms  FLOAT,
    http_status INTEGER
);

CREATE INDEX IF NOT EXISTS idx_request_logs_endpoint  ON request_logs (endpoint);
CREATE INDEX IF NOT EXISTS idx_request_logs_timestamp ON request_logs (timestamp);
