#!/usr/bin/python3
import sys
import requests
import json
import argparse
from datetime import *

"""
atdb_interface.py : a commandline tool to inferface with the ATDB REST API.
:author Nico Vermaas - Astron
"""
VERSION = "0.1.0 (17 aug 2018)"

# ====================================================================

# The request header
ATDB_HEADER = {
    'content-type': "application/json",
    'cache-control': "no-cache",
    'authorization': "Basic YWRtaW46YWRtaW4="
}

DEFAULT_BACKEND_HOST = "http://localhost:8000/atdb/"
TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

class ATDBException(Exception):
    """
    Exception with message.
    """
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class ATDB:
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

    def verbose_print(self, info_str):
        """
        Print info string if verbose is enabled (default False)
        :param info_str: String to print
        """
        if self.verbose:
            print(info_str)

    # === Backend requests ================================================================================
    def jsonifyPayload(self, payload):
        """
        {name:WSRTA180223003_B003.MS,filename:WSRTA180223003_B003.MS} =>
        {"name" : "WSRTA180223003_B003.MS" , "filename" : "WSRTA180223003_B003.MS"}
        :param payload:
        :return: payload_string
        """

        payload_string = str(payload).replace("{","{\"")
        payload_string = payload_string.replace("}", "\"}")
        payload_string = payload_string.replace(":", "\" : \"")
        payload_string = payload_string.replace(",", "\" , \"")
        #payload_string = payload_string.replace(",", ",\n")

        # reconstruct the lists by moving the brackets outside the double quotes
        payload_string = payload_string.replace("\"[", "[\"")
        payload_string = payload_string.replace("]\"", "\"]")
        payload_string = payload_string.replace("/,", "/\",\"")
        payload_string = payload_string.replace("u\"", "\"")

        self.verbose_print("payload_string: [" + payload_string+"]")
        return payload_string

    def encodePayload(self, payload):
        """

        The POST body does not simply accept a payload dict, it needs to be translated to a string with some
        peculiarities
        :param payload:
        :return: payload_string
        """

        payload_string = str(payload).replace("'","\"")
        #payload_string = payload_string.replace(",", ",\n")

        # reconstruct the lists by moving the brackets outside the double quotes
        payload_string = payload_string.replace("\"[", "[\"")
        payload_string = payload_string.replace("]\"", "\"]")
        payload_string = payload_string.replace("/,", "/\",\"")
        payload_string = payload_string.replace("u\"", "\"")

        self.verbose_print("The payload_string: [" + payload_string+"]")
        return payload_string


    def GET_TaskObjectByTaskId(self, resource, taskid):
        """
        Do a http GET request to the alta backend to find the Observation with the given runId
        :runId runId:
        """

        url = self.host + resource
        # create the querystring, external_ref is the mapping of this element to the alta datamodel lookup field
        querystring = {"taskID": taskid}

        response = requests.request("GET", url, headers=self.header, params=querystring)
        self.verbose_print("[GET " + response.url + "]")

        try:
            results = json.loads(response.text)
            taskobject = results[0]
            return taskobject
        except:
            raise (ATDBException("ERROR: " + response.url + " not found."))

    # ------------------------------------------------------------------------------#
    #                                Main User functions                            #
    # ------------------------------------------------------------------------------#


    def do_GET_ID(self, key, value):
        """
        Get the id based on a field value of a resource. This is a generic way to retrieve the id.
        :param resource: contains the resource, for example 'observations', 'dataproducts'
        :param field: the field to search on, this will probably be 'name' or 'filename'
        :param value: the value of the 'field' to search on.
        :return id
        """

        # split key in resource and field
        params = key.split(":")
        resource = params[0]
        field = params[1]

        url = self.host + resource + "?" + field + "=" + value
        response = requests.request("GET", url, headers=self.header)
        self.verbose_print("[GET " + response.url + "]")
        self.verbose_print("Response: " + str(response.status_code) + ", " + str(response.reason))

        try:
            my_json = json.loads(response.text)
            result = my_json[0]
            id = result['id']
            return id
        except:
            return '-1'
            #raise (ATDBException("ERROR: " + response.url + " not found."))


    def do_GET(self, key, id, taskid, value):
        """
        Do a http GET request to the ATDB backend to find the value of one field of an object
        :param key: contains the name of the resource and the name of the field separated by a colon.
        :param id: the database id of the object.
        :param taskid (optional): when the taskid (of an activity) is known it can be used instead of id.
        """

        # split key in resource and field
        params = key.split(":")
        resource = params[0]
        field = params[1]

        if taskid!=None:
            taskObject = self.GET_TaskObjectByTaskId(resource, taskid)
            id = taskObject['id']

        if id==None:
            # give up and throw an exception.
            raise (ATDBException("ERROR: no valid 'id' or 'taskid' provided"))

        url = self.host + resource + "/" + str(id) + "/"
        self.verbose_print(('url: ' + url))

        response = requests.request("GET", url, headers=self.header)
        self.verbose_print("[GET " + response.url + "]")
        self.verbose_print("Response: " + str(response.status_code) + ", " + str(response.reason))

        try:
            results = json.loads(response.text)
            value = results[field]
            return value
        except:
            raise (ATDBException("ERROR: " + response.url + " not found."))


    #  python atdb_interface.py -o GET_LIST --key observations:taskID --query status=valid
    def do_GET_LIST(self, key, query):
        """
        Do a http GET request to the ATDB backend to find the value of one field of an object
        :param key: contains the name of the resource and the name of the field separated by a dot.
        :param id: the database id of the object.
        :param taskid (optional): when the taskid (of an activity) is known it can be used instead of id.
        """

        # split key in resource and field
        params = key.split(":")
        resource = params[0]
        field = params[1]

        url = self.host + resource + "?" + str(query)
        self.verbose_print(('url: ' + url))

        response = requests.request("GET", url, headers=self.header)
        self.verbose_print("[GET " + response.url + "]")
        self.verbose_print("Response: " + str(response.status_code) + ", " + str(response.reason))

        try:
            results = json.loads(response.text)
            # loop through the list of results and extract the requested field (probably taskID),
            # and add it to the return list.
            list = []
            for result in results:
                value = result[field]
                list.append(value)

            return list
        except:
            raise (ATDBException("ERROR: " + str(response.status_code) + ", " + str(response.reason)))


    def do_PUT(self, key, id, value, taskid):
        """
        PUT a value to an existing field of a resource (table).
        :param key: contains the name of the resource and the name of the field separated by a dot. observations.description
        :param id: the database id of the object.
        :param value: the value that has to be PUT in the key. If omitted, an empty put will be done to trigger the signals.
        :param taskid (optional): when the taskid of an observation is known it can be used instead of id.
        """

        # split key in resource and field
        if key.find(':')>0:
            params = key.split(":")
            resource = params[0]
            field = params[1]
        else:
            resource = key
            field = None

        if taskid!=None:
            taskObject = self.GET_TaskObjectByTaskId(resource, taskid)
            id = taskObject['id']

        url = self.host + resource + "/" + str(id) + "/"
        self.verbose_print(('url: ' + url))
        if id==None:
            raise (ATDBException("ERROR: no valid 'id' or 'taskid' provided"))

        payload = {}
        if field!=None:
            payload[field]=value
            payload = self.encodePayload(payload)
        try:
            response = requests.request("PUT", url, data=payload, headers=self.header)
            self.verbose_print("[PUT " + response.url + "]")
            self.verbose_print("Response: " + str(response.status_code) + ", " + str(response.reason))
        except:
            raise (ATDBException("ERROR: " + str(response.status_code) + ", " + str(response.reason)))


    # do_PUT_LIST(key = observations:new_status, taskid = 180223003, value = valid)
    def do_PUT_LIST(self, key, taskid, value):
        """
        PUT a value to an existing field of  resource (table).
        :param key: contains the name of the resource and the name of the field separated by a colon. observations:new_status
        :param value: the value that has to be PUT in the key. If omitted, an empty put will be done to trigger the signals.
        :param taskid: the value is PUT to all objects with the provided taskid
        """

        # split key in resource and field
        if key.find(':')>0:
            params = key.split(":")
            resource = params[0]
            field = params[1]
        else:
            resource = key
            field = None

        get_key = resource+':id'
        get_query= 'taskID='+taskid
        ids = self.do_GET_LIST(get_key,get_query)

        for id in ids:
            url = self.host + resource + "/" + str(id) + "/"
            self.verbose_print(('url: ' + url))

            payload = {}
            if field!=None:
                payload[field]=value
                payload = self.encodePayload(payload)
            try:
                response = requests.request("PUT", url, data=payload, headers=self.header)
                self.verbose_print("[PUT " + response.url + "]")
                self.verbose_print("Response: " + str(response.status_code) + ", " + str(response.reason))
            except:
                raise (ATDBException("ERROR: " + str(response.status_code) + ", " + str(response.reason)))


    def do_POST(self, resource, payload):
        """
        PUT a value to an existing field of a resource (table).
        :param key: contains the name of the resource and the name of the field separated by a dot. observations.description
        :param id: the database id of the object.
        :param value: the value that has to be PUT in the key. If omitted, an empty put will be done to trigger the signals.
        :param taskid (optional): when the taskid of an observation is known it can be used instead of id.
        """

        url = self.host + resource + '/'
        self.verbose_print(('url: ' + url))
        self.verbose_print(('payload: ' + payload))

        payload = self.jsonifyPayload(payload)
        try:
            response = requests.request("POST", url, data=payload, headers=self.header)
            self.verbose_print("[POST " + response.url + "]")
            self.verbose_print("Response: " + str(response.status_code) + ", " + str(response.reason))
        except:
            raise (ATDBException("ERROR: " + str(response.status_code) + ", " + str(response.reason)))


    def do_DELETE(self, resource, id):
        """
        Do a http DELETE request to the ATDB backend
        """
        if id == None:
            raise (ATDBException("ERROR: no valid 'id' provided"))

        # if a range of ID's is given then do multiple deletes
        if (str(id).find('..')>0):
            self.verbose_print("Deleting " + str(id) + "...")
            s = id.split('..')
            start = int(s[0])
            end = int(s[1]) + 1
        else:
            # just a single delete
            start = int(id)
            end = int(id) + 1

        for i in range(start,end):
            url = self.host + resource + "/" + str(i) + "/"

            try:
                response = requests.request("DELETE", url, headers=self.header)
                self.verbose_print("[DELETE " + response.url + "]")
                self.verbose_print("Response: " + str(response.status_code) + ", " + str(response.reason))
            except:
                raise (ATDBException("ERROR: deleting " + url + "failed." + response.url))


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
    parser.add_argument("--host", nargs="?", default=DEFAULT_BACKEND_HOST, help= "Host url. Production = https://alta.astron.nl/altapi/, Acceptance = https://alta-acc.astron.nl/altapi/, Development (default) = http://localhost:8000/altapi/")
    parser.add_argument("--version", default=False, help="Show current version of this program, and the version of the ALTA backend.", action="store_true")
    parser.add_argument("--operation","-o", default="GET", help="GET, GET_ID, PUT, DELETE. Note that these operations will only work if you have the proper rights in the ALTA user database.")
    parser.add_argument("--id", default=None, help="id of the object to PUT to.")
    parser.add_argument("-t", "--taskid", nargs="?", default=None, help="Optional taskID which can be used instead of '--id' to lookup Observations or Dataproducts.")
    parser.add_argument("--key", default="observations.title", help="resource.field to PUT a value to. Example: observations.title")
    parser.add_argument("--query", "-q", default="taskID=180223003", help="Query to the REST API")
    parser.add_argument("--value", default="", help="value to PUT in the resource.field. If omitted it will PUT the object without changing values, but the built-in 'signals' will be triggered.")
    parser.add_argument("--payload", "-p", default="{}", help="Payload in json for the POST operation. To create new Observations or Dataproducts. (see examples)")
    parser.add_argument("--show_examples", "-e", default=False, help="Show some examples",action="store_true")

    args = parser.parse_args()
    try:
        atdb = ATDB(args.host, args.verbose)

        if (args.show_examples):

            print('atdb_interface.py version = '+VERSION)
            print('---------------------------------------------------------------------------------------------')
            print()
            print('--- basic examples --- ')
            print()
            print("Show the 'status' for Observation with taskID 180720003")
            print("> python atdb_interface.py -o GET --key observations:my_status --taskid 180223003")
            print()
            print("GET the ID of Observation with taskID 180223003")
            print("> python atdb_interface.py -o GET_ID --key observations:taskID --value 180223003")
            print()
            print("GET the ID of Dataproduct with name WSRTA180223003_ALL_IMAGE.jpg")
            print("> python atdb_interface.py -o GET_ID --key dataproducts:name --value WSRTA180223003_ALL_IMAGE.jpg")
            print()
            print("GET the 'status' for Dataproduct with ID = 45")
            print("> python atdb_interface.py -o GET --key dataproducts:my_status --id 45")
            print()
            print("PUT the 'status' of dataproduct with ID = 45 on 'copied'")
            print("> python atdb_interface.py -o PUT --key dataproducts:new_status --id 45 --value copied")
            print()
            print("PUT the 'status' of observation with taskID 180720003 on 'valid'")
            print("> python atdb_interface.py -o PUT --key observations:new_status --value valid --taskid 180223003")
            print()
            print("DELETE dataproduct with ID = 46 from the database (no files will be deleted).")
            print("> python atdb_interface.py -o DELETE --key dataproducts --id 46")
            print()
            print("DELETE dataproducts with ID's ranging from 11..15 from the database (no files will be deleted).")
            print("> python atdb_interface.py -o DELETE --key dataproducts --id 11..15 -v")
            print()
            print('--- advanced examples --- ')
            print()
            print("POST a new dataproduct to the database")
            print("> python atdb_interface.py -o POST --key dataproducts --payload {name:WSRTA180223003_B003.MS,filename:WSRTA180223003_B003.MS,description:WSRTA180223003_B003.MS,dataproduct_type:visibility,taskID:180223003,size:54321,quality:raw,new_status:defined,new_location:datawriter} -v")
            print()
            print("GET_LIST of taskIDs for observations with status = 'valid'")
            print("> python atdb_interface.py -o GET_LIST --key observations:taskID --query status=valid")
            print()
            print("GET_LIST of IDs for dataproducts with status = 'invalid'")
            print("> python atdb_interface.py -o GET_LIST --key dataproducts:id --query status=invalid")
            print()
            print("PUT the field 'new_status' on 'valid' for all dataproducts with taskId = '180816001'")
            print("> python  atdb_interface.py -o PUT_LIST --key dataproducts:new_status --taskid 180816001 --value valid")
            print('---------------------------------------------------------------------------------------------')
            return


        if (args.operation=='GET'):
            result = atdb.do_GET(key=args.key, id=args.id, taskid=args.taskid, value=args.value)
            print(result)

        if (args.operation == 'GET_ID'):
            result = atdb.do_GET_ID(key=args.key, value=args.value)
            print(result)

        if (args.operation == 'GET_LIST'):
            result = atdb.do_GET_LIST(key=args.key, query=args.query)
            print(result)

        if (args.operation=='PUT_LIST'):
            atdb.do_PUT_LIST(key=args.key, taskid=args.taskid, value=args.value)

        if (args.operation=='PUT'):
            atdb.do_PUT(key=args.key, id=args.id, value=args.value, taskid=args.taskid)

        if (args.operation=='POST'):
            atdb.do_POST(resource=args.key, payload=args.payload)

        if (args.operation=='DELETE'):
            atdb.do_DELETE(resource=args.key, id=args.id)

    except ATDBException as exp:
        exit_with_error(exp.message)

    sys.exit(0)


if __name__ == "__main__":
    main()

