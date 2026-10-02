CREATE TABLE IF NOT EXISTS parcels (
    print_key_code      VARCHAR(40)  NOT NULL,
    roll_year           INTEGER      NOT NULL,
    municipality_name   VARCHAR(100),
    swis_code           VARCHAR(10)  NOT NULL,
    property_class      VARCHAR(10),
    property_class_desc VARCHAR(200),
    address_number      VARCHAR(20),
    address_street      VARCHAR(120),
    owner_name          VARCHAR(200),
    zip                 VARCHAR(10),
    full_market_value   BIGINT,
    assessment_land     BIGINT,
    assessment_total    BIGINT,
    fetched_at          TIMESTAMPTZ  NOT NULL DEFAULT now(),
    PRIMARY KEY (swis_code, print_key_code, roll_year)
);

CREATE INDEX IF NOT EXISTS parcels_municipality_idx ON parcels (municipality_name, roll_year);

CREATE TABLE IF NOT EXISTS changes(
    id                  SERIAL PRIMARY KEY,
    swis_code           VARCHAR(10)  NOT NULL,
    print_key_code      VARCHAR(40)  NOT NULL,
    roll_year           INTEGER      NOT NULL,
    kind                VARCHAR(30)  NOT NULL,
    municipality    VARCHAR(100),
    address         VARCHAR(160),
    old_value       VARCHAR(200),
    new_value       VARCHAR(200),
    pct             NUMERIC(8,1),
    title           VARCHAR(300) NOT NULL,
    summary         TEXT         NOT NULL,
    impact          VARCHAR(10)  NOT NULL,
    detected_at     TIMESTAMPTZ  NOT NULL DEFAULT now(),
    UNIQUE (swis_code, print_key_code, roll_year, kind)
);

CREATE TABLE IF NOT EXISTS watches (
    id            SERIAL PRIMARY KEY,
    email         VARCHAR(200) NOT NULL,
    address       VARCHAR(160) NOT NULL,
    address_key   VARCHAR(160) NOT NULL,
    municipality  VARCHAR(100),
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT now()
);

ALTER TABLE changes ADD COLUMN IF NOT EXISTS address_key VARCHAR(160);
CREATE INDEX IF NOT EXISTS changes_address_key_idx ON changes (address_key);

CREATE TABLE IF NOT EXISTS notifications (
    id          SERIAL PRIMARY KEY,
    watch_id    INTEGER NOT NULL REFERENCES watches(id),
    change_id   INTEGER NOT NULL REFERENCES changes(id),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (watch_id, change_id)
);

CREATE TABLE IF NOT EXISTS sales (
    print_key_code  VARCHAR(40)  NOT NULL,
    sale_date       DATE         NOT NULL,
    price           BIGINT,
    book            VARCHAR(10)  NOT NULL,
    page            VARCHAR(10)  NOT NULL,
    condition       VARCHAR(100),
    fetched_at      TIMESTAMPTZ  NOT NULL DEFAULT now(),
    PRIMARY KEY (print_key_code, sale_date, book, page)
);
