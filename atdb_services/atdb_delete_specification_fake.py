import sys
import atdb_interface

def delete_observation(taskID):
    host = 'http://localhost:8000/atdb'
    atdb = atdb_interface.ATDB(host)

    # find the observation
    id = atdb.do_GET_ID(key='observations.taskID', value=taskID)
    while (int(id)>0):
        print('delete observation : '+str(taskID)+ ' (id = '+str(id)+')')
        atdb.do_DELETE(resource='observations', id=id)
        # check for more
        id = atdb.do_GET_ID(key='observations.taskID', value=taskID)

    id = atdb.do_GET_ID(key='dataproducts.taskID', value=taskID)
    while (int(id)>0):
        print('delete dataproduct for taskID '+str(taskID)+ ' (id = '+str(id)+')')
        atdb.do_DELETE(resource='dataproducts', id=id)
        # check for more
        id = atdb.do_GET_ID(key='dataproducts.taskID', value=taskID)

    print('done')

# atdb_delete_observation_fake 180223003
if __name__ == "__main__":
    delete_observation(sys.argv[1])