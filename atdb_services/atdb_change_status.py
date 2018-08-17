import sys
import atdb_interface

def change_status(url, search_key, new_status_value):

    # split host from resource
    s = url.split("atdb/")
    my_key = s[1] + ':new_status'       # observations:new_status
    host = s[0]+'atdb/'                 # http://localhost:8000/atdb/
    atdb = atdb_interface.ATDB(host)

    # id:27 or taskid:180223003
    params = search_key.split(':')
    search_field = params[0]            # taskid
    search_value = params[1]            # 180223003

    if search_field=='taskid':
        if my_key.startswith('observations'):
            atdb.do_PUT(key=my_key, id=None, taskid=search_value, value=new_status_value)
        if  my_key.startswith('dataproducts'):
            atdb.do_PUT_LIST(key=my_key, taskid=search_value, value=new_status_value)
    else:
        atdb.do_PUT(key=my_key, id=search_value, taskid=None, value=new_status_value)

# example:
# atdb_change_status http://localhost:8000/atdb/observations taskid:180223003 created
# atdb_change_status http://localhost:8000/atdb/dataproducts id:27 created
# atdb_change_status http://localhost:8000/atdb/dataproducts taskid:180223003 created
if __name__ == "__main__":
    url = sys.argv[1]
    search_key =  sys.argv[2]
    new_status_value =  sys.argv[3]
    change_status(url, search_key, new_status_value)