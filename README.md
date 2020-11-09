# StorageRestAPI<br />
Storage Rest API Class<br />

With this class it is a lot easier to work with the Configuration Rest API as it automatically gets the storage id and it creates/deletes sessions for all tasks.
Also the responses are formatted in JSON so can easily select or search for specific information.

## Available functions
### General
`_storage_device_id_get(self)`

`_jobs_by_id_get(self, jobId=None)`

`_jobs_last_get(self)`
### Resource Group
`resource_lock(self, waitTime=None)`

`resource_unlock(self)`
### Pools
`pools_get(self, poolId=None)`
### LDEVs
`ldevs_get(self, ldevNumber=None, count=16384)`
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
Please download the latest Hitachi Rest API documentation from:<br />
https://knowledge.hitachivantara.com/Documents/Management_Software/Configuration_Manager_REST_API<br />

## Coding
### Load RestAPI class
#If you have a Hitachi.py file in the same directory as you run your python program<br />
`from Hitachi import RestAPI`<br />
`#import the logger of the Hitachi.py Module`<br />
`from Hitachi import logger`<br />
`#import the logging module to specify the logging level`<br />
`import logging`<br />
`#set logging level`<br />
`logger.setLevel(logging.INFO)`<br />
`#logger.setLevel(logging.DEBUG)`<br />
`ip = '10.10.10.10'`<br />
`rest = RestAPI(storage_fqdn_ip=ip, username='[user]', password='[password]')`<br />
