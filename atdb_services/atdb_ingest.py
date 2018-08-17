import sys
import atdb_interface
import alta_interface

def create_ingest_parfile():
    s = "--host = alta.acc.icat.astron.nl\n"
    S =+ "--localDir = ~/early_science/ 180223003\n"
    s =+ "--irodsColl = apertif_main/visibilities_default/early_science /180223003\n"
    s = + "--size = 1504320322200\n"
    s = + "--ttl = 86400\n"

def start_auto_ingest(atdb_url, alta_url, old_status, new_status, username, password):
    atdb = atdb_interface.ATDB(atdb_url)

    # get the list taskID of 'valid' observations
    taskIDs =  atdb.do_GET_LIST(key='observations:taskID', query='my_status='+old_status)
    print(str(taskIDs))

    # loop through the list of 'valid' observations and gather its valid dataproducts,
    # by name, because that is the key that is used for the ingest.
    for taskID in taskIDs:
        dataproducts = atdb.do_GET_LIST(key='dataproducts:name', query='taskID='+taskID+'&my_status='+old_status)
        print(str(dataproducts))

    # connect to ALTA
    alta = alta_interface.ALTA(alta_url, username, password,True)


# example:
# atdb_ingest http://192.168.22.22/atdb/ http://localhost/altapi/
if __name__ == "__main__":
    atdb_url = 'http://192.168.22.22/atdb/'
    alta_url = 'http://localhost:8000/altapi/'
    old_status = 'valid'
    new_status = 'ingesting'
    username = 'vagrant'
    password = 'vagrant'

    start_auto_ingest(atdb_url, alta_url, old_status, new_status, username, password)
