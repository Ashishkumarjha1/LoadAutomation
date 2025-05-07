import pymysql
import subprocess


def createDatabase(db_name,db_ip):
    
    # Connect to database
    try:
        db = pymysql.connect(host=db_ip, user="root", password="pass")
        cursor = db.cursor()
        print("Successfully connected to database.")
    except pymysql.Error as e:
        print(f"Failed to connect to database: {e}")
        return "connectionFailed"

    # Check if database exists
    if cursor.execute(f"SHOW DATABASES LIKE '{db_name}'"):
        print(f"Database {db_name} already exists. Skipping creation.")
        return "alreadyCreated"
    else:
        # Create database and tables
        print(f"Creating database {db_name}...")
        try:
            cursor.execute(f"CREATE DATABASE {db_name}")
            print(f"Successfully created database {db_name}.")
            return "creationSuccess"
        except pymysql.Error as e:
            print(f"Failed to create database {db_name}: {e}")
            db.rollback()
            db.close()
            return "creaionFailed"

def connectDB(db_name,db_ip):
    try:
        db = pymysql.connect(
            host=db_ip,
            user="root",
            password="pass",
            database=db_name
        )
        # cursor=db.cursor()
        # print("Successfully connected to database.")
        return db
        
    except pymysql.Error as e:
        print(f"Failed to connect to database: {e}")
        return False


def createDefaultTables(db_name,db_ip):
    # Open connection to database
    db = connectDB(db_name,db_ip)
    if db == False:
        return "connectionFailed"
    else:
        cursor=db.cursor()

    # Open SQL file and read its contents
    try:
        with open("/home/allgovision/LoadTest_Scripts/default-tables.sql", "r") as f:
            sql = f.read()
        # print("Successfully read SQL file.")
    except IOError as e:
        print(f"Failed to read SQL file: {e}")
        db.close()
        return "failedSqlFile"

    # Split SQL file into individual queries
    queries = sql.split(';')

    # Remove empty queries
    queries = [q.strip() for q in queries if q.strip()]

    # Execute each query one by one
    
    try:
        for query in queries:
            cursor.execute(query)
            db.commit()
        print("Successfully created default tables.")
        return "creationSuccess"
    except pymysql.Error as e:
        print(f"Failed to execute query: {e}")
        db.rollback()
        db.close()
        return "creationFailed"
    

def createDockerColumns(db_name,db_ip):
    # Open connection to database
    db = connectDB(db_name,db_ip)
    if db == False:
        return "connectionFailed"
    else:
        cursor=db.cursor()
    
    # Check if docker is installed
    try:
        subprocess.check_call(["docker", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError:
        print("Docker is not installed. Please install Docker and try again.")
        return "dockerNotInstalled"
        
    # Get the container names
    try:
        output = subprocess.check_output(["docker", "ps", "--format", "{{.Names}}"], stderr=subprocess.STDOUT)
        container_names = output.decode().split("\n")[:-1]
    except subprocess.CalledProcessError as e:
        print(f"Failed to get running containers: {e.output.decode()}")
        db.close()
        return "failedGetDockers"


    # Loop through the container names and add a column for each container to the database tables
    # print(container_names)
    container_names.sort()
    # print(container_names)
    for container_name in container_names:
        # Replace non-alphanumeric characters and . with underscores and to create a valid column name
        #column_name = container_name.replace("-", "_")
        column_name = container_name.replace("-", "_").replace(".", "_")
        # Check if the column already exists in cpumemoryusage table
        try:
            cursor.execute("SELECT '"+column_name+"' FROM cpumemoryusage LIMIT 1")
            if cursor.fetchone():
                print(f"Column {column_name} already exists in cpumemoryusage table. Skipping.")
            else:
                # Add the column to the cpumemoryusage table
                sql_query = f"ALTER TABLE cpumemoryusage ADD COLUMN `{column_name}` varchar(255)"
                cursor.execute(sql_query)
                db.commit()
                
        except pymysql.Error as e:
            print(f"Failed to add column {column_name} to cpumemoryusage table: {e}")
            db.rollback()
            db.close()
            return "creationFailed"

        # Check if the column already exists in cpuusage table
        try:
            cursor.execute("SELECT '"+column_name+"' FROM cpuusage LIMIT 1")
            if cursor.fetchone():
                print(f"Column {column_name} already exists in cpuusage table. Skipping.")
            else:
                # Add the column to the cpuusage table
                sql_query = f"ALTER TABLE cpuusage ADD COLUMN `{column_name}` varchar(255)"
                cursor.execute(sql_query)
                db.commit()
        except pymysql.Error as e:
            print(f"Failed to add column {column_name} to cpuusage table: {e}")
            db.rollback()
            db.close()
            return "creationFailed"
    # Close database connection
    db.close()
    print(f"All docker columns added to tables.")
    return "creationSuccess"