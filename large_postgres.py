""" Test postgresql table with ~100M records / 2.5G in size """

import psycopg2


def test_database(host, user, password, database):
    """Fills in database table and executes aggregate query on it"""
    conn = psycopg2.connect("host='{}' user='{}' password='{}'"
                            .format(host, user, password))
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM pg_database WHERE datname=%s", (database,))
    if cur.rowcount == 0:
        conn.set_isolation_level(
            psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        cur.execute("CREATE DATABASE {}".format(database))


test_database("192.168.1.84", "jtac", "jtac", "large")
