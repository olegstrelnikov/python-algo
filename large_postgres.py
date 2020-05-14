""" Test postgresql table with ~100M records / 2.5G in size """

import random
import string
import time
import ipaddress
import psycopg2


def generate_host(length):
    """Generate random host name"""
    return "".join(random.choice(string.ascii_lowercase)
                   for _ in range(length))


def generate_record(tlds, services, ip_addresses, hosts_num, base):
    """Generate conversations db table record"""
    tlds_num = len(tlds)
    hosts = [
        (tlds_num*(1 + 2*i),
         tlds_num*(2 + 2*i),
         str(ipaddress.IPv4Address(
            base + random.randrange(0, ip_addresses))),
         1 + (i % len(services)),
         ) for i in range(hosts_num//2)]

    for tld1 in range(tlds_num):
        for tld2 in range(tlds_num):
            for ip1 in range(ip_addresses):
                str_ip1 = str(ipaddress.IPv4Address(base + ip1))
                for host1, host2, ip2, service in hosts:
                    yield (host1 + tld1, host2 + tld2, str_ip1, ip2,
                           service, random.uniform(0.0, 1000.0),
                           random.uniform(0.0, 1000.0))


def generate_values(tlds, services, ip_addresses, hosts_num, base):
    """Generate conversations db table record"""
    tlds_num = len(tlds)
    hosts = [
        (tlds_num*(1 + 2*i),
         tlds_num*(2 + 2*i),
         str(ipaddress.IPv4Address(
            base + random.randrange(0, ip_addresses))),
         1 + (i % len(services)),
         ) for i in range(hosts_num//2)]

    for tld1 in range(tlds_num):
        for tld2 in range(tlds_num):
            for ip1 in range(ip_addresses):
                str_ip1 = str(ipaddress.IPv4Address(base + ip1))
                for host1, host2, ip2, service in hosts:
                    yield host1 + tld1
                    yield host2 + tld2
                    yield str_ip1
                    yield ip2
                    yield service
                    yield random.uniform(0.0, 1000.0)
                    yield random.uniform(0.0, 1000.0)


def generate_table(rowcount, record):
    """Generate rowcount table records"""
    gen = generate_record(*record)
    for _ in range(rowcount):
        try:
            yield next(gen)
        except StopIteration:
            return


def generate_insert_values(records, columns):
    """Generate SQL script"""
    return ",".join("(" + ",".join("$"+str(i) for i in range(j*columns + 1, j*columns + columns + 1)) + ")" for j in range(records))


def test_database(host, user, password, database, records):
    """Fills in database table and executes aggregate query on it"""
    conn = psycopg2.connect(host=host, user=user,
                            password=password, dbname="postgres")
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM pg_database WHERE datname=%s", (database,))
    if cur.rowcount == 0:
        isolation_level = conn.isolation_level
        conn.set_isolation_level(
            psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        cur.execute("CREATE DATABASE {}".format(database))
        conn.set_isolation_level(isolation_level)
    conn.close()
    conn = psycopg2.connect(host=host, user=user,
                            password=password, dbname=database)
    conn.set_isolation_level(
        psycopg2.extensions.ISOLATION_LEVEL_REPEATABLE_READ)
    cur = conn.cursor()
    records_at_once = 65536 // 7
    cur.execute((
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

    ip_addresses = 2**24 - 2
    services = ("http", "smb", "cifs", "nfs", "scsi", "voip", "dns",
                "dns", "https", "ftp", "iscsi", "amazon")
    tlds = ("com", "net", "org", "us", "ru")

    assert records <= ip_addresses*len(services)*len(tlds)*len(tlds)
    gen = generate_values(tlds, services, ip_addresses, 100, 10*2**24 + 1)
    now = time.monotonic()
    for _ in range(records // records_at_once):
        cur.execute("EXECUTE inserter (" +
                    "%s, "*(7*records_at_once - 1) + "%s);",
                    [next(gen) for _ in range(7*records_at_once)])
    records_at_once = records % records_at_once
    if records_at_once > 0:
        cur.execute((
            """
            DEALLOCATE inserter;
            PREPARE inserter AS
                INSERT INTO {0}
                (host_from, host_to, ip_from, ip_to, service, inbound, outbound)
                VALUES
            """ + generate_insert_values(records_at_once, 7) + ";")
            .format("large_conversations")
            )
        cur.execute("EXECUTE inserter (" +
                    "%s, "*(7*records_at_once - 1) + "%s);",
                    [next(gen) for _ in range(7*records_at_once)])
    cur.execute("DEALLOCATE inserter;")
    conn.commit()
    print(records, "records inserted --- {:.3} seconds".format(
        time.monotonic() - now))


for rec in (1000, 10**4, 10**5, 10**6, 10**7, 10**8):
    test_database("192.168.8.180", "test", "test", "large", rec)
