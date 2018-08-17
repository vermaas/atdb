#!/usr/bin/python3
import os, sys
import time
import atdb_interface
from os import scandir
import argparse


"""
altapi.py : a commandline tool to inferface with the ATDB REST API.
:author Nico Vermaas - Astron
"""
VERSION = "1.0.0 (13 aug 2018)"

# ====================================================================

# The request header
ATDB_HEADER = {
    'content-type': "application/json",
    'cache-control': "no-cache",
    'authorization': "Basic YWRtaW46YWRtaW4="
}

DEFAULT_ATDB_HOST = "http://localhost:8000/atdb/"
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
    Calibrators class, use to parse SIP and update the backend database
    through REST API calls.
    """
    def __init__(self, host, verbose=False):
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

        self.verbose = verbose
        self.header = ATDB_HEADER
        self.atdb_interface = atdb_interface.ATDB(self.host)

    def verbose_print(self, info_str):
        """
        Print info string if verbose is enabled (default False)
        :param info_str: String to print
        """
        if self.verbose:
            print(info_str)

    def get_taskID(self, obs_dir_name):
        taskID = obs_dir_name.replace("WSRTA", "")
        return taskID

    def create_obs_payload(self, taskID, obs_dir_name):
        payload = "{name:" + obs_dir_name + ','
        payload += "taskID:" + taskID + ','
        payload += "task_type:observation" + ','
        payload += "new_status:created"
        payload += "}"
        return payload

    def create_dataproduct_payload(self, taskID, db_file_name):
        payload = "{name:" + str(db_file_name) + ','
        payload += "taskID:" + str(taskID) + ','
        payload += "filename:" + db_file_name + ','
        payload += "description:" + db_file_name + ','
        payload += "size:11111" + ','
        payload += "quality:?" + ','
        payload += "new_status:created"
        payload += "}"
        return payload

    # ------------------------------------------------------------------------------#
    #                                Main Services                                  #
    # ------------------------------------------------------------------------------#

    def service_data_monitor(self, dir_to_monitor):

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
                    payload = self.create_obs_payload(taskID, obs_dir_name)
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
                            payload = self.create_dataproduct_payload(taskID, dp_file_name)
                            self.atdb_interface.do_POST(resource='dataproducts', payload=payload)




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
    parser.add_argument("--atdb_host", nargs="?", default=DEFAULT_ATDB_HOST, help= "Production = https://atdb.astron.nl/atdb/, Test = https://192.168.22.22/atdb, Development (default) = http://localhost:8000/atdb/")
    parser.add_argument("--version", default=False, help="Show current version of this program, and the version of the ALTA backend.", action="store_true")
    parser.add_argument("--operation","-o", default="data-monitor", help="options are: data_monitor, ingest_monitor, ingest, add, delete, set_status, validate, cleanup")
    parser.add_argument("--id", default=None, help="id of the object to PUT to.")
    parser.add_argument("-t", "--taskid", nargs="?", default=None, help="Optional taskID which can be used instead of '--id' to lookup Observations or Dataproducts.")
    parser.add_argument("--status", default="valid", help="status to be set by the set-status operation")
    parser.add_argument("--query", "-q", default="taskID=180223003", help="Query to the REST API")
    parser.add_argument("--value", default="", help="value to PUT in the resource.field. If omitted it will PUT the object without changing values, but the built-in 'signals' will be triggered.")
    parser.add_argument("--show_examples", "-e", default=False, help="Show some examples",action="store_true")

    parser.add_argument("--interval", default=None, help="Polling interval in seconds. When enabled this instance of the program will run in monitoring mode.")
    parser.add_argument("--dir", default=None, help="Data Directory to monitor")

    args = parser.parse_args()
    try:
        atdb_service = ATDBService(args.atdb_host, args.verbose)
        print('starting '+args.operation+'...')

        if (args.show_examples):

            print('atdb_service.py version = '+VERSION)
            print('---------------------------------------------------------------------------------------------')
            print()
            print('--- basic examples --- ')
            print()
            print("Show the 'status' for Observation with taskID 180720003")
            print("> python atdb_interface.py -o GET --key observations:my_status --taskid 180223003")
            print()

            print('---------------------------------------------------------------------------------------------')
            return

        if (args.operation=='data_monitor'):
            atdb_service.service_data_monitor(dir_to_monitor=args.dir)
            if args.interval:
                print('starting polling ' + atdb_service.host + ' every ' + args.interval + ' secs')
                while True:
                    atdb_service.service_data_monitor(dir_to_monitor=args.dir)
                    print('sleep ' + args.interval + ' secs')
                    time.sleep(int(args.interval))



    except ATDBException as exp:
        exit_with_error(exp.message)

    print('done')
    sys.exit(0)


if __name__ == "__main__":
    main()

