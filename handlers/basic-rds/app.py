import sys
import json
import logging
import psycopg2

#rds settings
rds_host  = "aspire-db.cl3m8kiucudq.ca-central-1.rds.amazonaws.com"
rds_port = "5432"
name = "master"
password = "password"
db_name = "main_db"

logger = logging.getLogger()
logger.setLevel(logging.INFO)

try:
    conn = psycopg2.connect(user=name, password=password, host=rds_host,
                            port=rds_port, database=db_name)
except psycopg2.Error as e:
    logger.error("ERROR: Unexpected error: Could not connect to PostgreSQL instance.")
    logger.error(e)
    sys.exit()

logger.info("SUCCESS: Connection to RDS PostgreSQL instance succeeded")
def handler(event, context):
    """
    This function fetches content from PostgreSQL RDS instance
    """

    item_count = 0

    with conn.cursor() as cur:
        cur.execute("DROP TABLE IF EXISTS employees;")
        cur.execute("CREATE TABLE employees (id SERIAL PRIMARY KEY, name VARCHAR(50) NOT NULL);")
        cur.execute("INSERT INTO employees (name) VALUES ('Joe'),('Bob'),('Mary');")
        conn.commit()
        cur.execute("SELECT * FROM employees;")
        records = []
        for row in cur:
            item_count += 1
            logger.info(row)
            records.append(row)
    conn.commit()

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Added %d items from RDS PostgreSQL table" % (item_count),
            "cars": records
        }),
    }
