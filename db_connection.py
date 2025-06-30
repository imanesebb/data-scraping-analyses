import oracledb

def get_connection():
    return oracledb.connect(
                 user="SYS",
                 password="niggaballz12345678",
                 dsn="localhost/orcliman",
                 mode=oracledb.SYSDBA
    )
