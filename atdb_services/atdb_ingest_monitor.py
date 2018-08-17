import sys, time
import atdb_interface
import alta_interface


def check_arrival_in_alta(atdb_url, alta_url, old_status, new_status, username, password):
    # check if observations and dataproducts with status 'ingesting' if they have arrived in ALTA
    # if they do, then put the status on 'ingested'.
    atdb = atdb_interface.ATDB(atdb_url)
    alta = alta_interface.ALTA(alta_url, username, password, True)

    # get the list taskID of 'ingesting' observations
    taskIDs =  atdb.do_GET_LIST(key='observations:taskID', query='my_status='+old_status)
    print('Observations with status = '+old_status+' in ATDB: '+str(taskIDs))

    # connect to ALTA
    for taskID in taskIDs:
        alta_id = alta.do_GET_ID(key='activities:runId', value=taskID)
        print('Observation found in ALTA = '+str(alta_id))
        if (int(alta_id) > 0):
            # dataproduct was found in ALTA, put it on 'archived' in ATDB
            atdb.do_PUT(key='observations:new_status', id=None, taskid=taskID, value=new_status)

    # get the list taskID of 'ingesting' dataproducts
    names =  atdb.do_GET_LIST(key='dataproducts:name', query='my_status='+old_status)


    # connect to ALTA
    for name in names:
        alta_id  = alta.do_GET_ID(key='dataproducts:name', value=name)
        print('Dataproducts found in ALTA = '+str(id))
        if (int(alta_id)>0):
            # dataproduct was found in ALTA, put it on 'archived' in ATDB
            # get the ID of this dataproduct in atdb.
            atdb_id = atdb.do_GET_ID(key='dataproducts:name', value=name)
            print('set status of '+str(id)+' to '+new_status)
            atdb.do_PUT(key='dataproducts:new_status', id=atdb_id, taskid=None, value=new_status)


# example:
# atdb_ingest http://192.168.22.22/atdb/ http://localhost/altapi/
if __name__ == "__main__":
    interval_seconds = 60
    atdb_url = 'http://192.168.22.22/atdb/'
    alta_url = 'http://localhost:8000/altapi/'
    old_status = 'ingesting'
    new_status = 'archived'
    username = 'vagrant'
    password = 'vagrant'

    while True:
        check_arrival_in_alta(atdb_url, alta_url, old_status, new_status, username, password)
        print('sleep '+str(interval_seconds)+' secs')
        time.sleep(int(interval_seconds))