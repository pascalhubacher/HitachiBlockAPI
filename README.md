# HitachiBlockAPI
## Hitachi Block API Class
 
With this class it is a lot easier to work with the Configuration Manager Rest API as it automatically gets the storage id and it creates/deletes sessions for all tasks.
Also the responses are formatted as a python dict to easily select or search for specific information.

## Coding
### Install HitachiBlockAPI package
```
pip install HitachiBlockAPI
```
### Load RestAPI class
```
from HitachiBlockAPI import RestAPI
from HitachiBlockAPI import logger
#import the logging module to specify the logging level
import logging
#set logging level
logger.setLevel(logging.INFO)
#logger.setLevel(logging.DEBUG)
```
If you use the Configuration RestAPI / Ops Center API then use port 23451
```
storage = RestAPI(fqdn_ip='10.10.10.10', port=23451, username='[user]', password='[password]')
```
If you have more than one storage registerd then you have to specify with which one you want to work with
In the following example the first element is chosen.
If you want to change it then you have to reexecute the command with another element_number
```
storage.storage_device_id_set(serial_number=[serial number of the storage])
```
If you directly contact the storage SVP or the GUM then use port 443. But this is the default so you do not have to specify it.
```
storage = RestAPI(fqdn_ip='10.10.10.10', username='[user]', password='[password]')
```
If you only have one storage registerd then you do not have to set it (done automatically in the background).

## Available functions
### General
Get the ucode, IP and other details of the storage
```
storage_systems_get(fqdn_ip:str=None, port:str=None, username:str=None, password:str=None)
storage_device_id_get(fqdn_ip:str=None, port:str=None, username:str=None, password:str=None, serial_number:int=None)
storage_device_id_set(fqdn_ip:str=None, port:str=None, username:str=None, password:str=None, serial_number:int=None)
storage_details_get(fqdn_ip:str=None, port:str=None, username:str=None, password:str=None, storageDeviceId:str=None)
storage_summaries_get(fqdn_ip:str=None, port:str=None, username:str=None, password:str=None)
```
### Session handling
```
_session_create()
_session_delete()
_session_get()
```
### Jobs
```
_jobs_by_id_get(self, jobId=None)
_jobs_last_get(self)
```
### Resource Group
```
resource_lock(self, waitTime=None)
resource_unlock(self)
```
### Pools
```
pools_get(self, poolId=None)
```
### LDEVs
```
ldevs_get(self, ldevNumber=None, count=16384)
```
### Ports
`ports_get(self, portId=None, logins=None)`
### Host Groups
`host_groups_one_port_get(self, portId)`

`host_groups_all_ports_get(self)`
### LUNs
`luns_get(self, portId_hostGroupId)`

`luns_one_port_get(self, portId)`

`luns_all_ports_get(self)`
### WWNs
`wwns_get(self, portId_hostGroupId)`

`wwns_one_port_get(self, portId)`

`wwns_all_ports_get(self)`
### Replication
`replication_get(self, replicationType=None)`
### Snapshots / Cloning
`snapshotgroups_get(self, snapshotGroupName=None)`

`snapshots_get(self, ldevNumber=None)`

`snapshots_create(self, pvolLdevId=None, snapshotGroupName=None, snapshotPoolId=None, isClone=False, isConsistencyGroup=True, autoSplit=True)`

`snapshots_resync(self, snapshotGroupName=None, autoSplit=True)`

`snapshots_delete(self, snapshotGroupName=None)`

## Manual
Please download the latest Hitachi Block Rest API documentation from:<br />
https://knowledge.hitachivantara.com/Documents/Management_Software/Ops_Center/API_Configuration_Manager<br />