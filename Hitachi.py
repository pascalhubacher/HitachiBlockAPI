"""
This library provides an easy way to script tasks for the Hitachi Storage Arrays.

Please be aware that when passing arguments to methods that take \*\*kwargs, the exact
parameters that can be passed can be found in the REST API guide.
"""

import http.client
import json
import ssl
from base64 import b64encode
import logging
import time
import uuid

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
VERSION = "0.9.5"

class RestAPI:
    '''This Class can be used to : '''
    
    def __init__(self, protocol='https://', storage_fqdn_ip='127.0.0.1', username='maintenance', password='raid-maintenance'):
        self._ip_fqdn = storage_fqdn_ip
        self.__userAndPass = b64encode((username+':'+password).encode('utf-8')).decode("ascii")
        self._username = username
        self._protocol = protocol
        self._storage_device_id = None
        self._token = None
        self._session_id = None
        self.__url_base = '/ConfigurationManager/v1/objects'
        self.__url_base_ConfigurationManager = '/ConfigurationManager'
        self.__url_base_v1 = '/v1'
        self.__url_base_objects = '/objects'
        self.__url_resource_lock = '/services/resource-group-service/actions/lock/invoke'
        self.__url_resource_unlock = '/services/resource-group-service/actions/unlock/invoke'
        self.__url_storages = '/storages'
        self.__url_jobs = '/jobs'
        self.__url_sessions = '/sessions'
        self.__url_ports = '/ports'
        self.__url_pools = '/pools'
        self.__url_remotereplication = '/remote-replications'
        self.__url_snapshotgroups = '/snapshot-groups'
        self.__url_snapshotsall = '/snapshot-replications'
        self.__json_data = 'data'
        self.__json_storage_device_id = 'storageDeviceId'
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
    
    #extecutes the web request
    def _webrequest(self, request_type='GET', url_suffix=None, body=''):
        '''Return the json response of the webrequest'''
        start = time.time()
        
        if url_suffix == None:
            #set standar url suffix
            url = self._protocol+self._ip_fqdn+self.__url_base+self.__url_storages
        else:
            #use the url suffix that was set in the function call
            url = self._protocol+self._ip_fqdn+url_suffix    

        #if already a token is set then use it otherwise use the user and password
        if self._token is None:
            logger.debug('No token found. Use user ('+str(self._username)+') and password used')
            #user and password
            headers = {'Accept':'application/json', 'Content-Type':'application/json', 'Authorization' : 'Basic %s' %  self.__userAndPass}
        else:
            #token
            logger.debug('token ('+str(self._token)+') is used')
            headers = {'Accept':'application/json', 'Content-Type':'application/json', 'Authorization' : 'Session '+str(self._token)}

        #create https connection, unverified connection
        connection = http.client.HTTPSConnection(self._ip_fqdn, context=ssl._create_unverified_context())

        # Send request
        connection.request(method=request_type, url=url, headers=headers, body=body)
        
        # Get the response
        response = connection.getresponse()
        # Display the response status
        #print()
        #print ("Status = ", response.status)
        # 200 Ok
        # 202 Accepted The request has been accepted for processing, but the processing has not been completed.
        if response.status == http.client.OK or response.status == http.client.ACCEPTED:
            #print("connection successful!")
            #read the json bytes
            json_response_bytes = response.read()
            #print(json_response_bytes)
            #convert the json response to a utf-8 string
            json_response_string = str(json_response_bytes, encoding='utf8')
            #print(json_response_string)
            #convet the string into python json
            if not len(json_response_string) == 0:
                return_response = json.loads(json_response_string)
                return_response = [0, response.status, return_response]
            else:
                return_response = [0, response.status, '']
        else:
            #print()
            #print('Server response:', response.status, '-', response.reason)
            logger.error('Internal Error:')
            return_response = [-1, response.status, response.reason]
            
        #close connection
        connection.close()
        end = time.time()
        logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
        return(return_response)
    
    #general webrequest that creates/deletes sessions
    def _general_webrequest(self, request_type, url_suffix=None, body=''):
        start = time.time()

        #create session token
        self._session_create()
        
        return_response = self._webrequest(request_type=request_type, url_suffix=url_suffix, body=body)

        if len(return_response) == 3:
            if return_response[0] == 0:
                #success
                
                #remove session token
                self._session_delete()

                if not len(return_response[2]) == 0:
                    #remove the data key
                    if self.__json_data in return_response[2]:
                        if not len(return_response[2][self.__json_data]) == 0:
                            end = time.time()
                            logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
                            return(return_response[2][self.__json_data])
                        else:
                            end = time.time()
                            logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
                            return(None)
                    else:
                        #no list
                        end = time.time()
                        logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
                        return(return_response[2])
                else:
                    end = time.time()
                    logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
                    return(None)
                    
            else:
                logger.warning('WARNING: response status:'+str(return_response[1])+', response reason:'+str(return_response[2]), ', request:'+str(url_suffix))
                end = time.time()
                logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
                return(return_response)
        else:
            logger.error('ERROR: response:'+str(return_response))
            end = time.time()
            logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
            return(return_response)

    #execute in all functions
    def _general_execute(self):
        start = time.time()
        #set StorageDeviceId if not already set
        if self._storage_device_id == None:
            self._storage_device_id_set()
        
        end = time.time()
        logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")

        return(None)

    #gets the storge device id
    def _storage_device_id_get(self):
        '''This function is '''

        start = time.time()
        request_type = 'GET'
        
        logger.debug('Request string: '+str(self.__url_base+self.__url_storages))
        return_response=self._webrequest(request_type=request_type, 
                                     url_suffix=self.__url_base+self.__url_storages)
        logger.debug('Request response: ' + str(return_response))

        '''
        {
            "data": [
                {
                    "storageDeviceId": "800000058068",
                    "model": "VSP G1000",
                    "serialNumber": 58068,
                    "svpIp": "10.70.4.145"
                }
            ]
        }
        '''
        if len(return_response) == 3:
            if return_response[0] == 0:
                #success
                end = time.time()
                logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
                return(return_response[2][self.__json_data])
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

    #set storage device id        
    def _storage_device_id_set(self, element_number=0):
        start = time.time()
        request_type = 'GET'

        logger.debug('Request string: '+str(self.__url_base+self.__url_storages))
        return_response=self._webrequest(request_type=request_type, 
                                     url_suffix=self.__url_base+self.__url_storages)
        logger.debug('Request response: ' + str(return_response))

        '''
        {
            "data": [
                {
                    "storageDeviceId": "800000058068",
                    "model": "VSP G1000",
                    "serialNumber": 58068,
                    "svpIp": "10.70.4.145"
                }
            ]
        }
        '''
        if len(return_response) == 3:
            if return_response[0] == 0:
                #success
                self._storage_device_id = return_response[2][self.__json_data][int(element_number)][self.__json_storage_device_id]
                end = time.time()
                logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
                return(return_response[2][self.__json_data][int(element_number)][self.__json_storage_device_id])
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
    
    #get session id
    def _session_get(self):
        start = time.time()
        request_type='GET'

        #execute general procedures
        self._general_execute()

        logger.debug('Request string: '+str(self.__url_base+self.__url_storages+'/'+self._storage_device_id+self.__url_sessions))
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
        if len(return_response) == 3:
            if return_response[0] == 0:
                #success
                #self._storage_device_id = return_response[2]['data'][int(element_number)]['storageDeviceId']
                end = time.time()
                logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
                return(return_response[2][self.__json_data])
            else:
                logger.warning('WARNING: response status:'+str(return_response[1])+', response reason:'+str(return_response[2]))
                end = time.time()
                logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")                
                return(None)
        else:
            end = time.time()
            logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
            logger.error('ERROR: response:'+str(return_response))
            return(-1)
   
    #create session
    def _session_create(self):
        '''
        '''
        start = time.time()
        request_type='POST'

        #execute general procedures
        self._general_execute()

        logger.debug('Request string: '+str(self.__url_base+self.__url_storages+'/'+self._storage_device_id+self.__url_sessions))
        return_response=self._webrequest(request_type=request_type, url_suffix=self.__url_base+self.__url_storages+'/'+self._storage_device_id+self.__url_sessions)
        logger.debug('Request response: ' + str(return_response))

        '''
        {
            "token": "74014a6e-a4b2-4b87-8021-de0ef3e92bde",
            "sessionId": 3
        }
        -> [0, 200, {'token': '74014a6e-a4b2-4b87-8021-de0ef3e92bde', 'sessionId': 3}]
        '''

        if len(return_response) == 3:
            if return_response[0] == 0:
                #success
                #print(return_response)
                self._token = return_response[2][self.__json_token]
                self._session_id = return_response[2][self.__json_sessionId]
                end = time.time()
                logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
                return[return_response[2]]
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
        
    #delete session
    def _session_delete(self):
        '''
        '''
        start = time.time()
        request_type='DELETE'

        #execute general procedures
        self._general_execute()
        
        if self._session_id == None:
            return('WARNING: nothing done as no session was created')
        else:
            logger.debug('Request string: '+str(self.__url_base+self.__url_storages+'/'+str(self._storage_device_id)+self.__url_sessions+'/'+str(self._session_id)))
            return_response = self._webrequest(request_type=request_type, url_suffix=self.__url_base+self.__url_storages+'/'+str(self._storage_device_id)+self.__url_sessions+'/'+str(self._session_id))
            logger.debug('Request response: ' + str(return_response))

            if len(return_response) == 3:
                if return_response[0] == 0:
                    #success
                    self._token=None
                    self._session_id=None
                    end = time.time()
                    logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
                    return(return_response)
                else:
                    end = time.time()
                    logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
                    logger.warning('WARNING: response status:'+str(return_response[1])+', response reason:'+str(return_response[2]))
                    return(None)
            else:
                end = time.time()
                logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
                logger.error('ERROR: response:'+str(return_response))
                return(-1)
    
    #get jobs
    def _jobs_get(self):
        '''
        '''
        start = time.time()
        request_type='GET'

        #execute general procedures
        self._general_execute()

        #create session token
        self._session_create()

        logger.debug('Request string: '+str(self.__url_base+self.__url_storages+'/'+self._storage_device_id+self.__url_jobs))
        return_response = self._general_webrequest(request_type=request_type, url_suffix=self.__url_base+self.__url_storages+'/'+self._storage_device_id+self.__url_jobs)       
        logger.debug('Request response: ' + str(return_response))
        end = time.time()
        logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
        return(return_response)
        
    #get last job
    def _jobs_last_get(self):
        '''
        '''
        start = time.time()

        return_response = self._jobs_get()
        logger.debug('Request response: ' + str(return_response))

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
    def _jobs_by_id_get(self, jobId=None):
        '''
        '''
        start = time.time()

        return_response = self._jobs_get()
        logger.debug('Request response: ' + str(return_response))

        if not jobId == None:
            for job in return_response:
                if str(job['jobId']) == str(jobId):
                    end = time.time()
                    logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
                    return(job)
            
            logger.error('ERROR: response: jobId: "'+str(jobId)+'" is not found. Please specify an existing jobId.')
            end = time.time()
            logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
            return(-1)
        else:
            logger.error('ERROR: response: jobId is "None". Please specify a valid jobId.')
            end = time.time()
            logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
            return(-1)
    
    
        #get host groups of one port
    
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
    def resource_group_get(self):
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
        return_response = self._general_webrequest(request_type=request_type, url_suffix=self.__url_base+self.__url_storages + '/' + str(self._storage_device_id) + '/resource-groups')
        logger.debug('Request response: ' + str(return_response))

        end = time.time()
        logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
        return(return_response)

    #get pools
    def pools_get(self, poolId=None):
        start = time.time()
        request_type='GET'

        #execute general procedures
        self._general_execute()

        if poolId == None:
            #get the information of all ports
            logger.debug('Request string: '+str(self.__url_base)+self.__url_storages+'/'+str(self._storage_device_id)+str(self.__url_pools))
            return_response = self._general_webrequest(request_type=request_type, url_suffix=self.__url_base+self.__url_storages+'/'+str(self._storage_device_id)+str(self.__url_pools))
            logger.debug('Request response: ' + str(return_response))
        else:
            if str(poolId).isnumeric():
                logger.debug('Request string: '+str(self.__url_base+self.__url_storages+'/'+str(self._storage_device_id)+str(self.__url_pools)+'/'+str(poolId)))
                return_response = self._general_webrequest(request_type=request_type, url_suffix=self.__url_base+self.__url_storages+'/'+str(self._storage_device_id)+str(self.__url_pools)+'/'+str(poolId))
                logger.debug('Request response: ' + str(return_response))
            else:
                logger.error('Pool Id is not a number ('+str(poolId)+'). Must be between 0 and 127')
                return(-1)

        #if it is not a list then make it to one with one element
        if not isinstance(return_response, (list,)):
            return_response = [return_response]

        pools = {}
        i = 0
        for pool in return_response:
            i += 1
            pools[str(pool['poolId'])] = {}
            pools[str(pool['poolId'])] = pool
        
        end = time.time()
        logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
        return(pools)

    #get ports
    def ports_get(self, portId=None, logins=None):
        start = time.time()
        request_type='GET'

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

        if not (portId == None):
            if logins == None:
                #get the information of all ports
                logger.debug('Request string: '+str(self.__url_base+self.__url_storages+'/'+str(self._storage_device_id)+str(self.__url_ports)+'?portId='+str(portId)))
                return_response = self._general_webrequest(request_type=request_type, url_suffix=self.__url_base+self.__url_storages+'/'+str(self._storage_device_id)+str(self.__url_ports)+'?portId='+str(portId))
                logger.debug('Request response: ' + str(return_response))
            else:
                logger.debug('Request string: '+str(self.__url_base+self.__url_storages+'/'+str(self._storage_device_id)+str(self.__url_ports)+'?portId='+str(portId)+'detailInfoType=logins'))
                return_response = self._general_webrequest(request_type=request_type, url_suffix=self.__url_base+self.__url_storages+'/'+str(self._storage_device_id)+str(self.__url_ports)+'?portId='+str(portId)+'detailInfoType=logins')
                logger.debug('Request response: ' + str(return_response))
        else:
            if logins == None:
                #
                logger.debug('Request string: '+str(self.__url_base+self.__url_storages+'/'+str(self._storage_device_id)+str(self.__url_ports)))
                return_response = self._general_webrequest(request_type=request_type, url_suffix=self.__url_base+self.__url_storages+'/'+str(self._storage_device_id)+str(self.__url_ports))
                logger.debug('Request response: ' + str(return_response))
            else:
                logger.debug('Request string: '+str(self.__url_base+self.__url_storages+'/'+str(self._storage_device_id)+str(self.__url_ports)+'?detailInfoType=logins'))
                return_response = self._general_webrequest(request_type=request_type, url_suffix=self.__url_base+self.__url_storages+'/'+str(self._storage_device_id)+str(self.__url_ports)+'?detailInfoType=logins')
                logger.debug('Request response: ' + str(return_response))

        ports = {}
        #print('Number of storage ports:', len(return_response))
        i = 0
        for port in return_response:
            i += 1
            #print(str(port['portId']), 'port ' + str(i) + 'of' + str(len(return_response)))
            ports[str(port['portId'])] = {}
            ports[str(port['portId'])] = port
        
        end = time.time()
        logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
        return(ports)

    #get hostgroups of one port
    def host_groups_one_port_get(self, portId):
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
        return_response = self._general_webrequest(request_type=request_type, url_suffix=self.__url_base+self.__url_storages+'/'+str(self._storage_device_id)+'/host-groups?portId='+portId+'&isUndefined=false&detailInfoType=resourceGroup')
        logger.debug('Request response: ' + str(return_response))

        hostGroups = {}
        #print('Number of storage hostgroups of port ('+ str(portId) +'):', len(return_response))
        i = 0
        for hostGroup in return_response:
            i += 1
            #print(str(hostGroup['hostGroupId']), ' hostgroup ' + str(i) + 'of' + str(len(return_response)))
            hostGroups[str(hostGroup['hostGroupId'])] = hostGroup

        end = time.time()
        logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
        return(hostGroups)

    #get host group of all ports
    def host_groups_all_ports_get(self):
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
            return_response_hostgroup = self.host_groups_one_port_get(portId=port)
            for hostgroup in return_response_hostgroup:
                logger.info(hostgroup)
                hostgroups[hostgroup] = return_response_hostgroup[hostgroup]

        end = time.time()
        logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
        return(hostgroups)

    #get luns of one hostgroup
    def luns_get(self, portId_hostGroupId):
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
        return_response = self._general_webrequest(request_type=request_type, url_suffix=self.__url_base+self.__url_storages+'/'+str(self._storage_device_id)+'/luns?portId='+str(port)+'&hostGroupNumber='+str(hostgroup)+'&isBasicLunInformation=false&lunOption=ALUA')
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
    def luns_one_port_get(self, portId):
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
        return_response = self.host_groups_one_port_get(portId=portId)
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
    def luns_all_ports_get(self):
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
            return_response_luns = self.luns_one_port_get(portId=port)
            logger.debug('Request response: ' + str(return_response_luns))
            if not return_response_luns == None:
                for lun in return_response_luns:
                    luns[lun] = return_response_luns[lun]

        end = time.time()
        logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
        return(luns)      

    #get the wwns of one hostgroups of one port
    def wwns_get(self, portId_hostGroupId):
        start = time.time()
        request_type='GET'

        #execute general procedures
        self._general_execute()

        #'CL3-B,5' -> 'CL3-B' and '5'
        port, hostgroup = portId_hostGroupId.split(',')

        logger.debug('Request string: '+str(self.__url_base+'/host-wwns?portId='+str(port)+'&hostGroupNumber='+str(hostgroup)))
        return_response = self._general_webrequest(request_type=request_type, url_suffix=self.__url_base+'/host-wwns?portId='+str(port)+'&hostGroupNumber='+str(hostgroup))
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
    def wwns_one_port_get(self, portId):
        start = time.time()
        request_type='GET'

        #execute general procedures
        self._general_execute()

        #get all hostgroups of a port
        return_response = self.host_groups_one_port_get(portId=portId)
        logger.debug('Request response: ' + str(return_response))

        wwns = {}
        logger.info('Number of storage hostgroups of port ('+ str(portId) +'): ' + str(len(return_response)))
        i = 0
        for hostGroup in return_response:
            i += 1
            logger.info(str(hostGroup) + ' hostgroup ' + str(i) + 'of' + str(len(return_response)))
            logger.debug('Hostgroup raw data:'+str(return_response[hostGroup]))

            return_response_wwns = self.wwns_get(portId_hostGroupId=hostGroup)
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
    def wwns_all_ports_get(self):
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
            return_response_wwns = self.wwns_one_port_get(portId=port)
            logger.debug('Request response: ' + str(return_response_wwns))
            if not return_response_wwns == None:
                for wwn in return_response_wwns:
                    wwns[wwn] = return_response_wwns[wwn]

        end = time.time()
        logger.debug('total time used: ' + str("{0:05.1f}".format(end-start)) + "sec")
        return(wwns)

    #get all replication configuration
    def replication_get(self, replicationType=None):
        start = time.time()
        request_type='GET'
                
        #execute general procedures
        self._general_execute()

        if replicationType == None:
            logger.debug('Request string: '+str(self.__url_base+self.__url_remotereplication))
            return_response = self._general_webrequest(request_type=request_type, url_suffix=self.__url_base+self.__url_remotereplication)
            logger.debug('Request response: ' + str(return_response))
        else:
            if str(replicationType) in ['GAD', 'UR', 'TC']:
                logger.debug('Request string: '+str(self.__url_base+self.__url_remotereplication+'?replicationType='+str(replicationType)))
                return_response = self._general_webrequest(request_type=request_type, url_suffix=self.__url_base+self.__url_remotereplication+'?replicationType='+str(replicationType))
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

    #get all ldevs or a specifig ldev
    def ldevs_get(self, ldevNumber=None, count=16384):
        start = time.time()
        #max ldevs 16384
        request_type='GET'

        #execute general procedures
        self._general_execute()
        
        if ldevNumber == None:
            logger.debug('Request string: '+str(self.__url_base+self.__url_storages+'/'+str(self._storage_device_id)+'/ldevs?count='+str(count)))
            return_response = self._general_webrequest(request_type=request_type, url_suffix=self.__url_base+self.__url_storages+'/'+str(self._storage_device_id)+'/ldevs?count='+str(count))
            logger.debug('Request response: ' + str(return_response))
        else:
            if str(ldevNumber).isnumeric():
                logger.debug('Request string: '+str(self.__url_base+self.__url_storages+'/'+str(self._storage_device_id)+'/ldevs/'+str(ldevNumber)))
                return_response = self._general_webrequest(request_type=request_type, url_suffix=self.__url_base+self.__url_storages+'/'+str(self._storage_device_id)+'/ldevs/'+str(ldevNumber))
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
        
    #get snapshotgroups or a specific snapshotgroup
    def snapshotgroups_get(self, snapshotGroupName=None):
        start = time.time()
        request_type='GET'

        #execute general procedures
        self._general_execute()

        if snapshotGroupName == None:
            logger.debug('Request string: '+str(self.__url_base+self.__url_storages)+'/'+str(self._storage_device_id)+str(self.__url_snapshotgroups))
            return_response = self._general_webrequest(request_type=request_type, url_suffix=str(self.__url_base+self.__url_storages)+'/'+str(self._storage_device_id)+str(self.__url_snapshotgroups))
            logger.debug('Request response: ' + str(return_response))
        else:
            logger.debug('Request string: '+str(self.__url_base+self.__url_storages)+'/'+str(self._storage_device_id)+self.__url_snapshotgroups+'/'+str(snapshotGroupName))
            return_response = self._general_webrequest(request_type=request_type, url_suffix=str(self.__url_base+self.__url_storages)+'/'+str(self._storage_device_id)+self.__url_snapshotgroups+'/'+str(snapshotGroupName))
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
    def snapshots_get(self, ldevNumber=None):
        start = time.time()
        request_type='GET'

        #execute general procedures
        self._general_execute()

        if ldevNumber == None:
            logger.debug('Request string: '+str(self.__url_base+self.__url_storages+'/'+str(self._storage_device_id)+self.__url_snapshotsall))
            return_response = self._general_webrequest(request_type=request_type, url_suffix=self.__url_base+self.__url_storages+'/'+str(self._storage_device_id)+self.__url_snapshotsall)
            logger.debug('Request response: ' + str(return_response))
        else:
            if str(ldevNumber).isnumeric():
                logger.debug('Request string: '+str(self.__url_base+self.__url_storages+'/'+str(self._storage_device_id)+'/snapshots?pvolLdevId='+str(ldevNumber)))
                return_response = self._general_webrequest(request_type=request_type, url_suffix=self.__url_base+self.__url_storages+'/'+str(self._storage_device_id)+'/snapshots?pvolLdevId='+str(ldevNumber))
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