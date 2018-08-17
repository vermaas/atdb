#!/usr/bin/python3
import sys
import requests
import json
import argparse
from datetime import *

"""
alta_interface.py : a commandline tool to inferface with the ALTA REST API.
:author Nico Vermaas - Astron
"""
VERSION = "0.9.5-RC1 (16 aug 2018)"

# ====================================================================

# The request header
ALTA_HEADER = {
    'content-type': "application/json",
    'cache-control': "no-cache",
    'authorization': "Token to be retrieved from alatapi"
}

DEFAULT_BACKEND_HOST = "http://localhost:8000/altapi/"
ALTA_SYSTEM_USER = "backend-irods"
DEFAULT_CREDENTIALS_FILE = "/etc/irods/" + ALTA_SYSTEM_USER + ".secret"
TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

class ALTAException(Exception):
    """
    Exception with message.
    """
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class ALTA:
    """
    Calibrators class, use to parse SIP and update the backend database
    through REST API calls.
    """
    def __init__(self, host, username, password, verbose=True):
        """
        Constructor.
        :param host: the host name of the backend.
        :param username: The username known in Django Admin.
        :param verbose: more information runtime.
        :param header: Request header for ALTA REST requests with token authentication.
        """
        self.host = host
        self.username = username
        self.password = password
        self.verbose = verbose

        try:
            self.header = self.__get_request_header(username, password)
        except ALTAException as e:
            raise (ALTAException(e))
        except Exception as e:
            raise (ALTAException("ERROR in retrieving ALTA request header. Exception " + str(e)))


    def verbose_print(self, info_str):
        """
        Print info string if verbose is enabled (default False)
        :param info_str: String to print
        """
        if self.verbose:
            print(info_str)

    # === Backend requests ================================================================================
    def __get_token_from_backend(self, username, password):
        """
        Do a http POST request to the alta backend with username and password
        If username is the default "backend-irods" then it will be read from a credentials file
        which is located in the /etc/irods/
         For test purposes option user vagrant can be used
        otherwise retrieve from 'secret file'
        to retrieve the token which is used as header for all other backend calls
        :param: Username which should be defined in Django Admin
        :return: token string
        """
        # create the url, 'api_resource' defines which part of the REST API must be queried
        url = self.host + "obtain-auth-token/"

        payload = {}
        if username == ALTA_SYSTEM_USER:
            try:
                f = open(DEFAULT_CREDENTIALS_FILE)
            except Exception as e:
                raise (ALTAException("ERROR can not read credential file. " + str(e)))

            content = f.readlines()
            content = [x.strip() for x in content]
            credentials = [x.split(':') for x in content]

            for username, password in credentials:
                payload['username'] = username
                payload['password'] = password
        else:
            payload['username'] = username
            if (username=="vagrant"):
                # default user for testing, this only works in development
                payload['password'] = "vagrant"
            else:
                payload['password'] = password

        response = requests.request("POST", url, data=payload)
        self.verbose_print("[POST " + response.url + "]")
        self.verbose_print("response.txt: " + response.text)

        response_exception_msg = "ERROR: unknown user or wrong password for user ["+username+"]"
        try:
            results = json.loads(response.text)
            token = results["token"]
            self.verbose_print("token: " + token)
        except:
            # Decode failed
            raise (ALTAException(response_exception_msg))

        return token


    def __get_request_header(self, username, password):
        """
        Retrieve the request header required for ALTA REST calls
        :param: Username which should be defined in LDAP
        :return: Dictionary which contains the request header
        """
        header = ALTA_HEADER
        token = self.__get_token_from_backend(username, password)
        # token_str = "Token: " + token
        token_str = "Token " + token

        header['authorization'] = str(token_str)
        self.verbose_print("User: " + str(username) + ", header: " + str(header))
        return header


    def encodePayload(self, payload):
        """
        Translate the payload dictionary to a string.
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


    def GET_activityByRunId(self,  runId):
        """
        Do a http GET request to the alta backend to find the Observation with the given runId
        :runId runId:
        """

        url = self.host + "activities"
        # create the querystring, external_ref is the mapping of this element to the alta datamodel lookup field
        querystring = {"runId": runId}

        response = requests.request("GET", url, headers=self.header, params=querystring)
        self.verbose_print("[GET " + response.url + "]")

        try:
            results = json.loads(response.text)
            activity = results["results"][0]
            return activity
        except:
            raise (ALTAException("ERROR: " + response.url + " not found."))

    # ------------------------------------------------------------------------------#
    #                                Main User functions                            #
    # ------------------------------------------------------------------------------#

    def do_GET_version(self):
        """
        Do a http GET request to the alta backend to find the version of the API.
        :return version
        """

        url = self.host + "projects"

        response = requests.request("GET", url, headers=self.header)
        self.verbose_print("GET Response: " + str(response.status_code) + ", " + str(response.reason))

        try:
            results = json.loads(response.text)
            version = results["version"]
            return version
        except:
            raise (ALTAException("ERROR: " + response.url + " not found."))


    def do_GET_ID(self, key, value):
        """
        Get the id based on a field value of a resource. This is a generic way to retrieve the id.
        :param resource: contains the resource, for example 'projects', 'observations', 'dataproducts'
        :param field: the field to search on, this will probably be 'externalRef' or 'runId'
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
            result = my_json['results'][0]
            id = result['id']
            return id
        except:
            return '-1'


    def do_GET(self, key, id, runid, value):
        """
        Do a http GET request to the alta backend to find the value of one field of an object
        :param key: contains the name of the resource and the name of the field separated by a colon. observations.description
        :param id: the database id of the object.
        :param runid (optional): when the runid (of an activity) is known, it can be used instead of id.
        """

        # split key in resource and field
        params = key.split(":")
        resource = params[0]
        field = params[1]

        if runid!=None:
            activity = self.GET_activityByRunId(runid)
            id = activity['id']

        if id==None:
            # give up and throw an exception.
            raise (ALTAException("ERROR: no valid 'id' or 'runid' provided"))

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
            raise (ALTAException("ERROR: " + response.url + " not found."))


    def do_PUT(self, key, id, value, runid):
        """
        PUT a value to an existing field of a resource (table).
        :param key: contains the name of the resource and the name of the field separated by a colon. observations.description
        :param id: the database id of the object.
        :param value: the value that has to be PUT in the key. If omitted, an empty put will be done to trigger the signals.
        :param runid (optional): when the runid (of an activity) is known, it can be used instead of id.
        """

        # split key in resource and field
        if key.find(':')>0:
            params = key.split(":")
            resource = params[0]
            field = params[1]
        else:
            resource = key
            field = None

        if runid!=None:
            activity = self.GET_activityByRunId(runid)
            id = activity['id']

        url = self.host + resource + "/" + str(id) + "/"
        self.verbose_print(('url: ' + url))
        if id==None:
            raise (ALTAException("ERROR: no valid 'id' or 'runid' provided"))

        payload = {}
        if field!=None:
            payload[field]=value
            payload = self.encodePayload(payload)
        try:
            response = requests.request("PUT", url, data=payload, headers=self.header)
            self.verbose_print("[PUT " + response.url + "]")
            self.verbose_print("Response: " + str(response.status_code) + ", " + str(response.reason))
        except:
            raise (ALTAException("ERROR: " + response.url + " not found."))


    def do_DELETE(self, key, id):
        """
        Do a http DELETE request to the alta backend (it will fail if the user does not have the proper rights)
        """
        if id == None:
            raise (ALTAException("ERROR: no valid 'id' provided"))

        url = self.host + key + "/" + str(id) + "/"
        self.verbose_print(('DELETE: ' + url))

        try:
            response = requests.request("DELETE", url, headers=self.header)
            self.verbose_print("[DELETE " + response.url + "]")
            self.verbose_print("Response: " + str(response.status_code) + ", " + str(response.reason))
        except:
            raise (ALTAException("ERROR: deleting " +url+ "failed." + response.url))


    def do_UPLOAD(self, key, id, filename, runid):
        """
        Do a http POST request to the alta backend (it will fail if the user does not have the proper rights)
        """
        # first upload the file..
        url = self.host + "upload/"
        files = {'file': open(filename, 'rb')}
        self.verbose_print("files: " + str(files))
        payload = {'description': 'uploaded file by '+self.username, 'timestamp': str(datetime.now())}
        self.verbose_print("payload: " + str(payload))
        self.verbose_print("headers: " + str(self.header))

        # response = requests.post(url, files=files, data=payload, headers=self.header)
        # The request header
        file_upload_header = ALTA_HEADER
        file_upload_header['Content-Type'] = "multipart/form-data"
        self.verbose_print('file_upload_header: '+str(file_upload_header))

        response = requests.post(url, files=files, data=payload, headers=file_upload_header)
        self.verbose_print("[POST " + response.url + "]")

        # Q: Response: 415, Unsupported Media Type
        # A: If a client sends a request with a content-type that cannot be parsed then a UnsupportedMediaType exception will be raised, which by default will be caught and return a 415 Unsupported Media Type response
        # Manually through http://localhost:8000/altapi/upload/ the Media type = multipart/form-data
        # Content-Type: multipart/form-data;

        self.verbose_print("Response: " + str(response.status_code) + ", " + str(response.reason))

        # ...then add the hyperlink to the indicated resource.field.

        value = '???' # read the new url from the response? or what?

        # upload the link to the uploaded file to the provided resource and field
        # (usually activity.thumbnail or dataproduct.thumbnail)

        # split key in resource and field
        if key.find(':') > 0:
            params = key.split(":")
            resource = params[0]
            field = params[1]
        else:
            resource = key
            field = None

        if runid != None:
            activity = self.GET_activityByRunId(runid)
            id = activity['id']

        url = self.host + resource + "/" + str(id) + "/"
        self.verbose_print(('url: ' + url))
        if id == None:
            raise (ALTAException("ERROR: no valid 'id' or 'runid' provided"))

        payload = {}
        if field != None:
            payload[field] = value
            payload = self.encodePayload(payload)
        try:
            response = requests.request("PUT", url, data=payload, headers=self.header)
            self.verbose_print("[PUT " + response.url + "]")
            self.verbose_print("Response: " + str(response.status_code) + ", " + str(response.reason))
        except:
            raise (ALTAException("ERROR: " + response.url + " not found."))

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

    parser.add_argument("--value", default="", help="value to PUT in the resource.field. If omitted it will PUT the object without changing values, but the built-in 'signals' will be triggered.")
    parser.add_argument("--filename", default="", help="experimental, do not use")
    parser.add_argument("-r", "--runid", nargs="?", default=None, help="Optional runID which can be used instead of '--id' to lookup Observations or Pipelines.")
    parser.add_argument("-v","--verbose", default=False, help="More information at run time.",action="store_true")
    parser.add_argument("--host", nargs="?", default=DEFAULT_BACKEND_HOST, help= "Host url. Production = https://alta.astron.nl/altapi/, Acceptance = https://alta-acc.astron.nl/altapi/, Development (default) = http://localhost:8000/altapi/")
    parser.add_argument("-u","--user", nargs="?", default='alta-user', help="Username.")
    parser.add_argument("-p", "--password", nargs="?", default=ALTA_SYSTEM_USER, help="Password.")
    parser.add_argument("--version", default=False, help="Show current version of this program, and the version of the ALTA backend.", action="store_true")
    parser.add_argument("--key", default="observations.title", help="resource.field to PUT a value to. Example: observations.title")
    parser.add_argument("--id", default=None, help="id of the object to PUT to.")
    parser.add_argument("--operation","-o", default="GET", help="GET, GET_ID, PUT, DELETE. Note that these operations will only work if you have the proper rights in the ALTA user database.")
    parser.add_argument("--show_examples", "-e", default=False, help="Show some examples",action="store_true")

    args = parser.parse_args()
    try:
        alta = ALTA(args.host, args.user, args.password, args.verbose)

        if (args.show_examples):
            alta_version = alta.do_GET_version()
            print('alta_interface.py version = '+VERSION + ', ALTA version = '+alta_version)
            print('---------------------------------------------------------------------------------------------')
            print("Show the 'observer' field for Observation with runId=180720003")
            print("> python alta_interface.py -o GET --key observations:observer --runid 180720003 --user alta-user --password alta-user")
            print()
            print("Get the ID for Project with externalRef 'ALTA_18A_001'")
            print("> python alta_interface.py -o GET_ID --key projects:externalRef --value ALTA_18A_001  --user alta-user --password alta-user")
            print()
            print("Change the 'observer' field to 'NV', for Observation with (database) id=2078:")
            print("> python alta_interface.py -o PUT --key observations:observer --id 2078 --value NV --verbose -u vagrant")
            print()
            print("Change the 'observer' field to 'NV', for Observation with runId=180720003")
            print("> python alta_interface.py -o PUT --key observations:observer --runid 180720003 --value NJV --verbose -u alta-user -p alta-user")
            print()
            print("Add 2 calibrator_sources to the Observation with runId=180720003")
            print("> python alta_interface.py -o PUT --key observations:calibrator_sources --value 3C138,3C295 --runid 180720003 --user alta-user --password alta-user -v")
            print()
            print("Trigger an update of Activity with runid = 18010502. DatasetID will be updated based on used dataproducts")
            print("> python alta_interface.py -o PUT --key activities --runid 18010502 --u vagrant -v")
            print()
            print("Change the rights for project 10 to 'public'.")
            print("> python alta_interface.py -o PUT --key projects:rights --id 10 --value public --u vagrant -v")
            print()
            print("Trigger an update of Observation with runid = 18010502. DatasetID and will be updated, Calibrators will be searched")
            print("> python alta_interface.py -o PUT --key observations --runid 18010502 --u vagrant -v")
            print()
            print("Delete the (failed?) ingest object 554, including all the activities and dataproducts it added to the database.")
            print("> python alta_interface.py -o DELETE --key ingests --id 554 --user alta-user --password alta-user -v")
            print()
            print("Add an earlier uploaded thumbnail to observation ")
            print("> python alta_interface.py -o PUT --key observations:thumbnail --runid 180720003 --value http://alta.astron.nl/alta-static/media/WSRTA180223003_ALL_IMAGE.jpg --user vagrant --password vagrant -v")
            print()
            print("Upload a thumbnail to observation ")
            print("> python alta_interface.py -o UPLOAD --key observations:thumbnail --runid 180720003 --filename WSRTA180223003_B018_IMAGE.jpg --user vagrant --password vagrant -v")

            print('---------------------------------------------------------------------------------------------')
            return

        if (args.version):
            altapi_version = alta.do_GET_version()
            print('--- alta_interface.py version = '+VERSION + ', ALTA version = '+altapi_version + '---')
            return

        if (args.operation=='GET'):
            result = alta.do_GET(key=args.key, id=args.id, runid=args.runid, value=args.value)
            print(result)

        if (args.operation == 'GET_ID'):
            result = alta.do_GET_ID(key=args.key, value=args.value)
            print(result)

        if (args.operation=='PUT'):
            alta.do_PUT(key=args.key, id=args.id, value=args.value, runid=args.runid)

        if (args.operation=='DELETE'):
            alta.do_DELETE(key=args.key, id=args.id)

        # doesn't work yet, I get a 415 error
        if (args.operation=='UPLOAD'):
            alta.do_UPLOAD(key=args.key, id=args.id, filename=args.filename, runid=args.runid)

    except ALTAException as exp:
        exit_with_error(exp.message)

    sys.exit(0)


if __name__ == "__main__":
    main()

