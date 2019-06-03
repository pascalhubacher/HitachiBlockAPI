
# coding: utf-8

# In[40]:


"""
This library provides an easy way to script tasks for the Hitachi Storage Arrays.

Please be aware that when passing arguments to methods that take \*\*kwargs, the exact
parameters that can be passed can be found in the REST API guide.
"""

import http.client
import json
import ssl
from base64 import b64encode

# The current version of this library.
VERSION = "0.0.1"

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
    
    #, protocol=self.protocol, ip=self._ip_fqdn
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
        
        
    
    #, protocol=self.protocol, ip=self._ip_fqdn
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

    #, protocol='https://', ip='127.0.0.1', user='maintenance', password='raid-maintenance'
    def _session_get(self):
        request_type='GET'
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
    
    def _session_create(self):
        '''
        '''
        request_type='POST'
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
        
    def _session_delete(self):
        '''
        '''
        request_type='DELETE'
        return_response=self._webrequest(request_type=request_type, url_suffix='/ConfigurationManager/v1/objects/storages/'+str(self._storage_device_id)+'/sessions/'+str(self._session_id))
        '''
        '''
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
        
    def jobs_get(self):
        '''
        '''
        #create session token
        self._session_create()
        
        request_type='GET'
        return_response=self._webrequest(request_type=request_type, url_suffix='/ConfigurationManager/v1/objects/storages/'+str(self._storage_device_id)+'/jobs')
        '''
        '''
        if len(return_response) == 3:
            if return_response[0] == 0:
                #success
                
                #remove session token
                self._session_delete()
                
                #print(return_response)
                return(return_response[2]['data'])
            else:
                return('WARNING: response status:'+str(return_response[1])+', response reason:'+str(return_response[2]))
        else:
            return('ERROR: response:'+str(return_response))
    
    def jobs_get_last(self):
        '''
        '''
        return(self.jobs_get()[0])
    
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
    
    def ldevs_get(self, ldevNumber=None, count=100):
        #max ldevs 16384
        
        #create session token
        self._session_create()
        
        request_type='GET'
        if ldevNumber == None:
            return_response=self._webrequest(request_type=request_type, url_suffix='/ConfigurationManager/v1/objects/storages/'+str(self._storage_device_id)+'/ldevs?count='+str(count))
        else:
            if str(ldevNumber).isnumeric():
                return_response=self._webrequest(request_type=request_type, url_suffix='/ConfigurationManager/v1/objects/storages/'+str(self._storage_device_id)+'/ldevs/'+str(ldevNumber))
            else:
                return('ERROR: response: ldevNumber "'+str(ldevNumber)+'" is not a number.')
        '''
        '''
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
    
    def snapshots_get(self, ldevNumber=None):
        
        #create session token
        self._session_create()
        
        request_type='GET'
        if ldevNumber == None:
            return_response=self._webrequest(request_type=request_type, url_suffix='/ConfigurationManager/v1/objects/storages/'+str(self._storage_device_id)+'/snapshot-groups')
        else:
            if str(ldevNumber).isnumeric():
                return_response=self._webrequest(request_type=request_type, url_suffix='/ConfigurationManager/v1/objects/storages/'+str(self._storage_device_id)+'/snapshots?pvolLdevId='+str(ldevNumber))
            else:
                return('ERROR: response: ldevNumber "'+str(ldevNumber)+'" is not a number.')
            
        if len(return_response) == 3:
            if return_response[0] == 0:
                #success
                
                #remove session token
                self._session_delete()
                
                return(return_response[2]['data'])
            else:
                return('WARNING: response status:'+str(return_response[1])+', response reason:'+str(return_response[2]))
        else:
            return('ERROR: response:'+str(return_response))
    
    def snapshots_create(self, pvolLdevId=None, snapshotGroupName=None, snapshotPoolId=None, isClone=False, isConsistencyGroup=True,
                        autoSplit=True):
        
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
    
    def snapshots_resync(self, snapshotGroupName=None, autoSplit=True):
        
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
        
    def snapshots_delete(self, snapshotGroupName=None):
        
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