""" Test postgresql table with ~100M records / 2.5G in size """

import random
import string
import time
import rapidpg


def generate_host(length):
    """Generate random host name"""
    return "".join(random.choice(string.ascii_lowercase)
                   for _ in range(length))


def generate_insert_values(records, columns):
    """Generate SQL script"""
    return ",".join("(" + ",".join("$"+str(i) for i in range(
        j*columns + 1, j*columns + columns + 1)) + ")" for j in range(records))


IP_ADDRESSES = 2**24 - 2
SERVICES = ("http", "smb", "cifs", "nfs", "scsi", "voip", "dns",
            "dns", "https", "ftp", "iscsi", "amazon")
TLDS = ("com", "net", "org", "us", "ru")

NTLDS = len(TLDS)
NHOSTS = 100
IP_BASE = 10*2**24 + 1
NIPS = 2**24 - 2
HOSTS = [
    (NTLDS*(1 + 2*i),
     NTLDS*(2 + 2*i),
     IP_BASE + random.randrange(0, IP_ADDRESSES),
     1 + (i % len(SERVICES)),
     random.uniform(0.0, 1000.0),
     random.uniform(0.0, 1000.0)
     ) for i in range(NHOSTS//2)]


def fill_in_parameters(parameters, i, to_i):
    """ fill in inserter parameters """
    parameters.set_current(0)
    while i < to_i:
        host = i % (NHOSTS // 2)
        ip_from_index = i // (NHOSTS // 2)
        host_from_index = ip_from_index // NIPS
        host_to_index = host_from_index // NTLDS
        parameters.add_int(HOSTS[host][0] + (host_from_index % NTLDS))
        parameters.add_int(HOSTS[host][1] + (host_to_index % NTLDS))
        parameters.add_ip4_hbo(IP_BASE + ip_from_index % NIPS)
        parameters.add_ip4_hbo(HOSTS[host][2])
        parameters.add_int(HOSTS[host][3])
        parameters.add_double(HOSTS[host][4])
        parameters.add_double(HOSTS[host][5])
        i += 1


def add_records(conn, records, records_at_once, parameters):
    """ todo """
    i = records_at_once
    while i < records:
        parameters.set_current(0)
        fill_in_parameters(parameters, i - records_at_once, i)
        conn.exec_prepared("inserter", parameters)
        i += records_at_once


def test_database(host, user, password, database, records):
    """Fills in database table and executes aggregate query on it"""
    conn = rapidpg.Connection({"hostaddr": host, "user": user,
                               "password": password, "dbname": "postgres"})
    assert conn.is_connected()
    assert conn.status()
    res = conn.execute("SELECT 1 FROM pg_database WHERE datname='{}'"
                       .format(database))
    assert res.has_result()
    assert res.status() == rapidpg.Result.ExecStatusType.PGRES_TUPLES_OK
    if res.rowcount() == 0:
        res = conn.execute("CREATE DATABASE {}".format(database))
        assert res.has_result()
        assert res.status() == rapidpg.Result.ExecStatusType.PGRES_COMMAND_OK
    conn = rapidpg.Connection({"hostaddr": host, "user": user,
                               "password": password, "dbname": database})
    assert conn.is_connected()
    assert conn.status()
    records_at_once = 65536 // 7
    res = conn.execute((
        """
        CREATE EXTENSION IF NOT EXISTS pgcrypto;
        DROP TABLE IF EXISTS {0};
        CREATE TABLE IF NOT EXISTS {0}
        (
            --guid UUID NOT NULL DEFAULT gen_random_uuid(),
            host_from bigint,
            host_to bigint,
            ip_from inet,
            ip_to inet,
            service bigint,
            inbound double precision,
            outbound double precision--,
            --attrs jsonb--,
            --CONSTRAINT pk_conversations PRIMARY KEY(guid),
            --CONSTRAINT uq_converstions UNIQUE
            --    (host_from, host_to, ip_from, ip_to, service),
            --CONSTRAINT ck_inbound CHECK(inbound >= 0.0),
            --CONSTRAINT ck_outbound CHECK(outbound >= 0.0)
        );
        ALTER TABLE {0} SET UNLOGGED;
        --SET synchronous_commit TO OFF;
        --SET commit_delay TO 100000;
        DELETE FROM {0};
        PREPARE inserter AS
            INSERT INTO {0}
            (host_from, host_to, ip_from, ip_to, service, inbound, outbound)
            VALUES
        """ + generate_insert_values(records_at_once, 7) + ";")
        .format("large_conversations")
        )

    assert res.has_result()
    assert res.status() == rapidpg.Result.ExecStatusType.PGRES_COMMAND_OK

    now = time.monotonic()
    res = conn.execute("BEGIN TRANSACTION")

    assert res.has_result()
    assert res.status() == rapidpg.Result.ExecStatusType.PGRES_COMMAND_OK

    assert records <= IP_ADDRESSES*len(SERVICES)*len(TLDS)*len(TLDS)
    parameters = rapidpg.Parameters()
    add_records(conn, records, records_at_once, parameters)
    records_at_once = records % records_at_once
    if records_at_once > 0:
        res = conn.execute((
            """
            DEALLOCATE inserter;
            PREPARE inserter AS
              INSERT INTO {0}
              (host_from, host_to, ip_from, ip_to, service, inbound, outbound)
              VALUES
            """ + generate_insert_values(records_at_once, 7) + ";")
            .format("large_conversations")
            )
        assert res.has_result()
        assert res.status() == rapidpg.Result.ExecStatusType.PGRES_COMMAND_OK
        fill_in_parameters(parameters, records - records_at_once, records)
        res = conn.exec_prepared("inserter", parameters)
        assert res.has_result()
        assert res.status() == rapidpg.Result.ExecStatusType.PGRES_COMMAND_OK
    res = conn.execute("DEALLOCATE inserter; COMMIT TRANSACTION")
    assert res.has_result()
    assert res.status() == rapidpg.Result.ExecStatusType.PGRES_COMMAND_OK
    print(records, "records inserted --- {:.3} seconds".format(
        time.monotonic() - now))


for rec in (100, 1000, 10**4, 10**5, 10**6, 10**7, 10**8):
    test_database("192.168.8.180", "test", "test", "large", rec)
