import argparse
import databaseSetup as dbSetup
import serverRegistration as serverRegister

# Parse command line arguments
parser = argparse.ArgumentParser(description="Execute SQL queries on a database.")
parser.add_argument("database", type=str, help="Name of the database to execute queries on.")
parser.add_argument("cameralist", type=str, help="Comma-separated list of cameras.")
parser.add_argument("maindbhost", type=str, help="Host of the main database server")

args = parser.parse_args()
db_name = args.database
main_db_host = args.maindbhost
camera_name=args.cameralist
camera_list =camera_name[1:-1].split(',')

createDB = dbSetup.createDatabase(db_name,main_db_host)
if createDB == "connectionFailed" or createDB == "creationFailed" or createDB == "alreadyCreated":
    exit()
if createDB == "creationSuccess":
    createDefTab = dbSetup.createDefaultTables(db_name,main_db_host)
    if createDefTab == "connectionFailed" or createDefTab == "failedSqlFile" or createDefTab == "creationFailed":
        exit()
    if createDefTab == "creationSuccess":
        createDocTab = dbSetup.createDockerColumns(db_name,main_db_host)
        if createDocTab == "connectionFailed" or createDocTab == "dockerNotInstalled" or createDocTab == "failedGetDockers" or createDocTab == "creationFailed":
            exit()
        if createDocTab == "creationSuccess":
            #run serverinfo
            servRegst = serverRegister.addServerInfoToDB(db_name,camera_list,main_db_host)
