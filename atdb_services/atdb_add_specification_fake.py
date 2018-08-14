import sys
import atdb_interface

def add_observation(taskID, nrDataProducts):
    host = 'http://localhost:8000/atdb'
    atdb = atdb_interface.ATDB(host)

    # add 1 observation
    payload = "{name:M51 Early Science Dataset"+ ','
    payload += "taskID:" + str(taskID) + ','
    payload += "task_type:observation"+ ','
    payload += "new_status:defined"
    payload += "}"

    print('adding observation : '+str(taskID))

    atdb.do_POST(resource='observations', payload=payload)

    # add 5 dataproducts
    for i in range(int(nrDataProducts)):
        filename = 'WSRTA'+ str(taskID) + '_B' +  str(i).zfill((3))+'.MS'
        print(filename)

        payload = "{name:"+filename+','
        payload += "taskID:"+str(taskID)+','
        payload += "filename:"+filename+','
        payload += "description:"+filename+','
        payload += "size:39587376900"+','
        payload += "quality:?"+','
        payload += "new_status:defined"
        payload += "}"

        print('- adding dataproduct : ' + str(filename))
        atdb.do_POST(resource='dataproducts', payload=payload)

# atdb_add_observation_fake 180223003 5
if __name__ == "__main__":
    add_observation(sys.argv[1], sys.argv[2])