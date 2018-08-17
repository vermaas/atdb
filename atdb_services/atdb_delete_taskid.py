import sys
import atdb_interface

def delete_taskid(taskID, host):
    atdb = atdb_interface.ATDB(host)

    # find the observation
    id = atdb.do_GET_ID(key='observations:taskID', value=taskID)
    while (int(id)>0):
        print('delete observation : '+str(taskID)+ ' (id = '+str(id)+')')
        atdb.do_DELETE(resource='observations', id=id)
        # check for more
        id = atdb.do_GET_ID(key='observations:taskID', value=taskID)

    id = atdb.do_GET_ID(key='dataproducts:taskID', value=taskID)
    while (int(id)>0):
        print('delete dataproduct for taskID '+str(taskID)+ ' (id = '+str(id)+')')
        atdb.do_DELETE(resource='dataproducts', id=id)
        # check for more
        id = atdb.do_GET_ID(key='dataproducts:taskID', value=taskID)

    print('done')

# python atdb_delete_taskid.py 180223003 http://localhost:8000/atdb
# python atdb_delete_taskid.py 180223003_IMG http://192.168.22.22/atdb
if __name__ == "__main__":
    delete_taskid(sys.argv[1], sys.argv[2])