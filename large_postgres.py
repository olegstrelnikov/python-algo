""" Test postgresql table with ~100M records / 2.5G in size """

import psycopg2


def test_database(host, user, password, database):
    """Fills in database table and executes aggregate query on it"""
    conn = psycopg2.connect("host='{}' user='{}' password='{}'"
                            .format(host, user, password))
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM pg_database WHERE datname=%s", (database,))
    if cur.rowcount == 0:
        isolation_level = conn.isolation_level
        conn.set_isolation_level(
            psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        cur.execute("CREATE DATABASE {}".format(database))
        conn.set_isolation_level(isolation_level)
    conn.close()
    conn = psycopg2.connect(host=host, user=user, password=password,
                            dbname=database)
    cur = conn.cursor()
    cur.execute("""
        CREATE EXTENSION IF NOT EXISTS pgcrypto;
        CREATE TABLE IF NOT EXISTS large_conversations
        (
            guid UUID NOT NULL DEFAULT gen_random_uuid(),
            host_from character varying,
            host_to character varying,
            ip_from inet,
            ip_to inet,
            service character varying,
            inbound double precision,
            outbound double precision,
            attrs jsonb,
            CONSTRAINT pk_conversations PRIMARY KEY(guid),
            CONSTRAINT uq_converstions UNIQUE
                (host_from, host_to, ip_from, ip_to, service),
            CONSTRAINT ck_inbound CHECK(inbound >= 0.0),
            CONSTRAINT ck_outbound CHECK(outbound >= 0.0)
        );
        DELETE FROM large_conversations;
        """
                )
    conn.commit()


test_database("192.168.1.84", "jtac", "jtac", "large")
