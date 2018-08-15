import os, sys
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
    print(observation_dirs)

    for obs_dir in scandir(dir_to_monitor):
        if obs_dir.is_dir(follow_symlinks=False):
            obs_dir_name = obs_dir.name
            taskID = obs_dir_name.replace("WSRTA", "")

            # create and POST an observation per directory if the observation is not already in the database

            id = atdb.do_GET_ID(key='observations:taskID', value=taskID)
            if int(id)<0:
                # only POST a new observations
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
                      payload = create_dataproduct_payload(taskID, dp_file_name)
                      atdb.do_POST(resource='dataproducts', payload=payload)


# atdb_data_monitor d:\my_datawriter http://localhost:8000/atdb/
# python atdb_data_monitor.py d:\my_datawriter http://192.168.22.22/atdb/
if __name__ == "__main__":
    monitor_dir(sys.argv[1], sys.argv[2])