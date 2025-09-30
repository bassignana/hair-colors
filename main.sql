DROP TABLE IF EXISTS test_results;
CREATE TABLE test_results
(
    id            serial PRIMARY KEY,
    test_id       text    NOT NULL,
    vero_nome     text    NOT NULL,
    la_tua_scelta text    NOT NULL,
    corretto      integer NOT NULL
);