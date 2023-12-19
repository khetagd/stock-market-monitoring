import psycopg2

host = "roundhouse.proxy.rlwy.net"
user = "postgres"
password = "DG-Gbeda6BadF4ABFAGDBBe1gccCC*63"
db_name = "railway"
port = 52447

try:
    connection = psycopg2.connect(
        host = host,
        user = user,
        password = password,
        database = db_name,
        port = port
    )

except Exception as e:
    print(e)
    
    
    