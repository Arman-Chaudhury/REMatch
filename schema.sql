CREATE TABLE IF NOT EXISTS parcels (
    print_key_code      VARCHAR(40)  NOT NULL,
    roll_year           INTEGER      NOT NULL,
    municipality_name   VARCHAR(100),
    swis_code           VARCHAR(10),
    property_class      VARCHAR(10),
    property_class_desc VARCHAR(120),
    address_number      VARCHAR(20),
    address_street      VARCHAR(120),
    owner_name          VARCHAR(200),
    zip                 VARCHAR(10),
    full_market_value   BIGINT,
    assessment_land     BIGINT,
    assessment_total    BIGINT,
    fetched_at          TIMESTAMPTZ  NOT NULL DEFAULT now(),
    PRIMARY KEY (print_key_code, roll_year)
);

CREATE INDEX IF NOT EXISTS parcels_municipality_idx ON parcels (municipality_name, roll_year)