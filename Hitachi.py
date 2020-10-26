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

# create logger
logger = logging.getLogger('Hitachi.py')
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(module)s - %(lineno)d - %(funcName)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)

# The current version of this library.
VERSION = "0.0.2"

class RestAPI:
    '''This Class can be used to : '''
    
    def __init__(self, protocol='https://', storage_fqdn_ip='127.0.0.1', username='maintenance', password='raid-maintenance'):
        self._ip_fqdn = storage_fqdn_ip
        self.__userAndPass = b64encode((username+':'+password).encode('utf-8')).decode("ascii")
        self._protocol = protocol
        self._storage_device_id = None
        self._token = None
        self._session_id = None
        self.__url_base = '/ConfigurationManager/v1/objects'
        self.__url_storages = '/storages'
        self.__url_jobs = '/jobs'
        self.__url_sessions = '/sessions'
        self.__json_data = 'data'
        self.__json_detail = 'detail'
        self.__json_storage_device_id = 'storageDeviceId'
        self.__json_token = 'token'
        self.__json_sessionId = 'sessionId'
        self.__json_port = 'port'
        self.__json_hostgroup = 'hostgroup'


        #self.__maxConnectionsParallelTotal = 8
        #self.__maxConnectionsParallelGet = 6
    
    #extecutes the web request
    def _webrequest(self, request_type='GET', url_suffix=None, body=''):
        '''Return the json response of the webrequest'''
        
        if url_suffix == None:
            #set standar url suffix
            url = self._protocol+self._ip_fqdn+self.__url_base+self.__url_storages
        else:
            #use the url suffix that was set in the function call
            url = self._protocol+self._ip_fqdn+url_suffix    

        #if already a token is set then use it otherwise use the user and password
        if self._token is None:
            #user and password
            headers = {'Accept':'application/json', 'Content-Type':'application/json', 'Authorization' : 'Basic %s' %  self.__userAndPass}
        else:
            #token
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
            return_response = [-1, response.status, response.reason]
            
        #close connection
        connection.close()
        return(return_response)
    
    #general get part
    def _general_get(self, request_type, url_suffix=None):
        #create session token
        self._session_create()
        
        return_response = self._webrequest(request_type=request_type, url_suffix=url_suffix)

        if len(return_response) == 3:
            if return_response[0] == 0:
                #success
                
                #remove session token
                self._session_delete()

                if not len(return_response[2]) == 0:
                    #remove the data key
                    if self.__json_data in return_response[2]:
                        if not len(return_response[2][self.__json_data]) == 0:
                            return(return_response[2][self.__json_data])
                        else:
                            return(None)
                    else:
                        #no list
                        return(return_response[2])
                else:
                    return(None)
                    
            else:
                print('WARNING: response status:'+str(return_response[1])+', response reason:'+str(return_response[2]), ', request:'+str(url_suffix))
                return(return_response)
        else:
            print('ERROR: response:'+str(return_response))
            return(return_response)

    def _general_execute(self):
        #set StorageDeviceId if not already set
        if self._storage_device_id == None:
            self._storage_device_id_set()

    #gets the storge device id
    def _storage_device_id_get(self):
        '''This function is '''
        request_type = 'GET'
        
        return_response=self._webrequest(request_type=request_type, 
                                     url_suffix=self.__url_base+self.__url_storages)

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
                return(return_response[2][self.__json_data])
            else:
                return('WARNING: response status:'+str(return_response[1])+', response reason:'+str(return_response[2]))
        else:
            return('ERROR: response:'+str(return_response))

    #set storage device id        
    def _storage_device_id_set(self, element_number=0):
        request_type = 'GET'

        return_response=self._webrequest(request_type=request_type, 
                                     url_suffix=self.__url_base+self.__url_storages)
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
                return(return_response[2][self.__json_data][int(element_number)][self.__json_storage_device_id])
            else:
                return('WARNING: response status:'+str(return_response[1])+', response reason:'+str(return_response[2]))
        else:
            return('ERROR: response:'+str(return_response))
    
    #get session id
    def _session_get(self):
        request_type='GET'

        #execute general procedures
        self._general_execute()

        return_response=self._webrequest(request_type=request_type, url_suffix=self.__url_base+self.__url_storages+'/'+self._storage_device_id+self.__url_sessions)
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
                return(return_response[2][self.__json_data])
            else:
                return('WARNING: response status:'+str(return_response[1])+', response reason:'+str(return_response[2]))
        else:
            return('ERROR: response:'+str(return_response))
    
    #create session
    def _session_create(self):
        '''
        '''
        request_type='POST'

        #execute general procedures
        self._general_execute()

        return_response=self._webrequest(request_type=request_type, url_suffix=self.__url_base+self.__url_storages+'/'+self._storage_device_id+self.__url_sessions)
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
                return[return_response[2]]
            else:
                return('WARNING: response status:'+str(return_response[1])+', response reason:'+str(return_response[2]))
        else:
            return('ERROR: response:'+str(return_response))
        
    #delete session
    def _session_delete(self):
        '''
        '''
        request_type='DELETE'

        #execute general procedures
        self._general_execute()
        
        if self._session_id == None:
            return('WARNING: nothing done as no session was created')
        else:
            return_response = self._webrequest(request_type=request_type, url_suffix=self.__url_base+self.__url_storages+'/'+str(self._storage_device_id)+self.__url_sessions+'/'+str(self._session_id))
        
            if len(return_response) == 3:
                if return_response[0] == 0:
                    #success
                    self._token=None
                    self._session_id=None
                    #print(return_response)
                    return(return_response)
                else:
                    return('WARNING: response status:'+str(return_response[1])+', response reason:'+str(return_response[2]))
            else:
                return('ERROR: response:'+str(return_response))
    
    #get jobs
    def _jobs_get(self):
        '''
        '''
        request_type='GET'

        #execute general procedures
        self._general_execute()

        #create session token
        self._session_create()

        return_response = self._general_get(request_type=request_type, url_suffix=self.__url_base+self.__url_storages+'/'+self._storage_device_id+self.__url_jobs)       
        print(return_response)
        
    #get last job
    def _jobs_get_last(self):
        '''
        '''
        return_response = self._jobs_get()
        if return_response == None:
            return('WARNING: no job found')
        else:
            return(return_response[0])
    
    #get job by id
    def _jobs_get_by_jobid(self, jobId=None):
        '''
        '''

        response = self._jobs_get()
        if not jobId == None:
            for job in response:
                if str(job['jobId']) == str(jobId):
                    return(job)
                
            return('ERROR: response: jobId: "'+str(jobId)+'" is not found. Please specify an existing jobId.')
        else:
            return('ERROR: response: jobId is "None". Please specify a valid jobId.')
    
    
        #get host groups of one port
    
    #get ports
    def ports_get(self, portId=None, logins=None):
        #https://10.70.4.145/ConfigurationManager/v1/objects/storages/800000058068/ports?portId=CL1-A&?detailInfoType=logins
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
                return_response = self._general_get(request_type=request_type, url_suffix=self.__url_base+self.__url_storages+'/'+str(self._storage_device_id)+'/ports?portId='+str(portId))
            else:
                return_response = self._general_get(request_type=request_type, url_suffix=self.__url_base+self.__url_storages+'/'+str(self._storage_device_id)+'/ports?portId='+str(portId)+'detailInfoType=logins')
        else:
            if logins == None:
                #
                return_response = self._general_get(request_type=request_type, url_suffix=self.__url_base+self.__url_storages+'/'+str(self._storage_device_id)+'/ports')
            else:
                return_response = self._general_get(request_type=request_type, url_suffix=self.__url_base+self.__url_storages+'/'+str(self._storage_device_id)+'/ports?detailInfoType=logins')

        ports = {}
        #print('Number of storage ports:', len(return_response))
        i = 0
        for port in return_response:
            i += 1
            #print(str(port['portId']), 'port ' + str(i) + 'of' + str(len(return_response)))
            ports[str(port['portId'])] = {}
            ports[str(port['portId'])] = port
        
        return(ports)

    #get hostgroups of one port
    def host_groups_one_port_get(self, portId):
        # https://10.70.4.145/ConfigurationManager/v1/objects/storages/800000058068/host-groups?portId=CL1-A&isUndefined=true&detailInfoType=resourceGroup
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

        return_response = self._general_get(request_type=request_type, url_suffix=self.__url_base+self.__url_storages+'/'+str(self._storage_device_id)+'/host-groups?portId='+portId+'&isUndefined=false&detailInfoType=resourceGroup')
        hostGroups = {}
        #print('Number of storage hostgroups of port ('+ str(portId) +'):', len(return_response))
        i = 0
        for hostGroup in return_response:
            i += 1
            #print(str(hostGroup['hostGroupId']), ' hostgroup ' + str(i) + 'of' + str(len(return_response)))
            hostGroups[str(hostGroup['hostGroupId'])] = hostGroup

        return(hostGroups)

    #get host group of all ports
    def host_groups_all_ports_get(self):
        # https://10.70.4.145/ConfigurationManager/v1/objects/storages/800000058068/host-groups?portId=CL1-A&isUndefined=true&detailInfoType=resourceGroup
        request_type='GET'

        #execute general procedures
        self._general_execute()

        #get all portIds
        return_response = self.ports_get()
        hostgroups = {}
        
        i = 0
        for port in return_response:               
            #host group infos
            return_response_hostgroup = self.host_groups_one_port_get(portId=port)
            for hostgroup in return_response_hostgroup:
                hostgroups[hostgroup] = return_response_hostgroup[hostgroup]

        return(hostgroups)

    #logger added
    #get luns of one hostgroup
    def luns_get(self, portId_hostGroupId):
        #"https://10.10.10.10/ConfigurationManager/v1/objects/storages/800000058068/luns?portId=CL5-B&hostGroupNumber=1&isBasicLunInformation=false&lunOption=ALUA"
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
        return_response = self._general_get(request_type=request_type, url_suffix=self.__url_base+self.__url_storages+'/'+str(self._storage_device_id)+'/luns?portId='+str(port)+'&hostGroupNumber='+str(hostgroup)+'&isBasicLunInformation=false&lunOption=ALUA')
        logger.debug('Request response: ' + str(return_response))

        #No LUN found in hostgroup
        if return_response == None:
            logger.warning('No LUN found in Hostgroup: '+str(portId_hostGroupId))
            return(None)
        
        #Internal Error (no hostgroup on port)
        if isinstance(return_response, (list,)):
            if isinstance(return_response[0], (int,)):
                if return_response[0] == -1:
                    logger.error('error message :'+str(return_response))
                    return(None)
                else:
                    logger.error('Unknown error')
                    return(return_response)

        luns = {}
        i = 0
        for lun in return_response:
            i += 1
            logger.debug('lun information: ' + str(lun))
            luns[str(lun['lunId'])] = lun

        return(luns)
    
    #logger added
    #get the luns of one hostgroups of one port
    def luns_one_port_get(self, portId):
        #"https://10.10.10.10/ConfigurationManager/v1/objects/storages/800000058068/luns?portId=CL5-B&hostGroupNumber=1&isBasicLunInformation=false&lunOption=ALUA"
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
        logger.info('Number of storage hostgroups of port ('+ str(portId) +'):', len(return_response))
        i = 0
        for hostGroup in return_response:
            i += 1
            logger.info(str(hostGroup), ' hostgroup ' + str(i) + 'of' + str(len(return_response)))
            logger.debug('Hostgroup raw data:'+str(return_response[hostGroup]))

            return_response_luns = self.luns_get(portId_hostGroupId=hostGroup)
            logger.debug('Request response: ' + str(return_response_luns))
            if return_response_luns == None:
                #ignore hostgroup -> no luns in this hostgroup
                logger.warning('No lun configured in hostgroup:'+str(hostGroup))
                pass
            else:
                for lun in return_response_luns:
                    luns[lun] = return_response_luns[lun]
        
        if len(luns) == 0:
            return(None)
        else:
            return(luns)

    #get the luns of all hostgroups of one port
    def luns_all_ports_get(self):
        #"https://10.10.10.10/ConfigurationManager/v1/objects/storages/800000058068/luns?portId=CL5-B&hostGroupNumber=1&isBasicLunInformation=false&lunOption=ALUA"
        request_type='GET'

        #execute general procedures
        self._general_execute()

        #get all portIds
        return_response = self.ports_get()
        luns = {}
        
        i = 0
        for port in return_response:               
            #host group infos
            print(port)
            return_response_luns = self.luns_one_port_get(portId=port)
            if not return_response_luns == None:
                for lun in return_response_luns:
                    luns[lun] = return_response_luns[lun]

        return(luns)      

    #get the wwns of one hostgroups of one port
    def wwns_get(self, portId_hostGroupId):
        #/ConfigurationManager/v1/objects/host-wwns?portId=CL1-A&hostGroupNumber=0"
        request_type='GET'

        #execute general procedures
        self._general_execute()

        #'CL3-B,5' -> 'CL3-B' and '5'
        port, hostgroup = portId_hostGroupId.split(',')

        return_response = self._general_get(request_type=request_type, url_suffix=self.__url_base+self.__url_storages+'/host-wwns?portId='+str(port)+'&hostGroupNumber='+str(hostgroup))
        
        #Internal Error (no hostgroup on port)
        if return_response[0] == -1:
            return(None)

        #No WWN found in hostgroup
        if return_response == None:
            print('Warning: No WWN found in Hostgroup '+str(portId_hostGroupId))
            return(None)
        else:
            wwns = {}
            #print('Number of storage hostgroups of port ('+ str(portId) +'):', len(return_response))
            i = 0
            for wwn in return_response:
                i += 1
                #print(str(hostGroup['hostGroupId']), ' hostgroup ' + str(i) + 'of' + str(len(return_response)))
                #luns[str(lun['lunId'])] = lun

            return(wwns)


        return()

    #get resource group
    def resource_group_get(self):
        #"GET base-URL/v1/objects/storages/storage-device-ID/resource-groups"
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
   
        request_type='GET'

        #execute general procedures
        self._general_execute()

        return(self._general_get(request_type=request_type, url_suffix=self.__url_base+self.__url_storages + str(self._storage_device_id) + '/resource-groups'))

    #get all replication configuration
    def replication_get(self, replicationType=None):
        request_type='GET'
        #"https://10.10.10.10/ConfigurationManager/v1/objects/remote-replication"
                
        #execute general procedures
        self._general_execute()

        if replicationType == None:
            return(self._general_get(request_type=request_type, url_suffix='/ConfigurationManager/v1/objects/remote-replication'))
        else:
            if str(replicationType) in ['GAD', 'UR', 'TC']:
                return(self._general_get(request_type=request_type, url_suffix='/ConfigurationManager/v1/objects/remote-replications?replicationType='+str(replicationType)))

    #get all ldevs
    def ldevs_get(self, ldevNumberDec=None, count=100):
        #max ldevs 16384
        request_type='GET'

        #execute general procedures
        self._general_execute()
        
        if ldevNumberDec == None:
            return(self._general_get(request_type=request_type, url_suffix=self.__url_base+self.__url_storages+str(self._storage_device_id)+'/ldevs?count='+str(count)))
        else:
            if str(ldevNumberDec).isnumeric():
                return(self._general_get(request_type=request_type, url_suffix=self.__url_base+self.__url_storages+str(self._storage_device_id)+'/ldevs/'+str(ldevNumberDec)))
            else:
                return('ERROR: response: ldevNumber[dec] "'+str(ldevNumberDec)+'" is not a decimal ldev number')

    #get snapshots
    def snapshots_get(self, ldevNumber=None):
        request_type='GET'

        #execute general procedures
        self._general_execute()

        if ldevNumber == None:
            return(self._general_get(request_type=request_type, url_suffix=self.__url_base+self.__url_storages+str(self._storage_device_id)+'/snapshot-groups'))
        else:
            if str(ldevNumber).isnumeric():
                return(self._general_get(request_type=request_type, url_suffix=self.__url_base+self.__url_storages+str(self._storage_device_id)+'/snapshots?pvolLdevId='+str(ldevNumber)))
            else:
                return('ERROR: response: ldevNumber "'+str(ldevNumber)+'" is not a number.')
    
    #create snapshots
    def snapshots_create(self, pvolLdevId=None, snapshotGroupName=None, snapshotPoolId=None, isClone=False, isConsistencyGroup=True,
                        autoSplit=True):
        
        #execute general procedures
        self._general_execute()

        #create session token
        self._session_create()
        
        request_type='POST'
        body = json.dumps({"snapshotGroupName": str(snapshotGroupName),
                   "snapshotPoolId": str(snapshotPoolId),
                   "pvolLdevId": str(pvolLdevId),
                   "isClone": isClone,
                   "isConsistencyGroup": isConsistencyGroup,
                   "autoSplit": autoSplit,
                   "isDataReductionForceCopy": True
                  })
        
        if pvolLdevId == None:
            return('ERROR: response: You must specify a pvolLdevId.')
        else:
            if str(pvolLdevId).isnumeric():
                return_response=self._webrequest(request_type=request_type, url_suffix=self.__url_base+self.__url_storages+str(self._storage_device_id)+'/snapshots', body=body)
            else:
                return('ERROR: response: pvolLdevId "'+str(pvolLdevId)+'" is not a valid number.')
            
        if len(return_response) == 3:
            if return_response[0] == 0:
                #success
                
                #remove session token
                self._session_delete()
                
                return(return_response[2])
            else:
                return('WARNING: response status:'+str(return_response[1])+', response reason:'+str(return_response[2]))
        else:
            return('ERROR: response:'+str(return_response))
    
    #resync snapshots
    def snapshots_resync(self, snapshotGroupName=None, autoSplit=True):
        #execute general procedures
        self._general_execute()

        #create session token
        self._session_create()
        
        request_type='PUT'
        body = json.dumps({"parameters": {"autoSplit": autoSplit}})
        
        if snapshotGroupName == None:
            return('ERROR: response: You must specify a snapshotGroupName.')
        else:
            return_response=self._webrequest(request_type=request_type, url_suffix=self.__url_base+self.__url_storages+self._storage_device_id+'/snapshot-groups/'+str(snapshotGroupName)+'/actions/resync/invoke', body=body)
            
        if len(return_response) == 3:
            if return_response[0] == 0:
                #success
                
                #remove session token
                self._session_delete()
                
                return(return_response[2])
            else:
                return('WARNING: response status:'+str(return_response[1])+', response reason:'+str(return_response[2]))
        else:
            return('ERROR: response:'+str(return_response))
    
    #delete snapshots
    def snapshots_delete(self, snapshotGroupName=None):
        #execute general procedures
        self._general_execute()

        #create session token
        self._session_create()
        
        request_type='DELETE'
        if snapshotGroupName == None:
            return('ERROR: response: You must specify a snapshotGroupName.')
        else:
            return_response=self._webrequest(request_type=request_type, url_suffix=self.__url_base+self.__url_storages+rest._storage_device_id+'/snapshot-groups/'+str(snapshotGroupName))
            
        if len(return_response) == 3:
            if return_response[0] == 0:
                #success
                
                #remove session token
                self._session_delete()
                
                return(return_response[2])
            else:
                return('WARNING: response status:'+str(return_response[1])+', response reason:'+str(return_response[2]))
        else:
            return('ERROR: response:'+str(return_response))