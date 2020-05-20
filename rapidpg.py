""" rapidpg module """

import ctypes
from enum import IntEnum


class Parameters:
    """ pg parameters encapsulation """

    class Wrapper(ctypes.Structure):
        """ pg parameters wrapper """
        _fields_ = [('lengths', ctypes.POINTER(ctypes.c_int)),
                    ('pointers', ctypes.POINTER(ctypes.c_char_p)),
                    ('values', ctypes.c_char_p),
                    ('size', ctypes.c_size_t),
                    ('current', ctypes.c_size_t),
                    ('capacity', ctypes.c_size_t),
                    ('length', ctypes.c_size_t)
                    ]

    librapidpg = ctypes.CDLL('./librapidpg.so')

    librapidpg.rapidpg_create_parameters.restype = ctypes.POINTER(
        Wrapper)
    librapidpg.rapidpg_create_parameters.argtypes = []

    librapidpg.rapidpg_set_current.restype = ctypes.c_int
    librapidpg.rapidpg_set_current.argtypes = [ctypes.POINTER(Wrapper),
                                               ctypes.c_size_t]

    librapidpg.rapidpg_add_int.restype = ctypes.c_int
    librapidpg.rapidpg_add_int.argtypes = [ctypes.POINTER(Wrapper),
                                           ctypes.c_longlong]

    librapidpg.rapidpg_add_double.restype = ctypes.c_int
    librapidpg.rapidpg_add_double.argtypes = [ctypes.POINTER(Wrapper),
                                              ctypes.c_double]

    librapidpg.rapidpg_add_ip4_hbo.restype = ctypes.c_int
    librapidpg.rapidpg_add_ip4_hbo.argtypes = [ctypes.POINTER(Wrapper),
                                               ctypes.c_uint]

    librapidpg.rapidpg_destroy_parameters.restype = None
    librapidpg.rapidpg_destroy_parameters.argtypes = [ctypes.POINTER(Wrapper)]

    def __init__(self):
        self.parameters = Parameters.librapidpg.rapidpg_create_parameters()

    def __del__(self):
        Parameters.librapidpg.rapidpg_destroy_parameters(self.parameters)

    def set_current(self):
        """ set current parameter """
        Parameters.librapidpg.rapidpg_set_current(self.parameters)

    def add_int(self):
        """ add int """
        Parameters.librapidpg.rapidpg_add_int(self.parameters)

    def add_double(self):
        """ add double """
        Parameters.librapidpg.rapidpg_add_double(self.parameters)

    def add_ip4_hbo(self):
        """ add IPv4 address """
        Parameters.librapidpg.rapidpg_add_ip4_hbo(self.parameters)


libpq = ctypes.CDLL('libpq.so')


class CtypesEnum(IntEnum):
    """A ctypes-compatible IntEnum superclass."""
    @classmethod
    def from_param(cls, obj):
        """ todo """
        return int(obj)


class ExecStatusType(CtypesEnum):
    """ enum ExecStatusType """

    PGRES_EMPTY_QUERY = 0       # empty query string was executed

    # a query command that doesn't return
    # anything was executed properly by the
    # backend
    PGRES_COMMAND_OK = 1

    # a query command that returns tuples was
    # executed properly by the backend PGresult
    # contains the result tuples
    PGRES_TUPLES_OK = 2

    PGRES_COPY_OUT = 3          # Copy Out data transfer in progress
    PGRES_COPY_IN = 4           # Copy In data transfer in progress

    # an unexpected response was recv'd from the
    # backend
    PGRES_BAD_RESPONSE = 5

    PGRES_NONFATAL_ERROR = 6    # notice or warning message
    PGRES_FATAL_ERROR = 7       # query failed
    PGRES_COPY_BOTH = 8         # Copy In/Out data transfer in progress
    PGRES_SINGLE_TUPLE = 9      # single tuple from larger resultset


libpq.PQresultStatus.restype = ExecStatusType
libpq.PQresultStatus.argtypes = [ctypes.c_void_p]

libpq.PQclear.restype = None
libpq.PQclear.argtypes = [ctypes.c_void_p]

libpq.PQexec.restype = ctypes.c_void_p
libpq.PQexec.argtypes = [ctypes.c_void_p, ctypes.c_char_p]

libpq.PQconnectdbParams.restype = ctypes.c_void_p
libpq.PQconnectdbParams.argtypes = [ctypes.POINTER(ctypes.c_char_p),
                                    ctypes.POINTER(ctypes.c_char_p),
                                    ctypes.c_int]


class ConnStatusType(CtypesEnum):
    """ enum ConnStatusType """
    CONNECTION_OK = 0
    CONNECTION_BAD = 1
    # Non-blocking mode only below here

    #
    # The existence of these should never be relied upon - they should only
    # be used for user feedback or similar purposes.
    #

    CONNECTION_STARTED = 2              # Waiting for connection to be made
    CONNECTION_MADE = 3                 # Connection OK; waiting to send.
    CONNECTION_AWAITING_RESPONSE = 4    # Waiting for a response from the
                                        # postmaster.
    CONNECTION_AUTH_OK = 5              # Received authentication; waiting for
                                        # backend startup.
    CONNECTION_SETENV = 6               # Negotiating environment.
    CONNECTION_SSL_STARTUP = 7          # Negotiating SSL.
    CONNECTION_NEEDED = 8               # Internal state: connect() needed
    CONNECTION_CHECK_WRITABLE = 9       # Check if we could make a writable
                                        # connection.
    CONNECTION_CONSUME = 10             # Wait for any pending message and
                                        # consume them.


libpq.PQstatus.restype = ConnStatusType
libpq.PQstatus.argtypes = [ctypes.c_void_p]

libpq.PQerrorMessage.restype = ctypes.c_char_p
libpq.PQerrorMessage.argtypes = [ctypes.c_void_p]

libpq.PQfinish.restype = None
libpq.PQfinish.argtypes = [ctypes.c_void_p]

libpq.PQexecPrepared.restype = ctypes.c_void_p
libpq.PQexecPrepared.argtypes = [ctypes.c_void_p, ctypes.c_char_p,
                                 ctypes.c_int, ctypes.POINTER(ctypes.c_char_p),
                                 ctypes.POINTER(ctypes.c_int),
                                 ctypes.POINTER(ctypes.c_int), ctypes.c_int]

libpq.PQresultErrorMessage.restype = ctypes.c_char_p
libpq.PQresultErrorMessage.argtypes = [ctypes.c_void_p]


class Result:
    """ Wrapper of PGresult* """

    def __init__(self, result, sql):
        self.pg_result = result
        self.sql = sql

    def __del__(self):
        if self.pg_result is not None:
            libpq.PQclear(self.pg_result)

    def has_result(self):
        """ is there a result """
        return self.pg_result is not None

    def status(self):
        """ whether result is ok """
        return (libpq.PQresultStatus(self.pg_result) ==
                ExecStatusType.PGRES_COMMAND_OK)

    def error_message(self):
        """ get result error message"""
        return libpq.PQresultErrorMessage(self.pg_result).decode('utf-8')


class Connection:
    """ Wrapper of PGconn* """

    RAPID_PG_BINARY = ctypes.POINTER(ctypes.c_int).in_dll(libpq,
                                                          'RAPID_PG_BINARY')

    def __init__(self, conn_params):
        keys = (ctypes.c_char_p * (len(conn_params) + 1))()
        values = (ctypes.c_char_p * (len(conn_params) + 1))()
        keys[:-1] = conn_params.keys()
        values[:-1] = conn_params.values()
        keys[len(conn_params)] = None
        values[len(conn_params)] = None
        self.pg_conn = libpq.PQconnectdbParams(keys, values, 0)

    def __del__(self):
        if self.pg_conn is not None:
            libpq.PQfinish(self.pg_conn)

    def is_connected(self):
        """ Whether connection is established """
        return self.pg_conn is not None

    def status(self):
        """ Whether connection status is ok """
        return libpq.PQstatus(self.pg_conn) == ConnStatusType.CONNECTION_OK

    def error_message(self):
        """ Get connection error message """
        return libpq.PQerrorMessage(self.pg_conn).decode('utf-8')

    def exec(self, sql):
        """ execute sql w/o parameters """
        return Result(libpq.PQexec(self.pg_conn, sql.encode('utf-8')), sql)

    def exec_prepared(self, statement, parameters):
        """ execute prepared statement """
        contents = parameters.parameters.contents
        return Result(libpq.PQexecPrepared(
            self.pg_conn,
            statement.encode('utf-8'),
            contents.size,
            contents.pointers,
            contents.lengths,
            Connection.RAPID_PG_BINARY,
            1), statement)
