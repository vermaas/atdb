import os, sys
import time
import atdb_interface
from os import scandir

def get_taskID(obs_dir_name):
    taskID = obs_dir_name.replace("WSRTA", "")
    return taskID

def create_obs_payload(taskID, obs_dir_name):
    payload = "{name:"+ obs_dir_name+','
    payload += "taskID:" + taskID + ','
    payload += "task_type:observation"+ ','
    payload += "new_status:created"
    payload += "}"
    return payload

def create_dataproduct_payload(taskID, db_file_name):
    payload = "{name:" + str(db_file_name) + ','
    payload += "taskID:" + str(taskID) + ','
    payload += "filename:" + db_file_name + ','
    payload += "description:" + db_file_name + ','
    payload += "size:11111" + ','
    payload += "quality:?" + ','
    payload += "new_status:created"
    payload += "}"
    return payload

def monitor_dir(dir_to_monitor,host):
    atdb = atdb_interface.ATDB(host)

    # check for directories per observation
    observation_dirs = os.listdir(dir_to_monitor)

    for obs_dir in scandir(dir_to_monitor):
        if obs_dir.is_dir(follow_symlinks=False):
            obs_dir_name = obs_dir.name
            taskID = obs_dir_name.replace("WSRTA", "")

            # create and POST an observation per directory if the observation is not already in the database

            id = atdb.do_GET_ID(key='observations:taskID', value=taskID)
            if int(id)<0:
                # only POST a new observations
                print('add observation '+obs_dir_name+' to ATDB...')
                payload = create_obs_payload(taskID, obs_dir_name)
                atdb.do_POST(resource='observations', payload=payload)

            # scan for dataproducts in the observation directory
            new_dir_to_monitor = os.path.join(dir_to_monitor,obs_dir_name)

            for dp in scandir(new_dir_to_monitor):
                if dp.is_file() and dp.name.endswith("FITS"):
                    dp_file_name = dp.name
                    id = atdb.do_GET_ID(key='dataproducts:filename', value=dp_file_name)
                    if int(id) < 0:
                      # only POST a new dataproducts
                      print('- add dataproduct ' + dp_file_name + ' to ATDB...')
                      payload = create_dataproduct_payload(taskID, dp_file_name)
                      atdb.do_POST(resource='dataproducts', payload=payload)


# python atdb_data_monitor.py d:\my_datawriter 60 http://localhost:8000/atdb/
# python atdb_data_monitor.py d:\my_datawriter 30 http://192.168.22.22/atdb/
if __name__ == "__main__":
    dir_to_monitor = sys.argv[1]
    interval_seconds = sys.argv[2]
    host = sys.argv[3]

    while True:
        monitor_dir(dir_to_monitor, host)
        print('sleep '+interval_seconds+' secs')
        time.sleep(int(interval_seconds))

