import sys
import atdb_interface

def change_status(url, search_field, status):

    # split host from resource
    s = url.split("atdb/")
    my_key = s[1] + '.new_status'
    host = s[0]+'atdb/'
    atdb = atdb_interface.ATDB(host)

    # id:27 or taskid:180223003
    field = search_field.split(':')

    if field[0]=='taskid':
        atdb.do_PUT(key=my_key, id=None, taskid=field[1], value=status)
    else:
        atdb.do_PUT(key=my_key, id=field[1], taskid=None, value=status)

# example:
# atdb_change_status http://localhost:8000/atdb/observations taskid:180223003 created
# atdb_change_status http://localhost:8000/atdb/dataproducts id:27 created
if __name__ == "__main__":
    change_status(sys.argv[1], sys.argv[2], sys.argv[3])