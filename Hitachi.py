"""
This library provides an easy way to script tasks for the Hitachi Storage Arrays.

Please be aware that when passing arguments to methods that take \*\*kwargs, the exact
parameters that can be passed can be found in the REST API guide.
"""

import http.client
import json
import ssl
from base64 import b64encode

DESCRIPTION = 'detail'

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
        #self.__maxConnectionsParallelTotal = 8
        #self.__maxConnectionsParallelGet = 6
    
    #extecutes the web request
    def _webrequest(self, request_type='GET', url_suffix='/ConfigurationManager/v1/objects/storages/', body=''):
        '''Return the json response of the webrequest'''
        
        url = self._protocol+self._ip_fqdn+url_suffix
        
        if self._token is None:
            headers = {'Accept':'application/json', 'Content-Type':'application/json', 'Authorization' : 'Basic %s' %  self.__userAndPass}
        else:
            headers = {'Accept':'application/json', 'Content-Type':'application/json', 'Authorization' : 'Session '+str(self._token)}

        #create https connection, unverified connection
        connection = http.client.HTTPSConnection(self._ip_fqdn, context=ssl._create_unverified_context())

        # Send login request
        connection.request(method=request_type, url=url, headers=headers, body=body)
        
        #print()
        # Get the response
        response = connection.getresponse()
        # Display the response status
        #print()
        #print ("Status = ", response.status)
        # 200 Successful
        # 202 Accepted The request has been accepted for processing, but the processing has not been completed.
        if response.status == 200 or response.status == 202:
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
                    if 'data' in return_response[2]:
                        if not len(return_response[2]['data']) == 0:
                            return(return_response[2]['data'])
                        else:
                            return(None)
                    else:
                        #no list
                        return(return_response[2])
                else:
                    return(None)
                    
            else:
                return('WARNING: response status:'+str(return_response[1])+', response reason:'+str(return_response[2]))
        else:
            return('ERROR: response:'+str(return_response))

    def _general_execute(self):
        #set StorageDeviceId if not already set
        if self._storage_device_id == None:
            self.storage_device_id_set()

    #gets the storge device id
    def storage_device_id_get(self):
        '''This function is '''
        request_type = 'GET'
        
        return_response=self._webrequest(request_type=request_type, 
                                     url_suffix='/ConfigurationManager/v1/objects/storages')
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
                return(return_response[2]['data'])
            else:
                return('WARNING: response status:'+str(return_response[1])+', response reason:'+str(return_response[2]))
        else:
            return('ERROR: response:'+str(return_response))

    #set storage device id        
    def storage_device_id_set(self, element_number=0):
        request_type = 'GET'

        return_response=self._webrequest(request_type=request_type, 
                                     url_suffix='/ConfigurationManager/v1/objects/storages')
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
                self._storage_device_id = return_response[2]['data'][int(element_number)]['storageDeviceId']
                return(return_response[2]['data'][int(element_number)]['storageDeviceId'])
            else:
                return('WARNING: response status:'+str(return_response[1])+', response reason:'+str(return_response[2]))
        else:
            return('ERROR: response:'+str(return_response))
    
    #get session id
    def _session_get(self):
        request_type='GET'

        #execute general procedures
        self._general_execute()

        return_response=self._webrequest(request_type=request_type, 
                                url_suffix='/ConfigurationManager/v1/objects/storages/'+self._storage_device_id+'/sessions')
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
                return(return_response[2]['data'])
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

        return_response=self._webrequest(request_type=request_type, 
                                url_suffix='/ConfigurationManager/v1/objects/storages/'+self._storage_device_id+'/sessions')
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
                self._token = return_response[2]['token']
                self._session_id = return_response[2]['sessionId']
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
        
        return_response=self._webrequest(request_type=request_type, url_suffix='/ConfigurationManager/v1/objects/storages/'+str(self._storage_device_id)+'/sessions/'+str(self._session_id))
        
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
    def jobs_get(self):
        '''
        '''
        request_type='GET'

        #execute general procedures
        self._general_execute()

        #create session token
        self._session_create()
        
        return(self._general_get(request_type=request_type, url_suffix='/ConfigurationManager/v1/objects/storages/'+str(self._storage_device_id)+'/jobs'))
        
    #get last job
    def jobs_get_last(self):
        '''
        '''

        return(self.jobs_get()[0])
    
    #get job by id
    def jobs_get_by_jobid(self, jobId=None):
        '''
        '''

        response = self.jobs_get()
        if not jobId == None:
            for job in response:
                if str(job['jobId']) == str(jobId):
                    return(job)
                
            return('ERROR: response: jobId: "'+str(jobId)+'" is not found. Please specify an existing jobId.')
        else:
            return('ERROR: response: jobId is "None". Please specify a valid jobId.')
    
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

        return(self._general_get(request_type=request_type, url_suffix='/ConfigurationManager/v1/objects/storages/' + str(self._storage_device_id) + '/resource-groups'))

    #get specific host group of one port
    def host_group_one_port_get(self, portId, hostGroup):
        return()

    #get host groups of one port
    def host_groups_one_port_get(self, portId):
        # https://10.70.4.145/ConfigurationManager/v1/objects/storages/800000058068/host-groups?portId=CL1-A&isUndefined=true&detailInfoType=resourceGroup
        request_type='GET'

        #execute general procedures
        self._general_execute()

        return_response = self._general_get(request_type=request_type, url_suffix='/ConfigurationManager/v1/objects/storages/'+str(self._storage_device_id)+'/host-groups?portId='+portId+'&isUndefined=false&detailInfoType=resourceGroup')
        hostGroups = {}
        print('Number of storage hostgroups of port ('+ str(portId) +'):', len(return_response))
        i = 0
        for hostGroup in return_response:
            i += 1
            print(str(hostGroup['hostGroupId']), ' hostgroup ' + str(i) + 'of' + str(len(return_response)))
            hostGroups[str(hostGroup['hostGroupId'])] = {}
            hostGroups[str(hostGroup['hostGroupId'])][DESCRIPTION] = hostGroup

        return(hostGroups)

    #get host group of all ports
    def host_groups_all_ports_get(self):
        # https://10.70.4.145/ConfigurationManager/v1/objects/storages/800000058068/host-groups?portId=CL1-A&isUndefined=true&detailInfoType=resourceGroup
        request_type='GET'

        #execute general procedures
        self._general_execute()

        #get all portIds
        return_response = self.ports_get()
        ports = {}
        print('Number of storage ports:', len(return_response))
        i = 0
        for port in return_response:
            i += 1
            print(str(port['portId']), 'port ' + str(i) + 'of' + str(len(return_response)))
            ports[str(port['portId'])] = {}
            ports[str(port['portId'])][DESCRIPTION] = port
            ports[str(port['portId'])] = self.host_groups_one_port_get(port['portId'])

        return(ports)

    #get luns of one hostgroup
    def luns_get(self, portId, hostGroupId):
        #"https://10.10.10.10/ConfigurationManager/v1/objects/storages/800000058068/luns?portId=CL5-B&hostGroupNumber=1&isBasicLunInformation=false&lunOption=ALUA"
        request_type='GET'

        #execute general procedures
        self._general_execute()

        return(self._general_get(request_type=request_type, url_suffix='/ConfigurationManager/v1/objects/storages/'+str(self._storage_device_id)+'/luns?portId='+portId+'&hostGroupNumber='+str(hostGroupId)+'&isBasicLunInformation=false&lunOption=ALUA'))
        
    #not done yet
    #get the luns of all hostgroups of one port
    def luns_one_port_get(self, portId):
        #"https://10.10.10.10/ConfigurationManager/v1/objects/storages/800000058068/luns?portId=CL5-B&hostGroupNumber=1&isBasicLunInformation=false&lunOption=ALUA"
        request_type='GET'

        #execute general procedures
        self._general_execute()

        '''
        {'hostGroupId': 'CL3-B,0',
        'portId': 'CL3-B',
        'hostGroupNumber': 0,
        'hostGroupName': '3B-G00',
        'hostMode': 'LINUX/IRIX',
        'resourceGroupId': 0,
        'isDefined': True}
        '''
        #get all hostgroups of a port
        return_response_hostgroups = self.host_groups_get(portId)
        luns = {}
        luns[str(portId)] = {}
        print('Number of storage hostgroups of port ('+ str(portId) +'):', len(return_response_hostgroups))
        i = 0
        for hostgroup in return_response_hostgroups:
            i += 1
            print(str(hostgroup['hostGroupId']), ' hostgroup ' + str(i) + 'of' + str(len(return_response_hostgroups)))
            #create hostgroup element
            luns[str(portId)][str(hostgroup['hostGroupId'])] = {}


            host_groups[str(port['portId'])] = self._general_get(request_type=request_type, url_suffix='/ConfigurationManager/v1/objects/storages/'+str(self._storage_device_id)+'/host-groups?portId='+str(port['portId'])+'&isUndefined=false&detailInfoType=resourceGroup')
        print('done')
        return(luns)


        #return(self._general_get(request_type=request_type, url_suffix='/ConfigurationManager/v1/objects/storages/'+str(self._storage_device_id)+'/luns?portId='+portId+'&hostGroupNumber='+str(hostGroupId)+'&isBasicLunInformation=false&lunOption=ALUA'))

    #not done yet
    #get the luns of all hostgroups of one port
    def luns_all_ports_get(self):
        #"https://10.10.10.10/ConfigurationManager/v1/objects/storages/800000058068/luns?portId=CL5-B&hostGroupNumber=1&isBasicLunInformation=false&lunOption=ALUA"
        request_type='GET'

        #execute general procedures
        self._general_execute()

        return(self._general_get(request_type=request_type, url_suffix='/ConfigurationManager/v1/objects/storages/'+str(self._storage_device_id)+'/luns?portId='+portId+'&hostGroupNumber='+str(hostGroupId)+'&isBasicLunInformation=false&lunOption=ALUA'))
    

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

    #get ports
    def ports_get(self, portId=None, logins=None):
        #https://10.70.4.145/ConfigurationManager/v1/objects/storages/800000058068/ports?portId=CL1-A&?detailInfoType=logins
        request_type='GET'

        #execute general procedures
        self._general_execute()

        if not (portId == None):
            return(self._general_get(request_type=request_type, url_suffix='/ConfigurationManager/v1/objects/storages/'+str(self._storage_device_id)+'/ports?portId='+portId+'&detailInfoType=logins'))
        else:
            if logins == None:
                return(self._general_get(request_type=request_type, url_suffix='/ConfigurationManager/v1/objects/storages/'+str(self._storage_device_id)+'/ports'))
            else:
                return(self._general_get(request_type=request_type, url_suffix='/ConfigurationManager/v1/objects/storages/'+str(self._storage_device_id)+'/ports?detailInfoType=logins'))

    #get ldevs
    def ldevs_get(self, ldevNumberDec=None, count=100):
        #max ldevs 16384
        request_type='GET'

        #execute general procedures
        self._general_execute()
        
        if ldevNumberDec == None:
            return(self._general_get(request_type=request_type, url_suffix='/ConfigurationManager/v1/objects/storages/'+str(self._storage_device_id)+'/ldevs?count='+str(count)))
        else:
            if str(ldevNumberDec).isnumeric():
                return(self._general_get(request_type=request_type, url_suffix='/ConfigurationManager/v1/objects/storages/'+str(self._storage_device_id)+'/ldevs/'+str(ldevNumberDec)))
            else:
                return('ERROR: response: ldevNumber "'+str(ldevNumber)+'" is not a decimal ldev number')

    #get snapshots
    def snapshots_get(self, ldevNumber=None):
        request_type='GET'

        #execute general procedures
        self._general_execute()

        if ldevNumber == None:
            return(self._general_get(request_type=request_type, url_suffix='/ConfigurationManager/v1/objects/storages/'+str(self._storage_device_id)+'/snapshot-groups'))
        else:
            if str(ldevNumber).isnumeric():
                return(self._general_get(request_type=request_type, url_suffix='/ConfigurationManager/v1/objects/storages/'+str(self._storage_device_id)+'/snapshots?pvolLdevId='+str(ldevNumber)))
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
                return_response=self._webrequest(request_type=request_type, url_suffix='/ConfigurationManager/v1/objects/storages/'+str(self._storage_device_id)+'/snapshots', body=body)
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
            return_response=self._webrequest(request_type=request_type, url_suffix='/ConfigurationManager/v1/objects/storages/'+rest._storage_device_id+'/snapshot-groups/'+str(snapshotGroupName)+'/actions/resync/invoke', body=body)
            
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
            return_response=self._webrequest(request_type=request_type, url_suffix='/ConfigurationManager/v1/objects/storages/'+rest._storage_device_id+'/snapshot-groups/'+str(snapshotGroupName))
            
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