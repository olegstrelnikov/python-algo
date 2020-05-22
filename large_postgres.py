""" Test postgresql table with ~100M records / 2.5G in size """

import random
import string
import time
import ipaddress
import rapidpg


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
         base + random.randrange(0, ip_addresses),
         1 + (i % len(services)),
         ) for i in range(hosts_num//2)]

    for tld1 in range(tlds_num):
        for tld2 in range(tlds_num):
            for ip1 in range(ip_addresses):
                str_ip1 = base + ip1
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
    return ",".join("(" + ",".join("$"+str(i) for i in range(
        j*columns + 1, j*columns + columns + 1)) + ")" for j in range(records))


def fill_in_parameters(parameters, records_at_once, gen):
    """ fill in inserter parameters """
    parameters.set_current(0)
    for _ in range(records_at_once):
        record = next(gen)
        parameters.add_int(record[0])
        parameters.add_int(record[1])
        parameters.add_ip4_hbo(record[2])
        parameters.add_ip4_hbo(record[3])
        parameters.add_int(record[4])
        parameters.add_double(record[5])
        parameters.add_double(record[6])


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

    ip_addresses = 2**24 - 2
    services = ("http", "smb", "cifs", "nfs", "scsi", "voip", "dns",
                "dns", "https", "ftp", "iscsi", "amazon")
    tlds = ("com", "net", "org", "us", "ru")

    assert records <= ip_addresses*len(services)*len(tlds)*len(tlds)
    gen = generate_record(tlds, services, ip_addresses, 100, 10*2**24 + 1)
    parameters = rapidpg.Parameters()
    for _ in range(records // records_at_once):
        fill_in_parameters(parameters, records_at_once, gen)
        res = conn.exec_prepared("inserter", parameters)
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
        fill_in_parameters(parameters, records_at_once, gen)
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
