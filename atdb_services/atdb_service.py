#!/usr/bin/python3
import os, sys
import time
import atdb_interface
import alta_interface
from os import scandir
import argparse


"""
altapi.py : a commandline tool to inferface with the ATDB REST API.
:author Nico Vermaas - Astron
"""
VERSION = "1.0.0 (17 aug 2018)"

# ====================================================================

# The request header
ATDB_HEADER = {
    'content-type': "application/json",
    'cache-control': "no-cache",
    'authorization': "Basic YWRtaW46YWRtaW4="
}

DEFAULT_ATDB_HOST = "http://localhost:8000/atdb"
DEFAULT_ATDB_HOST = "http://192.168.22.22/atdb"
DEFAULT_ALTA_HOST = "http://localhost:8000/altapi"

TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

class ATDBException(Exception):
    """
    Exception with message.
    """
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class ATDBService:
    """
    ATDBService class. This class contains all the atdb services.
    """
    def __init__(self, host, alta_host, user, password,verbose=False):
        """
        Constructor.
        :param host: the host name of the backend.
        :param username: The username known in Django Admin.
        :param verbose: more information runtime.
        :param header: Request header for Atdb REST requests with token authentication.
        """
        self.host = host
        if (not self.host.endswith('/')):
            self.host += '/'

        self.alta_host = alta_host
        if (not self.alta_host.endswith('/')):
            self.alta_host += '/'

        self.verbose = verbose
        self.header = ATDB_HEADER
        self.user = user
        self.password = password
        self.atdb_interface = atdb_interface.ATDB(self.host, self.verbose)

        try:
            self.alta_interface = alta_interface.ALTA(self.alta_host,self.user,self.password, self.verbose)
        except:
            print("ERROR: No connection to ALTA could be made on "+self.alta_host+". Continuing without ALTA connection.")
            print("Warning: ingest_monitor will not work, status will appear to stay on 'ingesting' until connection with ALTA is restored.")

    def verbose_print(self, info_str):
        """
        Print info string if verbose is enabled (default False)
        :param info_str: String to print
        """
        if self.verbose:
            print(info_str)

    def get_taskID(self, obs_dir_name):
        """
        Extract a taskID from a directory name. WSRTA180817001.MS => 180817001
        :param obs_dir_name: Observation directory name
        """
        taskID = obs_dir_name.replace("WSRTA", "")
        if taskID.find('.')>=0:
            s = taskID.split('.')
            taskID = s[0]

        return taskID

    def create_obs_payload(self, taskID, obs_dir_name, status):
        payload = "{name:" + obs_dir_name + ','
        payload += "taskID:" + taskID + ','
        payload += "task_type:observation" + ','
        payload += "new_status:"+status
        payload += "}"
        return payload

    def create_dataproduct_payload(self, taskID, db_file_name, status):
        payload = "{name:" + str(db_file_name) + ','
        payload += "taskID:" + str(taskID) + ','
        payload += "filename:" + db_file_name + ','
        payload += "description:" + db_file_name + ','
        payload += "size:11111" + ','
        payload += "quality:?" + ','
        payload += "new_status:"+status
        payload += "}"
        return payload

    # ------------------------------------------------------------------------------#
    #                                Main Services                                  #
    # ------------------------------------------------------------------------------#

    def add_fake(self,taskid, count, status):

        # add 1 observation
        payload = "{name:M51 Early Science Dataset" + ','
        payload += "taskID:" + str(taskid) + ','
        payload += "task_type:observation" + ','
        payload += "new_status:"+status
        payload += "}"

        print('adding observation : ' + str(taskid))

        self.atdb_interface.do_POST(resource='observations', payload=payload)

        # add 5 dataproducts
        for i in range(int(count)):
            filename = 'WSRTA' + str(taskid) + '_B' + str(i).zfill((3)) + '.MS'
            print(filename)

            payload = "{name:" + filename + ','
            payload += "taskID:" + str(taskid) + ','
            payload += "filename:" + filename + ','
            payload += "description:" + filename + ','
            payload += "size:39587376900" + ','
            payload += "quality:?" + ','
            payload += "new_status:"+status
            payload += "}"

            print('- adding dataproduct : ' + str(filename))
            self.atdb_interface.do_POST(resource='dataproducts', payload=payload)

    # --------------------------------------------------------------------------------------------------------
    # TODO: extend to search for MS (dirs), the prototype now only searches for FITS (files)
    def service_data_monitor(self, dir_to_monitor):
        """
        Monitor a data directory. Check for new Observations (directories) and Dataproducts (directories or filenames)
        :param dir_to_monitor: Directory to monitor for new data
        """

        # check for directories per observation
        observation_dirs = os.listdir(dir_to_monitor)

        for obs_dir in scandir(dir_to_monitor):
            if obs_dir.is_dir(follow_symlinks=False):
                obs_dir_name = obs_dir.name
                taskID = obs_dir_name.replace("WSRTA", "")

                # create and POST an observation per directory if the observation is not already in the database

                id = self.atdb_interface.do_GET_ID(key='observations:taskID', value=taskID)
                if int(id) < 0:
                    # only POST a new observations
                    self.verbose_print('add observation ' + obs_dir_name + ' to ATDB...')
                    payload = self.create_obs_payload(taskID, obs_dir_name,"created")
                    self.atdb_interface.do_POST(resource='observations', payload=payload)

                # scan for dataproducts in the observation directory
                new_dir_to_monitor = os.path.join(dir_to_monitor, obs_dir_name)

                for dp in scandir(new_dir_to_monitor):
                    if dp.is_file() and dp.name.endswith("FITS"):
                        dp_file_name = dp.name
                        id = self.atdb_interface.do_GET_ID(key='dataproducts:filename', value=dp_file_name)
                        if int(id) < 0:
                            # only POST a new dataproducts
                            self.verbose_print('- add dataproduct ' + dp_file_name + ' to ATDB...')
                            payload = self.create_dataproduct_payload(taskID, dp_file_name, "created")
                            self.atdb_interface.do_POST(resource='dataproducts', payload=payload)

    # --------------------------------------------------------------------------------------------------------
    def service_ingest_monitor(self, dir_to_monitor, old_status, new_status):
        # check if observations and dataproducts with status 'ingesting' if they have arrived in ALTA
        # if they do, then put the status on 'ingested'.

        # get the list taskID of 'ingesting' observations
        taskIDs = self.atdb_interface.do_GET_LIST(key='observations:taskID', query='my_status=' + old_status)
        self.verbose_print('Observations with status = ' + old_status + ' in ATDB: ' + str(taskIDs))

        # connect to ALTA
        for taskID in taskIDs:
            alta_id = self.alta_interface.do_GET_ID(key='activities:runId', value=taskID)
            self.verbose_print('Observation found in ALTA = ' + str(alta_id))
            if (int(alta_id) > 0):
                # dataproduct was found in ALTA, put it on 'archived' in ATDB
                self.atdb_interface.do_PUT(key='observations:new_status', id=None, taskid=taskID, value=new_status)

        # get the list of names of 'ingesting' dataproducts
        names = self.atdb_interface.do_GET_LIST(key='dataproducts:name', query='my_status=' + old_status)

        # connect to ALTA.
        for name in names:
            # get the alta_id of the dataproduct
            alta_id = self.atdb_interface.do_GET_ID(key='dataproducts:name', value=name)
            self.verbose_print('Dataproducts found in ALTA = ' + str(id))

            # check if this dataproduct has already arrived in ALTA..
            if (int(alta_id) > 0):
                # ... if it has arrived in ALTA then put it on 'archived' in ATDB
                # get the atdb_id of this dataproduct
                atdb_id = self.atdb_interface.do_GET_ID(key='dataproducts:name', value=name)
                self.verbose_print('set status of ' + str(id) + ' to ' + new_status)
                self.atdb_interface.do_PUT(key='dataproducts:new_status', id=atdb_id, taskid=None, value=new_status)

# --------------------------------------------------------------------------------------------------------
    # example: change status of observation with taskid=180223003 to valid.
    # change_status('observations','taskid:180223003','valid'
    def service_change_status(self, resource, search_key, status):

        my_key = resource + ':new_status'   # observations:new_status

        # id:27 or taskid:180223003
        params = search_key.split(':')
        search_field = params[0]            # taskid
        search_value = params[1]            # 180223003

        if search_field=='taskid':
            if my_key.startswith('observations'):
                self.atdb_interface.do_PUT(key=my_key, id=None, taskid=search_value, value=status)
            if  my_key.startswith('dataproducts'):
                self.atdb_interface.do_PUT_LIST(key=my_key, taskid=search_value, value=status)
        else:
            self.atdb_interface.do_PUT(key=my_key, id=search_value, taskid=None, value=status)

# --------------------------------------------------------------------------------------------------------
    #TODO: finish
    def service_auto_ingest(self,old_status, new_status):

        # get the list taskID of 'valid' observations
        taskIDs = self.atdb_interface.do_GET_LIST(key='observations:taskID', query='my_status=' + old_status)
        self.verbose_print(str(taskIDs))

        # loop through the list of 'valid' observations and gather its valid dataproducts,
        # by name, because that is the key that is used for the ingest.
        for taskID in taskIDs:
            self.atdb_interface.do_PUT(key='observations:new_status', id=None, taskid=taskID, value=new_status)

            ids = self.atdb_interface.do_GET_LIST(key='dataproducts:id',
                                            query='taskID=' + taskID + '&my_status=' + old_status)
            self.verbose_print(str(ids))
            for id in ids:
                self.atdb_interface.do_PUT(key='dataproducts:new_status', id=id, taskid=None, value=new_status)


        # create the ingest parameter file
        # TODO: move the invalid dataproducts away? rename them so that the ingest doesn't recognize them?

# --------------------------------------------------------------------------------------------------------
    def service_delete_taskid(self, taskid):

        # find the observation
        id = self.atdb_interface.do_GET_ID(key='observations:taskID', value=taskid)
        while (int(id) > 0):
            print('delete observation : ' + str(taskid) + ' (id = ' + str(id) + ')')
            self.atdb_interface.do_DELETE(resource='observations', id=id)
            # check for more
            id = self.atdb_interface.do_GET_ID(key='observations:taskID', value=taskid)

        id = self.atdb_interface.do_GET_ID(key='dataproducts:taskID', value=taskid)
        while (int(id) > 0):
            print('delete dataproduct for taskID ' + str(taskid) + ' (id = ' + str(id) + ')')
            self.atdb_interface.do_DELETE(resource='dataproducts', id=id)
            # check for more
            id = self.atdb_interface.do_GET_ID(key='dataproducts:taskID', value=taskid)

# ------------------------------------------------------------------------------#
#                                Module level functions                         #
# ------------------------------------------------------------------------------#
def exit_with_error(message):
    """
    Exit the code for an error.
    :param message: the message to print.
    """
    print("EXCEPTION RAISED: ")
    print(message)
    sys.exit(-1)


# ------------------------------------------------------------------------------#
#                                Main                                           #
# ------------------------------------------------------------------------------#


def main():
    """
    The main module.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-v","--verbose", default=False, help="More information at run time.",action="store_true")
    parser.add_argument("--atdb_host", nargs="?", default=DEFAULT_ATDB_HOST, help= "Production = https://atdb.astron.nl/atdb/, Test = https://192.168.22.22/atdb, Development (default) = http://localhost:8000/atdb")
    parser.add_argument("--alta_host", nargs="?", default=DEFAULT_ALTA_HOST, help="Production = https://alta.astron.nl/altapi/, Acceptance = https://alta-acc.astron.nl/altapi, Development (default) = http://localhost:8000/altapi")
    parser.add_argument("-u","--user", nargs="?", default='vagrant', help="Username.")
    parser.add_argument("-p", "--password", nargs="?", default='vagrant', help="Password.")
    parser.add_argument("--version", default=False, help="Show current version of this program, and the version of the ALTA backend.", action="store_true")
    parser.add_argument("--operation","-o", default="data-monitor", help="options are: data_monitor, ingest_monitor, ingest, add_fake, delete_taskid, change_status, validate, cleanup")
    parser.add_argument("--resource","-r", default='observations', help="observations or dataproducts")
    parser.add_argument("--search_key", "-k", default='taskid:180223003', help="Search key used for various services")
    parser.add_argument("--taskid", nargs="?", default=None, help="Optional taskID which can be used instead of '--id' to lookup Observations or Dataproducts.")
    parser.add_argument("--status", default="valid", help="status to be set by the set-status operation")
    parser.add_argument("--count", default="37", help="Number of (fake) dataproducts to add.")
    parser.add_argument("--show_examples", "-e", default=False, help="Show some examples",action="store_true")

    parser.add_argument("--interval", default=None, help="Polling interval in seconds. When enabled this instance of the program will run in monitoring mode.")
    parser.add_argument("--dir", default=None, help="Data Directory to monitor")

    args = parser.parse_args()
    try:
        atdb_service = ATDBService(args.atdb_host, args.alta_host, args.user, args.password, args.verbose)

        print('starting '+args.operation+'...')

        if (args.show_examples):

            print('atdb_service.py version = '+VERSION)
            print('--------------------------------------------------------------')
            print()
            print('--- Examples --- ')
            print()
            print("Start the DataMonitor for directory '~/my_datawriter' and let it check for new data every minute")
            print(">python atdb_service.py -o data_monitor --dir ~/my_datawriter --interval 60")
            print()
            print("Start the IngestMonitor and let it check for finished ingests every minute")
            print(">python atdb_service.py -o ingest_monitor --interval 60")
            print()
            print("Start (auto) ingest. This service will look for 'valid' tasks and dataproducts and starts the ingest to ALTA")
            print(">python atdb_service.py -o ingest --interval 60")
            print()
            print("Change status of all dataproducts with taskid=180223003 to valid")
            print(">python atdb_service.py -o change_status --resource dataproducts --search_key taskid:180223003_IMG --status valid")
            print()
            print("Change status of 1 dataproduct with id=55 to invalid")
            print(">python atdb_service.py -o change_status --resource dataproducts --search_key id:55 --status invalid")
            print()
            print("Change status of observation with taskid=180223003 to valid")
            print("WARNING: this starts the Ingest of this Observation and all its 'valid' dataproducts ")
            print(">python atdb_service.py -o change_status --resource observations --search_key taskid:180223003_IMG --status valid")
            print()
            print("For test purposes: Add a fake Observation 180817001 with 37 Dataproducts")
            print(">python atdb_service.py -o add_fake --taskid 180817001 --count 37 --status created")
            print()
            print("Delete Observation and DataProducts for taskid 180223003_IMG (from the ATDB database only)")
            print(">python atdb_service.py -o delete_taskid --taskid 180223003_IMG")
            print()
            print('--------------------------------------------------------------')
            return

        # --------------------------------------------------------------------------------------------------------
        if (args.operation=='add_fake'):
            atdb_service.add_fake(taskid=args.taskid, count=args.count, status=args.status)

        # --------------------------------------------------------------------------------------------------------
        if (args.operation=='data_monitor'):
            if not args.dir:
                print("ERROR: --dir is requied for 'data_monitor'")
                return

            atdb_service.service_data_monitor(dir_to_monitor=args.dir)
            if args.interval:
                print('starting polling ' + atdb_service.host + ' every ' + args.interval + ' secs')
                while True:
                    atdb_service.service_data_monitor(dir_to_monitor=args.dir)
                    print('sleep ' + args.interval + ' secs')
                    time.sleep(int(args.interval))

        # --------------------------------------------------------------------------------------------------------
        if (args.operation=='ingest_monitor'):
            atdb_service.service_ingest_monitor(dir_to_monitor=args.dir,old_status='ingesting',new_status='archived')
            if args.interval:
                print('starting polling ' + atdb_service.host + ' every ' + args.interval + ' secs')
                while True:
                    atdb_service.service_ingest_monitor(dir_to_monitor=args.dir,old_status='ingesting',new_status='archived')
                    print('sleep ' + args.interval + ' secs')
                    time.sleep(int(args.interval))

        # --------------------------------------------------------------------------------------------------------
        if (args.operation == 'ingest'):
            atdb_service.service_auto_ingest(old_status='valid', new_status='ingesting')
            if args.interval:
                print('starting polling ' + atdb_service.host + ' every ' + args.interval + ' secs')
                while True:
                    atdb_service.service_auto_ingest(old_status='valid', new_status='ingesting')
                    print('sleep ' + args.interval + ' secs')
                    time.sleep(int(args.interval))

        # --------------------------------------------------------------------------------------------------------
        if (args.operation=='change_status'):
            atdb_service.service_change_status(resource=args.resource, search_key=args.search_key, status=args.status)

        # --------------------------------------------------------------------------------------------------------
        if (args.operation=='delete_taskid'):
            atdb_service.service_delete_taskid(taskid=args.taskid)


    except ATDBException as exp:
        exit_with_error(exp.message)

    print('done')
    sys.exit(0)


if __name__ == "__main__":
    main()

