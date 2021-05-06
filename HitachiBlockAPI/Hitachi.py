"""
This library provides an easy way to script tasks for the Hitachi Storage Arrays.
"""

import http.client
import socket
import json
import ssl
from base64 import b64encode
import logging
import time
import uuid
import sys
import pprint

pp = pprint.PrettyPrinter(indent=4)

# create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
#2020-10-27 08:24:01,160 - DEBUG - Hitachi.py - line+522 - luns_one_port_get - Message
#formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - line+%(lineno)d - %(funcName)s - %(message)s')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - line+%(lineno)d - %(funcName)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)

# The current version of this library.
VERSION = "0.9.2"

class RestAPI:
    '''This Class can be used to : '''

    def __init__(self, protocol:str='https://', fqdn_ip:str='127.0.0.1', port:int=443, username:str='maintenance', password:str='raid-maintenance'):
        self._ip_fqdn = fqdn_ip
        self._port = str(port)
        self._username = username
        self.__password = password
        self.__userAndPass = b64encode((username+':'+password).encode('utf-8')).decode("ascii")
        self._protocol = protocol
        self._storage_device_id = None
        self._token = None
        self._session_id = None
        self.__url_base = '/ConfigurationManager/v1/objects'
        self.__url_base_ConfigurationManager = '/ConfigurationManager'
        self.__url_base_v1 = '/v1'
        self.__url_base_objects = '/objects'
        self.__url_base_views = '/views'
        self.__url_resource_lock = '/services/resource-group-service/actions/lock/invoke'
        self.__url_resource_unlock = '/services/resource-group-service/actions/unlock/invoke'
        self.__url_storages = '/storages'
        self.__url_storage_summaries = '/storage-summaries/instance'
        self.__url_jobs = '/jobs'
        self.__url_sessions = '/sessions'
        self.__url_ports = '/ports'
        self.__url_host_wwn_paths = '/host-wwn-paths'
        self.__url_pools = '/pools'
        self.__url_remotereplication = '/remote-replications'
        self.__url_snapshotgroups = '/snapshot-groups'
        self.__url_snapshotsall = '/snapshot-replications'
        self.__json_data = 'data'
        self.__json_storage_device_id = 'storageDeviceId'
        self.__json_serial_number = 'serialNumber'
        self.__json_token = 'token'
        self.__json_sessionId = 'sessionId'
        self.__json_hostWwnId = 'hostWwnId'
        self.__json_ldevId = 'ldevId'
        self.__json_remoteReplicationId = 'remoteReplicationId'
        self.__json_snapshotGroupName = 'snapshotGroupName'
        self.__json_snapshotId = 'snapshotId' #if you specify an ldev in the request url
        self.__json_snapshotReplicationId = 'snapshotReplicationId' #if you do not specify an ldev

        #self.__maxConnectionsParallelTotal = 8
        #self.__maxConnectionsParallelGet = 6

    #check if string is of json format
    def __is_json(self, myjson:str):
        try:
            json_object = json.loads(myjson)
        except ValueError as e:
            return False
        return True

    #check the response
    def __check_response(self, return_response:list, element_number:int=0, key:str=None):
        if key == None:
            key = self.__json_data

        return_value = None

        if len(return_response) == 3:
            if return_response[0] == 0:
                #maybe json string
                if self.__is_json(str(return_response[2])):
                    logger.debug('output is of type json string')
                    return_response_json = json.loads(return_response[2])
                    #if you specify 'all' then the whole dictionary is sent back
                    if key == 'all':
                        logger.debug('key "all" selected')
                        #return dict
                        return(return_response_json)
                    else:
                        #check if the key exists
                        if key in return_response_json:
                            if len(return_response_json[key]) == 0:
                                logger.warning('the key "'+str(key)+'" is empty.')
                                return(None)
                            else:
                                logger.debug('key "'+str(key)+'" selected')
                                #is it a list then keep the list type
                                if isinstance(return_response_json[key], list):
                                    return(return_response_json[key])
                                else:
                                    #return dict
                                    return(return_response_json[key])
                        else:
                            logger.error('the key you looked for "'+str(key)+'" does not exist in the dictionary.')
                            return(-1)
                else:
                    if str(return_response[2]) == '':
                        logger.debug('empty response')
                        return(None)
                    else:
                        logger.error('ERROR: response:'+str(return_response))
                        return(-1)
            else:
                logger.warning('WARNING: response status:'+str(return_response[1])+', response reason:'+str(return_response[2]))
                return(None)
        else:
            logger.error('ERROR: response:'+str(return_response))
            return(-1)

    #extecutes the web request
    def _webrequest(self, fqdn_ip:str=None, port:str=None, username:str=None, password:str=None, request_type:str='GET', url_suffix:str=None, body:str=None, timeout:int=60):
        '''Return the json response of the webrequest'''
        start = time.time()

        #set internal values if nothing is specified
        if fqdn_ip == None:
            fqdn_ip = self._ip_fqdn
        if port == None:
            port = self._port
        if username == None and password == None:
            userAndPass = self.__userAndPass
        else:
            userAndPass = b64encode((username+':'+password).encode('utf-8')).decode("ascii")

        if url_suffix == None:
            #set standar url suffix
            url = self._protocol+fqdn_ip+':'+str(port)+self.__url_base+self.__url_storages
        else:
            #use the url suffix that was set in the function call
            url = self._protocol+fqdn_ip+':'+str(port)+url_suffix

        #if already a token is set then use it otherwise use the user and password
        if self._token is None:
            logger.debug('No token found. Use user ('+str(self._username)+') and password used')
            #user and password
            headers = {'Accept':'application/json', 'Content-Type':'application/json', 'Authorization' : 'Basic %s' %  userAndPass}
        else:
            #token
            logger.debug('token ('+str(self._token)+') is used')
            headers = {'Accept':'application/json', 'Content-Type':'application/json', 'Authorization' : 'Session '+str(self._token)}

        #convert the body to json format string if it is a dictionary
        if not body == None:
            if type(body) == str:
                if not self.__is_json:
                    body = json.dumps(body)

        #create https connection, unverified connection
        connection = http.client.HTTPSConnection(fqdn_ip+':'+port, context=ssl._create_unverified_context(), timeout=timeout)

        try:
            # Send request
            logger.debug('request type: '+ str(request_type))
            logger.debug('headers: '+ str(headers))
            logger.debug('body: '+ str(body))
            logger.debug('URL: '+ str(url))
            if body == None:
                connection.request(method=request_type, url=url, headers=headers)
            else:
                connection.request(method=request_type, url=url, headers=headers, body=body)
            # Get the response
            response = connection.getresponse()
        except socket.timeout as st:
            logger.error('ERROR: http(s) timeout received after '+str(timeout)+'sec. : '+str(st))
            return([-1, 'ERROR: http(s) timeout received after '+str(timeout)+'sec.', st])
        except http.client.HTTPException as e:
            # other kind of error occured during request
            logger.error('ERROR: HTTPException: '+str(e))
            return([-1, 'ERROR: HTTPException', st])

        # Display the response status
        #print()
        #print ("Status = ", response.status)
        # 200 Ok
        # 202 Accepted The request has been accepted for processing, but the processing has not been completed.
        logger.debug('request response status: '+ str(response.status))
        response_string = str(response.read(), encoding='utf8').replace('\r', '').replace('\n','')
        if response.status == http.client.OK or response.status == http.client.ACCEPTED:
            if not len(response_string) == 0:
                return_response = [0, response.status, response_string]
            else:
                return_response = [0, response.status, '']
        else:
            logger.error('Got error back. status: '+ str(response.status)+' - reason: '+str(response.reason))
            return_response = [-1, response.status, response_string]

        #close connection
        connection.close()
        end = time.time()
        logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
        return(return_response)

    #general webrequest that creates/deletes sessions
    def _general_webrequest(self, fqdn_ip:str=None, port:str=None, username:str=None, password:str=None, request_type:str='GET', url_suffix:str=None, body:str=None, timeout:int=60, check=True):
        start = time.time()

        return_value = None

         #set internal values if nothing is specified
        if fqdn_ip == None:
            fqdn_ip = self._ip_fqdn
        if port == None:
            port = self._port
        if username == None and password == None:
            userAndPass = self.__userAndPass
        else:
            userAndPass = b64encode((username+':'+password).encode('utf-8')).decode("ascii")

        #create session token if not a GET request
        if not request_type == 'GET':
            self._session_create()

        #send request
        return_response = self._webrequest(fqdn_ip=fqdn_ip, port=port, username=username, password=password, request_type=request_type, url_suffix=url_suffix, body=body, timeout=timeout)

        # Do not check response when there is no response.....
        if check:
            return_response = self.__check_response(return_response=return_response)

        end = time.time()

        #create session token if not a GET request
        if not request_type == 'GET':
            self._session_delete()

        logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
        return(return_response)

    #execute in all functions
    def _general_execute(self):
        start = time.time()
        #set StorageDeviceId if not already set
        if self._storage_device_id == None:
            self.storage_device_id_set()

        end = time.time()
        logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")

        return(None)

    #gets the storge elements
    def storage_systems_get(self, fqdn_ip:str=None, port:str=None, username:str=None, password:str=None):
        start = time.time()
        request_type = 'GET'

        #set token to None so user and password is used
        self._token = None
        #set internal values if nothing is specified
        if username == None:
            username = self._username
        if password == None:
            password = self.__password
        if fqdn_ip == None:
            fqdn_ip = self._ip_fqdn
        if port == None:
            port = self._port

        logger.debug('Request string: '+str(request_type)+' - '+str(self.__url_base+self.__url_storages))
        return_response=self._webrequest(request_type=request_type, fqdn_ip=fqdn_ip, port=port, username=username, password=password, url_suffix=self.__url_base+self.__url_storages)
        logger.debug('Request response: ' + str(return_response))
        return_response = self.__check_response(return_response=return_response)
        #[{'storageDeviceId': '800000058068',  'model': 'VSP G1000',  'serialNumber': 58068,  'svpIp': '10.70.4.145'}]

        #create a dictionary out of the list
        storages = {}
        for storage in return_response:
            storages[storage[self.__json_serial_number]] = storage

        end = time.time()
        logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
        return(storages)

    #gets the storge details ucode, ip
    def storage_details_get(self, fqdn_ip:str=None, port:str=None, username:str=None, password:str=None):
        start = time.time()
        request_type = 'GET'

        if fqdn_ip == None:
            #execute general procedures
            self._general_execute()

        #set token to None so user and password is used
        self._token = None
        #set internal values if nothing is specified
        if fqdn_ip == None:
            fqdn_ip = self._ip_fqdn
        if port == None:
            port = self._port
        if username == None:
            username = self._username
        if password == None:
            password = self.__password

        logger.debug('Request string: '+str(request_type)+' - '+str(self.__url_base_ConfigurationManager)+str(self.__url_base_v1)+self.__url_base_objects+self.__url_storages+'/'+str(self._storage_device_id))
        return_response=self._webrequest(request_type=request_type, fqdn_ip=fqdn_ip, port=port, username=username, password=password, url_suffix=str(self.__url_base_ConfigurationManager)+str(self.__url_base_v1)+self.__url_base_objects+self.__url_storages+'/'+str(self._storage_device_id))
        logger.debug('Request response: ' + str(return_response))

        return_response = self.__check_response(return_response=return_response, key='all')
        end = time.time()
        logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
        return(return_response)

    #gets the summaries of a storage
    def storage_summaries_get(self, fqdn_ip:str=None, port:str=None, username:str=None, password:str=None, timeout:int=90):
        #self.__url_storage_summaries
        start = time.time()
        request_type = 'GET'

        #execute general procedures
        self._general_execute()

        #set token to None so user and password is used
        self._token = None
        #set internal values if nothing is specified
        if fqdn_ip == None:
            fqdn_ip = self._ip_fqdn
        if port == None:
            port = self._port
        if username == None:
            username = self._username
        if password == None:
            password = self.__password

        logger.debug('Request string: '+str(request_type)+' - '+str(self.__url_base_ConfigurationManager)+str(self.__url_base_v1)+self.__url_base_objects+self.__url_storages+'/'+str(self._storage_device_id)+str(self.__url_storage_summaries))
        return_response=self._webrequest(request_type=request_type, fqdn_ip=fqdn_ip, port=port, username=username, password=password, url_suffix=str(self.__url_base_ConfigurationManager)+str(self.__url_base_v1)+self.__url_base_objects+self.__url_storages+'/'+str(self._storage_device_id)+str(self.__url_storage_summaries), timeout=timeout)
        logger.debug('Request response: ' + str(return_response))

        return_response = self.__check_response(return_response=return_response, key='all')
        end = time.time()
        logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
        return(return_response)

    #register a storage in the Configuration Manager API
    def storage_register(self, storage_fqdn_ip:str, storage_username:str, storage_password:str, cmrestapi_fqdn_ip:str=None, storage_port:str='443', cmrestapi_port:str='23451', cmrest_username:str=None, cmrest_password:str=None):
        #get storage details
        start = time.time()
        request_type = 'GET'

        #set token to None so user and password is used
        self._token = None
        #set internal values if nothing is specified
        #CM REST API
        if cmrest_username == None:
            logger.debug('cm rest username set to: '+str(self._username))
            cmrest_username = self._username
        if cmrest_password == None:
            logger.debug('cmrest password set to the value you set as you instanciated it.')
            cmrest_password = self.__password
        if cmrestapi_fqdn_ip == None:
            logger.debug('cmrestapi_fqdn_ip set to: '+str(self._ip_fqdn))
            cmrestapi_fqdn_ip = self._ip_fqdn
        #Storage
        if storage_username == None:
            logger.debug('storage username set to: '+str(self._username))
            storage_username = self._username
        if storage_password == None:
            logger.debug('storage password set to the value you set as you instanciated it.')
            storage_password = self.__password

        #get storage device id
        storageDeviceId=self.storage_device_id_set(fqdn_ip=storage_fqdn_ip, port=storage_port, username=storage_username, password=storage_password)
        logger.debug('storageDeviceId set to'+str(storageDeviceId))
        return_response=self.storage_details_get(fqdn_ip=storage_fqdn_ip, port=storage_port, username=storage_username, password=storage_password)

        '''
        For VSP E series, VSP G350, G370, G700, G900, VSP F350, F370, F700, F900 with SVP
        {  "ctl1Ip" : "192.0.10.10",  "ctl2Ip" : "192.0.10.11",  "model" : "VSP G900",   "serialNumber" : 123456,  "usesSvp" : true,  "svpIp" : "192.0.2.100" }
        For VSP E series, VSP G350, G370, G700, G900, VSP F350, F370, F700, F900 without SVP
        {  "ctl1Ip" : "192.0.10.10",  "ctl2Ip" : "192.0.10.11",  "model" : "VSP G900",   "serialNumber" : 123456,  "usesSvp" : false }
        For storage systems VSP 5000 series, VSP G200, G400, G600, G800, VSP G1000,VSP G1500, VSP F400, F600, F800, VSP F1500, Virtual Storage Platform, orUnified Storage VM
        { "model": "VSP G1000", "serialNumber": 50679, "svpIp": "10.70.5.145", "isSecure": true }
        '''

        #parse json string to dictionary
        if type(return_response) == dict:
            storage_details = return_response
        else:
            logger.error('Request response is not of type dictionary ('+str(type(return_response))+')')
            sys.exit()

        #create new body to register the storage
        body = {}
        if str(storage_details['model']) in ['VSP E990', 'VSP G350', 'VSP G370', 'VSP G700', 'VSP G900', 'VSP F350', 'VSP F370', 'VSP F700', 'VSP F900']:
            #"ctl1Ip",  "ctl2Ip", "model", "serialNumber"
            logger.debug('Storage model: '+str(storage_details['model']))
            body['model'] = storage_details['model']
            body['serialNumber'] = storage_details['serialNumber']
            body['ctl1Ip'] = storage_details['ctl1Ip']
            body['ctl2Ip'] = storage_details['ctl2Ip']

        if str(storage_details['model']) in ['VSP 5100', 'VSP 5500', 'VSP 5100H', 'VSP 5500H', 'VSP G200', 'VSP G400', 'VSP G600', 'VSP G800', 'VSP G1000', 'VSP G1500', 'VSP F400', 'VSP F600', 'VSP F800', 'VSP F1500', 'VSP N400', 'VSP N600', 'VSP N800', 'HUS VM', 'VSP']:
            #model, serialNumber, svpIp, isSecure used
            logger.debug('Storage model: '+str(storage_details['model']))
            body['model'] = storage_details['model']
            body['serialNumber'] = storage_details['serialNumber']
            body['svpIp'] = storage_details['svpIp']
            body['isSecure'] = storage_details['isSecure']
        else:
            logger.error('storage model not supported ('+str(return_response['model'])+')')
            return(-1)
            sys.exit()

        logger.debug('Body set to: '+ json.dumps(body))

        #register storage
        request_type = 'POST'
        logger.debug('Request string: '+str(request_type)+' - '+str(self.__url_base+self.__url_storages))
        return_response=self._general_webrequest(request_type=request_type, fqdn_ip=cmrestapi_fqdn_ip, port=cmrestapi_port, username=cmrest_username, password=cmrest_password, body=json.dumps(body), url_suffix=self.__url_base+self.__url_storages)
        logger.debug('Request response: ' + str(return_response))

        return(return_response)

    #set storage device id
    def storage_device_id_get(self, fqdn_ip:str=None, port:str=None, username:str=None, password:str=None, serial_number:str=None):
        start = time.time()
        request_type = 'GET'

        return_value = None

        #set token to None so user and password is used
        self._token = None

        #set internal values if nothing is specified
        if username == None:
            username = self._username
        if password == None:
            password = self.__password
        if fqdn_ip == None:
            fqdn_ip = self._ip_fqdn
        if port == None:
            port = self._port

        if self._storage_device_id == None:
            # logger.info('storageDeviceID not set. Send request to find out.')
            logger.debug('Request string: '+str(request_type)+' - '+str(self.__url_base+self.__url_storages))
            return_response=self.storage_systems_get(fqdn_ip=fqdn_ip, username=username, password=password, port=port)
            logger.debug('Request response: ' + str(return_response))
        else:
            logger.info('storageDeviceID already set to: '+str(self._storage_device_id))
            return(self._storage_device_id)

        if type(return_response) == dict:
            if len(return_response) == 1:
                #only one storage system is returned
                for element in return_response:
                    return_value = return_response[element][self.__json_storage_device_id]
                    break
            else:
                #element number specified
                if serial_number == None:
                    logger.error('The parameter "serial_number" is not specified but more than 1 storage system is returned. Specify what storge system you want to use.')
                    sys.exit()
                else:
                    #storage device id of the element specified is returned
                    for key, value in return_response.items():
                        if str(key) == str(serial_number):
                            return_value = value[self.__json_storage_device_id]
                            break
                    #if the serial number is not found
                    if return_value == None:
                        logger.error('The parameter "serial_number" is not found in the storage systems that are returned. Specify a serial number that exists.')
                        sys.exit()
        else:
            #totally wrong return type
            logger.error('The response is not of type list ('+str(type(return_response))+')')
            sys.exit()

        end = time.time()
        logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
        return(return_value)

    #set storage device id
    def storage_device_id_set(self, fqdn_ip:str=None, port:str=None, username:str=None, password:str=None, serial_number:str=None):

        #set token to None so user and password is used
        self._token = None
        #set internal values if nothing is specified
        if username == None:
            username = self._username
        if password == None:
            password = self.__password
        if fqdn_ip == None:
            fqdn_ip = self._ip_fqdn
        if port == None:
            port = self._port

        #Set back the storageDeviceId to None
        self._storage_device_id = None

        #get storage device id
        return_response=self.storage_device_id_get(fqdn_ip=fqdn_ip, port=port, username=username, password=password, serial_number=serial_number)
        #set variable
        logger.debug('set class variable "_storage_device_id" to "' + str(return_response) + '"')
        self._storage_device_id = return_response
        return(return_response)

        #get jobs

    #get jobs
    def _jobs_get(self):
        '''
        {
        "data": [
            {
            "jobId": 43,
            "self": "/ConfigurationManager/v1/objects/storages/800000058068/jobs/43",
            "userId": "user",
            "status": "Completed",
            "state": "Succeeded",
            "createdTime": "2020-11-16T15:20:17Z",
            "updatedTime": "2020-11-16T15:20:19Z",
            "completedTime": "2020-11-16T15:20:19Z",
            "request": {
                "requestUrl": "/ConfigurationManager/v1/objects/storages/800000058068/ldevs/40962",
                "requestMethod": "DELETE",
                "requestBody": ""
            },
            "affectedResources": [
                "/ConfigurationManager/v1/objects/storages/800000058068/ldevs/40962"
            ]
            },
        '''
        start = time.time()
        request_type='GET'

        #execute general procedures
        self._general_execute()

        logger.debug('Request string: '+str(self.__url_base+self.__url_storages+'/'+self._storage_device_id+self.__url_jobs))
        return_response = self._general_webrequest(request_type=request_type, url_suffix=self.__url_base+self.__url_storages+'/'+self._storage_device_id+self.__url_jobs)

        end = time.time()
        logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
        return(return_response)

    #get last job
    def _jobs_last_get(self):
        '''
        '''
        start = time.time()

        return_response = self._jobs_get()

        if return_response == None:
            logger.warning('WARNING: no job found')
            end = time.time()
            logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
            return(None)
        else:
            end = time.time()
            logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
            return(return_response[0])

    #get job by id
    def _jobs_by_id_get(self, jobId:str=None):
        '''
        '''
        start = time.time()
        return_value = None

        return_response = self._jobs_get()
        logger.debug('Request response: ' + str(return_response))

        if not jobId == None:
            for job in return_response:
                if str(job['jobId']) == str(jobId):
                    return_value = job

            #if the job id was not found in the list
            if return_value == None:
                logger.error('ERROR: response: jobId: "'+str(jobId)+'" is not found. Please specify an existing jobId.')
                return_value = -1
        else:
            logger.error('ERROR: response: jobId is "None". Please specify a valid jobId.')
            logger.info('all jobs are sent back')
            return_value = return_response

        end = time.time()
        logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
        return(return_value)
        #get host groups of one port

    #get session id
    def _session_get(self):
        start = time.time()
        request_type='GET'

        #execute general procedures
        self._general_execute()

        logger.debug('Request string: '+str(self.__url_base+self.__url_storages+'/'+self._storage_device_id+self.__url_sessions))
        #these requests do not use the general webrequest this function is part of it.
        return_response=self._webrequest(request_type=request_type, url_suffix=self.__url_base+self.__url_storages+'/'+self._storage_device_id+self.__url_sessions)
        logger.debug('Request response: ' + str(return_response))

        '''
        {
            "data": [
                {
                    "sessionId": 5,
                    "userId": "hup",
                    "createdTime": "2019-05-28T14:04:41Z",
                    "lastAccessedTime": "2019-05-28T14:04:41Z"
                }
            ]
        }
        '''
        return_response = self.__check_response(return_response=return_response)
        end = time.time()
        logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
        return(return_response)

    #create session
    def _session_create(self):
        '''
        '''
        return_value = None

        start = time.time()
        request_type='POST'

        #set token to None so user and password is used
        self._token = None

        logger.debug('Request string: '+str(self.__url_base+self.__url_storages+'/'+self._storage_device_id+self.__url_sessions))
        #these requests do not use the general webrequest this function is part of it.
        return_response=self._webrequest(request_type=request_type, url_suffix=self.__url_base+self.__url_storages+'/'+self._storage_device_id+self.__url_sessions)
        logger.debug('Request response: ' + str(return_response))

        '''
        {
            "token": "74014a6e-a4b2-4b87-8021-de0ef3e92bde",
            "sessionId": 3
        }
        -> [0, 200, {'token': '74014a6e-a4b2-4b87-8021-de0ef3e92bde', 'sessionId': 3}]
        '''

        return_response = self.__check_response(return_response=return_response, key='all')
        if type(return_response) == dict:
            logger.debug('token: ' + str(return_response[self.__json_token]))
            self._token = return_response[self.__json_token]
            logger.debug('session id: ' + str(return_response[self.__json_sessionId]))
            self._session_id = return_response[self.__json_sessionId]
            return_value = None
        else:
            logger.error('the response was not in dictionary or json format.')
            return_value = -1

        end = time.time()
        logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
        return(return_value)

    #delete session
    def _session_delete(self):
        '''
        '''
        return_value = None

        start = time.time()
        request_type='DELETE'

        if self._session_id == None:
            return('WARNING: nothing done as no session was created')
        else:
            logger.debug('Request string: '+str(self.__url_base+self.__url_storages+'/'+str(self._storage_device_id)+self.__url_sessions+'/'+str(self._session_id)))
            #these requests do not use the general webrequest this function is part of it.
            return_response = self._webrequest(request_type=request_type, url_suffix=self.__url_base+self.__url_storages+'/'+str(self._storage_device_id)+self.__url_sessions+'/'+str(self._session_id))
            logger.debug('Request response: ' + str(return_response))

            return_response = self.__check_response(return_response=return_response, key='all')
            self._token = None
            self._session_id = None
            return_value = None

        end = time.time()
        logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
        return(return_value)

    # Show status of refresh for all arrays
    def refresh_status(self):
        start = time.time()
        request_type='GET'

        #execute general procedures
        # self._general_execute()

        # https://172.29.165.22:23451/ConfigurationManager/v1/views/refresh-statuses
        logger.debug('Request string: '+str(request_type)+' - '+str(self.__url_base_ConfigurationManager)+str(self.__url_base_v1)+self.__url_base_views+'/refresh-statuses')
        return_response = self._general_webrequest(request_type=request_type, url_suffix=str(self.__url_base_ConfigurationManager)+str(self.__url_base_v1)+self.__url_base_views+'/refresh-statuses')
        logger.debug('Request response: ' + str(return_response))

        return(return_response)


    # Invoke a refresh for the acutal array
    def refresh_invoke(self):
        start = time.time()
        request_type='PUT'

        #execute general procedures
        self._general_execute()

        body = '''
        {
          "parameters": {
            "storageDeviceId": '''+str(self._storage_device_id)+'''
          }
        }
        '''

        # https://172.29.165.22:23451/ConfigurationManager/v1/views/actions/refresh/invoke
        logger.debug('Request string: '+str(self.__url_base_ConfigurationManager)+str(self.__url_base_v1)+self.__url_base_views+'/actions/refresh/invoke')
        return_response = self._general_webrequest(request_type=request_type, url_suffix=str(self.__url_base_ConfigurationManager)+str(self.__url_base_v1)+str(self.__url_base_views+'/actions/refresh/invoke'), body=body, check=False)
        logger.debug('Request response: ' + str(return_response))
        return(return_response)



    #lock the resource
    #not done
    def resource_lock(self, waitTime=None):
        start = time.time()
        request_type='PUT'

        #execute general procedures
        self._general_execute()

        #set the default if it is not set or it is not a numeric value
        if waitTime == None or not (str(waitTime).isnumeric()):
            waitTime = 30

        body = '''
        {
          "parameters": {
            "waitTime": '''+str(waitTime)+'''
          }
        }
        '''
        #lock the resources
        logger.debug('Request string: '+str(self.__url_base_ConfigurationManager)+str(self.__url_base_v1)+'/'+str(self._storage_device_id)+str(self.__url_resource_lock))
        return_response = self._general_webrequest(request_type=request_type, url_suffix=str(self.__url_base_ConfigurationManager)+str(self.__url_base_v1)+'/'+str(self._storage_device_id)+str(self.__url_resource_lock), body=body)
        logger.debug('Request response: ' + str(return_response))

        return(return_response)

    #unlook the resource
    #not done
    def resource_unlock(self):
        return()

    #get resource group information
    def resource_group_get(self, timeout:int=180):
        start = time.time()
        request_type='GET'

        '''
        {
            "data": [
                {
                "resourceGroupId": 0,
                "resourceGroupName": "meta_resource",
                "lockStatus": "Unlocked",
                "virtualStorageId": 0,
                "ldevIds": [
                    0,
                    4
                ],
                "parityGroupIds": [
                    "1-1",
                    "5-5"
                ],
                "externalParityGroupIds": [
                    "10-2"
                ],
                "portIds": [
                    "CL1-A",
                    "CL3-A"
                   ],
                "hostGroupIds": [
                    "CL3-A,0",
                    "CL3-A,1"
                ]
            },
            {
                "resourceGroupId": 1,
                "resourceGroupName": "VSM55555",
                "lockStatus": "Unlocked",
                "virtualStorageId": 2,
                "ldevIds": [
            ...
            }
        '''

        #execute general procedures
        self._general_execute()

        logger.debug('Request string: '+str(self.__url_base+self.__url_storages + '/' + str(self._storage_device_id) + '/resource-groups'))
        return_response = self._general_webrequest(request_type=request_type, url_suffix=self.__url_base+self.__url_storages + '/' + str(self._storage_device_id) + '/resource-groups', timeout=timeout)
        logger.debug('Request response: ' + str(return_response))

        end = time.time()
        logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
        return(return_response[0])

    # ==========================================================================
    # get host-wwn-paths by views
    # ==========================================================================
    # gets all lun path with hsds / wwn and more from ConfMgr DB (views)
    # we get all possible (16384) elements
    # ==========================================================================
    # curl --insecure --noproxy '*' -H "Content-Type:application/json"  -u restadmin:restadmin0nly -X GET "https://172.29.165.22:23451/ConfigurationManager/v1/views/host-wwn-paths?\$count=16384&\$query=(ldev.storageDeviceId%20eq%20%27886000417711%27)"
    # https://172.29.165.22:23451/ConfigurationManager/v1/views/host-wwn-paths?\$count=16384&\$query=(ldev.storageDeviceId%20eq%20%27886000417711%27)

    # returns elements like that:

    # {
    #     'hostGroup': {   'hostGroupId': 'CL1-A,1',
    #                      'hostGroupName': 'testvmdanb0001_1',
    #                      'hostGroupNumber': 1,
    #                      'hostMode': 'WIN_EX',
    #                      'hostModeOptions': [2, 13, 25, 40],
    #                      'isDefined': True,
    #                      'portId': 'CL1-A',
    #                      'resourceGroupId': 0,
    #                      'storageDeviceId': '886000417711'},
    #     'hostWwn': {   'hostWwnId': 'CL1-A,1,ff00112233445566',
    #                    'storageDeviceId': '886000417711',
    #                    'wwnNickname': '-'},
    #     'ldev': {   'attributes': ['CVS', 'HDT'],
    #                 'blockCapacity': 419430400,
    #                 'byteFormatCapacity': '200.00 G',
    #                 'clprId': 0,
    #                 'dataReductionMode': 'disabled',
    #                 'dataReductionStatus': 'DISABLED',
    #                 'emulationType': 'OPEN-V-CVS',
    #                 'isDefined': True,
    #                 'isFullAllocationEnabled': False,
    #                 'isRelocationEnabled': True,
    #                 'label': 'a9cu-rh-gaga',
    #                 'ldevId': 12544,
    #                 'mpBladeId': 0,
    #                 'numOfUsedBlock': 0,
    #                 'poolId': 0,
    #                 'resourceGroupId': 0,
    #                 'status': 'NML',
    #                 'storageDeviceId': '886000417711',
    #                 'tierLevel': 'all',
    #                 'tierLevelForNewPageAllocation': 'M',
    #                 'usedCapacityPerTierLevel1': 0},
    #     'lun': {'lun': 1, 'lunId': 'CL1-A,1,1', 'storageDeviceId': '886000417711'},
    #     'port': {   'fabricMode': True,
    #                 'loopId': 'EF',
    #                 'lunSecuritySetting': True,
    #                 'portAttributes': ['TAR', 'MCU', 'RCU', 'ELUN'],
    #                 'portConnection': 'PtoP',
    #                 'portId': 'CL1-A',
    #                 'portSpeed': '16G',
    #                 'portType': 'FIBRE',
    #                 'storageDeviceId': '886000417711',
    #                 'wwn': '50060e8012452f00'},
    #     'wwn': {'wwn': 'ff00112233445566'}
    # }


    def view_host_wwn_paths_get(self):
        start = time.time()
        return_value = None
        request_type='GET'

        #execute general procedures
        self._general_execute()

        logger.debug('Request string: '+str(request_type)+' - '+str(self.__url_base_ConfigurationManager)+str(self.__url_base_v1)+self.__url_base_views+self.__url_host_wwn_paths+'?$count=16384&$query=ldev.storageDeviceId%20eq%20'+str(self._storage_device_id))
        return_response = self._general_webrequest(request_type=request_type, url_suffix=str(self.__url_base_ConfigurationManager)+str(self.__url_base_v1)+self.__url_base_views+self.__url_host_wwn_paths+'?$count=16384&$query=ldev.storageDeviceId%20eq%20'+str(self._storage_device_id))

        logger.debug('Request response: ' + str(return_response))

        #if it is not a list then make it to one with one element
        if not isinstance(return_response, (list,)):
            return_response = [return_response]

        #create dictionary out of the data
        # host_wwn_paths = {}

        # i = 0
        # for path in return_response:
        #     i += 1
        #     host_wwn_paths[path[self.__json_ldevId]] = ldev

        end = time.time()
        logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
        return(return_response)


    #get pools
    def pools_get(self, poolId=None, timeout:int=30):
        start = time.time()
        return_value = None
        request_type='GET'

        #execute general procedures
        self._general_execute()

        if poolId == None:
            #get the information of all ports
            logger.debug('Request string: '+str(self.__url_base)+self.__url_storages+'/'+str(self._storage_device_id)+str(self.__url_pools))
            return_response = self._general_webrequest(request_type=request_type, url_suffix=self.__url_base+self.__url_storages+'/'+str(self._storage_device_id)+str(self.__url_pools))
            logger.debug('Request response: ' + str(return_response))
            if isinstance(return_response, list):
                #create dictionary out of the response
                pools = {}
                i = 0
                for pool in return_response:
                    i += 1
                    pools[str(pool['poolId'])] = {}
                    pools[str(pool['poolId'])] = pool
                return_value = pools
            else:
                logger.error('Response is not a list. output: '+ str(return_response))
                return_value = -1
        else:
            if str(poolId).isnumeric():
                logger.debug('Request string: '+str(self.__url_base+self.__url_storages+'/'+str(self._storage_device_id)+str(self.__url_pools)+'/'+str(poolId)))
                return_response = self._webrequest(request_type=request_type, url_suffix=self.__url_base+self.__url_storages+'/'+str(self._storage_device_id)+str(self.__url_pools)+'/'+str(poolId))
                return_response = self.__check_response(return_response=return_response, key='all')
                logger.debug('Request response: ' + str(return_response))
                #create dictionary out of the response
                pools = {}
                pools[str(return_response['poolId'])] = {}
                pools[str(return_response['poolId'])] = return_response
                return_value = pools
            else:
                logger.error('Pool Id is not a number ('+str(poolId)+'). Must be between 0 and 127')
                return_value = -1

        end = time.time()
        logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
        return(return_value)

    #get ports
    def ports_get(self, portId=None, logins:bool=True, timeout:int=180):
        start = time.time()
        request_type='GET'

        return_value = None

        #execute general procedures
        self._general_execute()

        '''
        {'CL1-A': {'portId': 'CL1-A',
                 'portType': 'FIBRE',
           'portAttributes': ['MCU'],
                'portSpeed': '8G',
                   'loopId': 'EF',
               'fabricMode': True,
           'portConnection': 'PtoP',
       'lunSecuritySetting': True,
                      'wwn': '50060e8007e2d400'}}
        '''

        if portId == None:
            #get the information of all ports
            if logins == True:
                logger.debug('Request string: '+self.__url_base+self.__url_storages+'/'+self._storage_device_id+self.__url_ports+'?detailInfoType=logins')
                return_response = self._general_webrequest(request_type=request_type, url_suffix=self.__url_base+self.__url_storages+'/'+self._storage_device_id+self.__url_ports+'?detailInfoType=logins', timeout=timeout)
            else:
                logger.debug('Request string: '+str(self.__url_base+self.__url_storages+'/'+str(self._storage_device_id)+str(self.__url_ports)))
                return_response = self._general_webrequest(request_type=request_type, url_suffix=self.__url_base+self.__url_storages+'/'+self._storage_device_id+self.__url_ports, timeout=timeout)

            logger.debug('Request response: ' + str(return_response))
            if isinstance(return_response, list):
                ports = {}
                i = 0
                for port in return_response:
                    i += 1
                    ports[str(port['portId'])] = {}
                    ports[str(port['portId'])] = port
                return_value = ports
            else:
                logger.error('Response is not a list. output: '+ str(return_response))
                return_value = -1
        else:
            #just one specifig port, login info not available. but class info available
            logger.debug('Request string: '+self.__url_base+self.__url_storages+'/'+self._storage_device_id+self.__url_ports+'/'+str(portId)+'?detailInfoType=class')
            return_response = self._webrequest(request_type=request_type, url_suffix=self.__url_base+self.__url_storages+'/'+str(self._storage_device_id)+str(self.__url_ports)+'/'+str(portId)+'?detailInfoType=class', timeout=timeout)
            return_response = self.__check_response(return_response=return_response, key='all')
            logger.debug('Request response: ' + str(return_response))
            ports = {}
            ports[str(return_response['portId'])] = {}
            ports[str(return_response['portId'])] = return_response
            return_value = ports

        end = time.time()
        logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
        return(return_value)

    # get all ldevs or a specifig ldev
    # TODO: Support more parameters (Page: 420ff Hitachi Ops Center API Configuration Manager REST API Reference Guide)
    #
    def ldevs_get(self, ldevNumber=None, count=16384, timeout:int=1000, defined=True):
        start = time.time()
        #max ldevs 16384
        request_type='GET'

        #execute general procedures
        self._general_execute()

        if ldevNumber == None:
            if timeout == 30:
                timeout = 600
            if defined == True:
                # Get only the defined LDEVs, makes more sense, and is much faster.....
                logger.debug('Request string: '+str(self.__url_base+self.__url_storages+'/'+str(self._storage_device_id)+'/ldevs?count='+str(count)+'&ldevOption=defined'))
                return_response = self._general_webrequest(request_type=request_type, url_suffix=self.__url_base+self.__url_storages+'/'+str(self._storage_device_id)+'/ldevs?count='+str(count)+'&ldevOption=defined', timeout=timeout)
            else:
                logger.debug('Request string: '+str(self.__url_base+self.__url_storages+'/'+str(self._storage_device_id)+'/ldevs?count='+str(count)))
                return_response = self._general_webrequest(request_type=request_type, url_suffix=self.__url_base+self.__url_storages+'/'+str(self._storage_device_id)+'/ldevs?count='+str(count), timeout=timeout)
            logger.debug('Request response: ' + str(return_response))
        else:
            if str(ldevNumber).isnumeric():
                logger.debug('Request string: '+str(self.__url_base+self.__url_storages+'/'+str(self._storage_device_id)+'/ldevs/'+str(ldevNumber)))
                return_response = self._webrequest(request_type=request_type, url_suffix=self.__url_base+self.__url_storages+'/'+str(self._storage_device_id)+'/ldevs/'+str(ldevNumber), timeout=timeout)
                return_response = self.__check_response(return_response=return_response, key='all')
                logger.debug('Request response: ' + str(return_response))
            else:
                logger.error('ERROR: response: ldevNumber[dec] "'+str(ldevNumber)+'" is not a decimal ldev number')
                end = time.time()
                logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
                return(-1)

        #if it is not a list then make it to one with one element
        if not isinstance(return_response, (list,)):
            return_response = [return_response]

        #create dictionary out of the data
        ldevs = {}
        #print('Number of storage hostgroups of port ('+ str(portId) +'):', len(return_response))
        i = 0
        for ldev in return_response:
            i += 1
            ldevs[ldev[self.__json_ldevId]] = ldev

        end = time.time()
        logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
        return(ldevs)

    #get hostgroups of one port
    def host_groups_one_port_get(self, portId, timeout:int=600):
        start = time.time()
        request_type='GET'

        #execute general procedures
        self._general_execute()

        '''
        {'CL3-B,0': {'hostGroupId': 'CL3-B,0',
                          'portId': 'CL3-B',
                 'hostGroupNumber': 0,
                   'hostGroupName': '3B-G00',
                        'hostMode': 'LINUX/IRIX',
                 'resourceGroupId': 0,
                       'isDefined': True}}
        '''
        logger.debug('Request string: '+str(self.__url_base+self.__url_storages+'/'+str(self._storage_device_id)+'/host-groups?portId='+portId+'&isUndefined=false&detailInfoType=resourceGroup'))
        return_response = self._general_webrequest(request_type=request_type, url_suffix=self.__url_base+self.__url_storages+'/'+str(self._storage_device_id)+'/host-groups?portId='+portId+'&isUndefined=false&detailInfoType=resourceGroup', timeout=timeout)
        logger.debug('Request response: ' + str(return_response))

        hostGroups = {}
        #print('Number of storage hostgroups of port ('+ str(portId) +'):', len(return_response))
        i = 0
        for hostGroup in return_response:
            if '-G00' not in hostGroup['hostGroupId']:
                i += 1
                #print(str(hostGroup['hostGroupId']), ' hostgroup ' + str(i) + 'of' + str(len(return_response)))
                hostGroups[str(hostGroup['hostGroupId'])] = hostGroup

        end = time.time()
        logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
        return(hostGroups)

    #get host group of all ports
    def host_groups_all_ports_get(self, timeout:int=600):
        start = time.time()
        request_type='GET'

        #execute general procedures
        self._general_execute()

        #get all portIds
        return_response = self.ports_get()
        logger.debug('Request response: ' + str(return_response))

        hostgroups = {}

        i = 0
        for port in return_response:
            #host group infos
            logger.info(port)
            return_response_hostgroup = self.host_groups_one_port_get(portId=port, timeout=timeout)
            for hostgroup in return_response_hostgroup:
                logger.info(hostgroup)
                hostgroups[hostgroup] = return_response_hostgroup[hostgroup]

        end = time.time()
        logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
        return(hostgroups)

    #get luns of one hostgroup
    def luns_get(self, portId_hostGroupId, timeout:int=30):
        start = time.time()
        request_type='GET'

        #execute general procedures
        self._general_execute()

        '''
        {'CL3-B,5,0': {'lunId': 'CL3-B,5,0',
                      'portId': 'CL3-B',
             'hostGroupNumber': 5,
                    'hostMode': 'VMWARE_EX',
                         'lun': 0,
                      'ldevId': 1536,
             'isCommandDevice': False,
               'luHostReserve': {'openSystem': False,
                                 'persistent': False,
                                     'pgrKey': False,
                                  'mainframe': False,
                                 'acaReserve': False},
                            'hostModeOptions': [54, 63, 114],
                              'isAluaEnabled': True,
                      'asymmetricAccessState': 'Active/Optimized'}}}
        '''

        #'CL3-B,5' -> 'CL3-B' and '5'
        port, hostgroup = portId_hostGroupId.split(',')
        logger.debug('Port:'+str(port)+' hostgroup: '+ str(hostgroup))

        logger.debug('Request string: '+str(self.__url_base+self.__url_storages+'/'+str(self._storage_device_id)+'/luns?portId='+str(port)+'&hostGroupNumber='+str(hostgroup)+'&isBasicLunInformation=false&lunOption=ALUA'))
        return_response = self._general_webrequest(request_type=request_type, url_suffix=self.__url_base+self.__url_storages+'/'+str(self._storage_device_id)+'/luns?portId='+str(port)+'&hostGroupNumber='+str(hostgroup)+'&isBasicLunInformation=false&lunOption=ALUA', timeout=timeout)
        logger.debug('Request response: ' + str(return_response))

        #No LUN found in hostgroup
        if return_response == None:
            logger.warning('No LUN(s) found in Hostgroup: '+str(portId_hostGroupId))
            end = time.time()
            logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
            return(None)

        #Internal Error (no hostgroup on port)
        if isinstance(return_response, (list,)):
            if isinstance(return_response[0], (int,)):
                if return_response[0] == -1:
                    logger.error('error message :'+str(return_response))
                    end = time.time()
                    logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
                    return(None)
                else:
                    logger.error('Unknown error')
                    end = time.time()
                    logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
                    return(return_response)

        luns = {}
        i = 0
        for lun in return_response:
            i += 1
            logger.debug('lun information: ' + str(lun))
            luns[str(lun['lunId'])] = lun

        end = time.time()
        logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
        return(luns)

    #get the luns of one hostgroups of one port
    def luns_one_port_get(self, portId, timeout:int=60):
        start = time.time()
        request_type='GET'

        #execute general procedures
        self._general_execute()

        '''
        {'CL3-B,5,0': {'lunId': 'CL3-B,5,0',
                      'portId': 'CL3-B',
             'hostGroupNumber': 5,
                    'hostMode': 'VMWARE_EX',
                         'lun': 0,
                      'ldevId': 1536,
             'isCommandDevice': False,
               'luHostReserve': {'openSystem': False,
                                 'persistent': False,
                                     'pgrKey': False,
                                  'mainframe': False,
                                 'acaReserve': False},
                            'hostModeOptions': [54, 63, 114],
                              'isAluaEnabled': True,
                      'asymmetricAccessState': 'Active/Optimized'}}}
        '''

        #get all hostgroups of a port
        return_response = self.host_groups_one_port_get(portId=portId, timeout=timeout)
        logger.debug('Request response: ' + str(return_response))

        luns = {}
        logger.info('Number of storage hostgroups of port ('+ str(portId) +'): ' + str(len(return_response)))
        i = 0
        for hostGroup in return_response:
            i += 1
            logger.info(str(hostGroup) + ' hostgroup ' + str(i) + 'of' + str(len(return_response)))
            logger.debug('Hostgroup raw data:'+str(return_response[hostGroup]))

            return_response_luns = self.luns_get(portId_hostGroupId=hostGroup)
            logger.debug('Request response: ' + str(return_response_luns))
            if return_response_luns == None:
                #ignore hostgroup -> no luns in this hostgroup
                #logger.warning('No LUN(s) configured in hostgroup:'+str(hostGroup))
                pass
            else:
                for lun in return_response_luns:
                    luns[lun] = return_response_luns[lun]

        end = time.time()
        logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
        if len(luns) == 0:
            return(None)
        else:
            return(luns)

    #get the luns of all hostgroups of one port
    def luns_all_ports_get(self, timeout:int=60):
        start = time.time()
        request_type='GET'

        #execute general procedures
        self._general_execute()

        #get all portIds
        return_response = self.ports_get()
        logger.debug('Request response: ' + str(return_response))

        luns = {}
        i = 0
        for port in return_response:
            #host group infos
            logger.info(port)
            return_response_luns = self.luns_one_port_get(portId=port, timeout=timeout)
            logger.debug('Request response: ' + str(return_response_luns))
            if not return_response_luns == None:
                for lun in return_response_luns:
                    luns[lun] = return_response_luns[lun]

        end = time.time()
        logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
        return(luns)

    #get the wwns of one hostgroups of one port
    def wwns_get(self, portId_hostGroupId, timeout:int=30):
        start = time.time()
        request_type='GET'

        #execute general procedures
        self._general_execute()

        #'CL3-B,5' -> 'CL3-B' and '5'
        port, hostgroup = portId_hostGroupId.split(',')

        logger.debug('Request string: '+str(self.__url_base+self.__url_storages+'/'+str(self._storage_device_id)+'/host-wwns?portId='+str(port)+'&hostGroupNumber='+str(hostgroup)))
        return_response = self._general_webrequest(request_type=request_type, url_suffix=self.__url_base+self.__url_storages+'/'+str(self._storage_device_id)+'/host-wwns?portId='+str(port)+'&hostGroupNumber='+str(hostgroup), timeout=timeout)
        logger.debug('Request response: ' + str(return_response))

        '''
        [{'hostWwnId': 'CL1-B,6,2400000087805858', 'portId': 'CL1-B', 'hostGroupNumber': 6, 'hostGroupName': 'CB500_Blade4_pepalma', 'hostWwn': '2400000087805858', 'wwnNickname': 'pepalma'}]
        '''

        #No WWN found in hostgroup
        if return_response == None:
            logger.warning('Warning: No WWN found in Hostgroup '+str(portId_hostGroupId))
            end = time.time()
            logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
            return(None)

        #Internal Error (no hostgroup on port)
        if isinstance(return_response, (list,)):
            if isinstance(return_response[0], (int,)):
                if return_response[0] == -1:
                    logger.error('error message :'+str(return_response))
                    end = time.time()
                    logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
                    return(None)
                else:
                    logger.error('Unknown error')
                    end = time.time()
                    logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
                    return(return_response)

        wwns = {}
        #print('Number of storage hostgroups of port ('+ str(portId) +'):', len(return_response))
        i = 0
        for wwn in return_response:
            i += 1
            wwns[wwn[self.__json_hostWwnId]] = wwn

        end = time.time()
        logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
        return(wwns)

    #get the wwns of all hostgroups of one port
    def wwns_one_port_get(self, portId, timeout:int=30):
        start = time.time()
        request_type='GET'

        #execute general procedures
        self._general_execute()

        #get all hostgroups of a port
        return_response = self.host_groups_one_port_get(portId=portId, timeout=timeout)
        logger.debug('Request response: ' + str(return_response))

        wwns = {}
        logger.info('Number of storage hostgroups of port ('+ str(portId) +'): ' + str(len(return_response)))
        i = 0
        for hostGroup in return_response:
            i += 1
            logger.info(str(hostGroup) + ' hostgroup ' + str(i) + 'of' + str(len(return_response)))
            logger.debug('Hostgroup raw data:'+str(return_response[hostGroup]))

            return_response_wwns = self.wwns_get(portId_hostGroupId=hostGroup, timeout=timeout)
            logger.debug('Request response: ' + str(return_response_wwns))
            if return_response_wwns == None:
                #ignore hostgroup -> no wwn(s) in this hostgroup
                pass
            else:
                for wwn in return_response_wwns:
                    wwns[wwn] = return_response_wwns[wwn]

        end = time.time()
        logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
        if len(wwns) == 0:
            return(None)
        else:
            return(wwns)

    #get the wwns of all hostgroups of all ports
    def wwns_all_ports_get(self, timeout:int=300):
        start = time.time()
        request_type='GET'

        #execute general procedures
        self._general_execute()

        #get all portIds
        return_response = self.ports_get()
        logger.debug('Request response: ' + str(return_response))

        #create dictionary out of the data
        wwns = {}
        i = 0
        for port in return_response:
            #host group infos
            logger.info(port)
            return_response_wwns = self.wwns_one_port_get(portId=port, timeout=timeout)
            logger.debug('Request response: ' + str(return_response_wwns))
            if not return_response_wwns == None:
                for wwn in return_response_wwns:
                    wwns[wwn] = return_response_wwns[wwn]

        end = time.time()
        logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
        return(wwns)

    #get all replication configuration
    def replication_get(self, replicationType=None, timeout:int=1000):
        start = time.time()
        request_type='GET'

        #execute general procedures
        self._general_execute()

        if replicationType == None:
            logger.debug('Request string: '+str(self.__url_base+self.__url_storages+'/'+str(self._storage_device_id)+self.__url_remotereplication))
            return_response = self._general_webrequest(request_type=request_type, url_suffix=self.__url_base+self.__url_storages+'/'+str(self._storage_device_id)+self.__url_remotereplication, timeout=timeout)
            logger.debug('Request response: ' + str(return_response))
        else:
            if str(replicationType) in ['GAD', 'UR', 'TC']:
                logger.debug('Request string: '+str(self.__url_base+self.__url_remotereplication+'?replicationType='+str(replicationType)))
                return_response = self._general_webrequest(request_type=request_type, url_suffix=self.__url_base+self.__url_storages+'/'+str(self._storage_device_id)+self.__url_remotereplication+'?replicationType='+str(replicationType), timeout=timeout)
                logger.debug('Request response: ' + str(return_response))
            else:
                logger.error('ERROR: the replicationType ('+str(replicationType)+') is not supported. Specify "GAD", "UR", "TC".')
                end = time.time()
                logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
                return(-1)

        #if it is not a list then make it to one with one element
        if not isinstance(return_response, (list,)):
            return_response = [return_response]

        #create dictionary out of the data
        replications = {}
        #print('Number of storage hostgroups of port ('+ str(portId) +'):', len(return_response))
        i = 0
        for replication in return_response:
            i += 1
            replications[replication[self.__json_remoteReplicationId]] = replication

        end = time.time()
        logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
        return(replications)

    #get snapshotgroups or a specific snapshotgroup
    def snapshotgroups_get(self, snapshotGroupName=None, timeout:int=30):
        start = time.time()
        request_type='GET'

        #execute general procedures
        self._general_execute()

        if snapshotGroupName == None:
            logger.debug('Request string: '+str(self.__url_base+self.__url_storages)+'/'+str(self._storage_device_id)+str(self.__url_snapshotgroups))
            return_response = self._general_webrequest(request_type=request_type, url_suffix=str(self.__url_base+self.__url_storages)+'/'+str(self._storage_device_id)+str(self.__url_snapshotgroups), timeout=timeout)
            logger.debug('Request response: ' + str(return_response))
        else:
            logger.debug('Request string: '+str(self.__url_base+self.__url_storages)+'/'+str(self._storage_device_id)+self.__url_snapshotgroups+'/'+str(snapshotGroupName))
            return_response = self._general_webrequest(request_type=request_type, url_suffix=str(self.__url_base+self.__url_storages)+'/'+str(self._storage_device_id)+self.__url_snapshotgroups+'/'+str(snapshotGroupName), timeout=timeout)
            logger.debug('Request response: ' + str(return_response))

        #if it is not a list then make it to one with one element
        if not isinstance(return_response, (list,)):
            return_response = [return_response]

        #create dictionary out of the data
        snapshotgroups = {}
        #print('Number of storage hostgroups of port ('+ str(portId) +'):', len(return_response))
        i = 0
        for snapshotgroup in return_response:
            i += 1
            snapshotgroups[snapshotgroup[self.__json_snapshotGroupName]] = snapshotgroup

        end = time.time()
        logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
        return(snapshotgroups)

    #get all snapshots or the snapshots of a specific ldev
    def snapshots_get(self, ldevNumber=None, timeout:int=360):
        start = time.time()
        request_type='GET'

        #execute general procedures
        self._general_execute()

        if ldevNumber == None:
            logger.debug('Request string: '+str(self.__url_base+self.__url_storages+'/'+str(self._storage_device_id)+self.__url_snapshotsall))
            return_response = self._general_webrequest(request_type=request_type, url_suffix=self.__url_base+self.__url_storages+'/'+str(self._storage_device_id)+self.__url_snapshotsall, timeout=timeout)
            logger.debug('Request response: ' + str(return_response))
        else:
            if str(ldevNumber).isnumeric():
                logger.debug('Request string: '+str(self.__url_base+self.__url_storages+'/'+str(self._storage_device_id)+'/snapshots?pvolLdevId='+str(ldevNumber)))
                return_response = self._general_webrequest(request_type=request_type, url_suffix=self.__url_base+self.__url_storages+'/'+str(self._storage_device_id)+'/snapshots?pvolLdevId='+str(ldevNumber), timeout=timeout)
                logger.debug('Request response: ' + str(return_response))
            else:
                logger.error('ERROR: response: ldevNumber "'+str(ldevNumber)+'" is not a number.')
                end = time.time()
                logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
                return(-1)

        #if it is not a list then make it to one with one element
        if not isinstance(return_response, (list,)):
            return_response = [return_response]

        #create dictionary out of the data
        snapshots = {}
        #print('Number of storage hostgroups of port ('+ str(portId) +'):', len(return_response))
        i = 0
        for snapshot in return_response:
            i += 1
            if self.__json_snapshotReplicationId in snapshot:
                snapshots[snapshot[self.__json_snapshotReplicationId]] = snapshot
            else:
                snapshots[snapshot[self.__json_snapshotId]] = snapshot

        end = time.time()
        logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
        return(snapshots)

    #create snapshots
    #not done
    def snapshots_create(self, pvolLdevId=None, snapshotGroupName=None, snapshotPoolId=None, isClone=False, isConsistencyGroup=True,
                        autoSplit=True):

        start = time.time()
        request_type='POST'

        #execute general procedures
        self._general_execute()

        #create session token
        self._session_create()

        if pvolLdevId == None:
            logger.error('ERROR: response: You must specify a pvolLdevId.')
            end = time.time()
            logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
            return(-1)
        else:
            if str(pvolLdevId).isnumeric():
                #if no snapshotgroup is specified the create a uuid4 RFC4122 string
                if snapshotGroupName==None:
                    #snapshotgroup string can be at max 32 characters
                    #create uuid4.hex (RFC 4122) string -> 'aa77aba4d3484b358fd509a43b9b44ab' 32 chars
                    snapshotGroupName = str(uuid.uuid4().hex)

                body = '''
                {
                "snapshotGroupName": "snapshotGroup",
                "snapshotPoolId": 5,
                "pvolLdevId": 3555,
                "isConsistencyGroup": true,
                "autoSplit": true
                }
                '''

                body = '''{"snapshotGroupName": str(snapshotGroupName),
                   "snapshotPoolId": str(snapshotPoolId),
                   "pvolLdevId": str(pvolLdevId),
                   "isClone": isClone,
                   "isConsistencyGroup": isConsistencyGroup,
                   "autoSplit": autoSplit,
                   "isDataReductionForceCopy": True
                  }'''

                logger.debug('Request string: '+str(self.__url_base+self.__url_storages+'/'+str(self._storage_device_id)+'/snapshots', body=body))
                return_response=self._webrequest(request_type=request_type, url_suffix=self.__url_base+self.__url_storages+'/'+str(self._storage_device_id)+'/snapshots', body=body)
                logger.debug('Request response: ' + str(return_response))
            else:
                logger.error('ERROR: response: pvolLdevId "'+str(pvolLdevId)+'" is not a valid number.')
                end = time.time()
                logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
                return(-1)

        if len(return_response) == 3:
            if return_response[0] == 0:
                #success

                #remove session token
                self._session_delete()

                end = time.time()
                logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
                return(return_response[2])
            else:
                logger.warning('WARNING: response status:'+str(return_response[1])+', response reason:'+str(return_response[2]))
                end = time.time()
                logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
                return(None)
        else:
            logger.error('ERROR: response:'+str(return_response))
            end = time.time()
            logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
            return(-1)

    #resync snapshots
    #not done
    def snapshots_resync(self, snapshotGroupName=None, autoSplit=True):
        start = time.time()
        request_type='PUT'

        #execute general procedures
        self._general_execute()

        #create session token
        self._session_create()


        body = json.dumps({"parameters": {"autoSplit": autoSplit}})
        logger.debug('body: ' + str(body))

        if snapshotGroupName == None:
            logger.error('ERROR: response: You must specify a snapshotGroupName.')
            end = time.time()
            logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
            return(-1)
        else:
            logger.debug('Request string: '+str(self.__url_base+self.__url_storages+'/'+self._storage_device_id+self.__url_snapshotgroups+'/'+str(snapshotGroupName)+'/actions/resync/invoke', body=body))
            return_response=self._webrequest(request_type=request_type, url_suffix=self.__url_base+self.__url_storages+'/'+self._storage_device_id+self.__url_snapshotgroups+'/'+str(snapshotGroupName)+'/actions/resync/invoke', body=body)
            logger.debug('Request response: ' + str(return_response))

        if len(return_response) == 3:
            if return_response[0] == 0:
                #success

                #remove session token
                self._session_delete()

                end = time.time()
                logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
                return(return_response[2])
            else:
                logger.warning('WARNING: response status:'+str(return_response[1])+', response reason:'+str(return_response[2]))
                end = time.time()
                logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
                return(None)
        else:
            logger.error('ERROR: response:'+str(return_response))
            end = time.time()
            logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
            return(-1)

    #delete snapshots
    #not done
    def snapshots_delete(self, snapshotGroupName=None):
        start = time.time()
        request_type='DELETE'

        #execute general procedures
        self._general_execute()

        #create session token
        self._session_create()

        request_type='DELETE'
        if snapshotGroupName == None:
            logger.error('ERROR: response: You must specify a snapshotGroupName.')
            end = time.time()
            logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
            return(-1)
        else:
            logger.debug('Request string: '+str(self.__url_base+self.__url_storages+'/'+self._storage_device_id+self.__url_snapshotgroups+'/'+str(snapshotGroupName)))
            return_response = self._webrequest(request_type=request_type, url_suffix=self.__url_base+self.__url_storages+'/'+self._storage_device_id+self.__url_snapshotgroups+'/'+str(snapshotGroupName))
            logger.debug('Request response: ' + str(return_response))

        if len(return_response) == 3:
            if return_response[0] == 0:
                #success

                #remove session token
                self._session_delete()

                return(return_response[2])
            else:
                logger.warning('WARNING: response status:'+str(return_response[1])+', response reason:'+str(return_response[2]))
                end = time.time()
                logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
                return(None)
        else:
            logger.error('ERROR: response:'+str(return_response))
            end = time.time()
            logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
            return(-1)
