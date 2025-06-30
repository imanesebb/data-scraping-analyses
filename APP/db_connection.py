import oracledb

def get_connection():
    return oracledb.connect(
                 user="SYS",
                 password="",
                 dsn="",
                 mode=oracledb.SYSDBA
    )
