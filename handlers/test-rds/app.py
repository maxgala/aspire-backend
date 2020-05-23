import json
import psycopg2


def lambda_handler(event, context):
    try:
        connection = psycopg2.connect(
            user="master",
            password="password",
            host="bakhit-sam-db.cl3m8kiucudq.ca-central-1.rds.amazonaws.com",
            port="5432",
            database="aspire_db"
        )

        cursor = connection.cursor()
        # Print PostgreSQL Connection properties
        print(connection.get_dsn_parameters(), "\n")

        # Print PostgreSQL version
        cursor.execute("SELECT version();")
        record = cursor.fetchone()
        print("You are connected to - ", record, "\n")

        cursor.execute("SELECT * FROM cars;")
        records = cursor.fetchall()
        print(records)

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        # closing database connection.
        if (connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "hello from read",
            "cars": records
        }),
    }
