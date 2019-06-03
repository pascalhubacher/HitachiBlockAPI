# StorageRestAPI<br />
Storage Rest API Class<br />

Please download the latest Hitachi Rest API documentation from:<br />
https://knowledge.hitachivantara.com/Documents/Management_Software/Configuration_Manager_REST_API<br />

<h2>Load RestAPI class</h2>
#If you have a Hitachi.py file in the same directory that contains the RestAPI class<br />
from Hitachi import RestAPI<br />
ip = '10.10.10.10'<br />
rest = RestAPI(storage_fqdn_ip=ip, username='[user]', password='[password]')<br />

<h2>get storage id</h2>
#if there are more than one storage systems<br />
response = rest.storage_device_id_get()<br />
if len(response) == 1:<br />
    response = rest.storage_device_id_set(element_number=0)<br />
    print('storage device id:', response)<br />
else:<br />
    print('more than one storage found:')<br />
    print(response)<br />
    
<h2>get ldev information</h2>
3845[dec] means 0F:05[hex]<br />
response =rest.ldevs_get(ldevNumber=3845)<br />
print(response)<br />

<h2>get all snapshot groups</h2>
response =rest.snapshots_get()<br />
print(response)<br />

<h2>get specific snapshot</h2>
response =rest.snapshots_get(ldevNumber=3845)<br />
print(response)<br />

<h2>create snapshot</h2>
response =rest.snapshots_create(snapshotGroupName='test',snapshotPoolId=4, pvolLdevId=3845)<br />
print(response)<br />

<h2>resync snapshot group</h2>
response =rest.snapshots_resync(snapshotGroupName='test')<br />
print(response)<br />

<h2>delete snapshot group</h2>
response =rest.snapshots_delete(snapshotGroupName='test')<br />
print(response)<br />

<h2>get last job</h2>
response =rest.jobs_get_last()<br />
print(response)<br />

<h2>get specific jobid</h2>
response =rest.jobs_get_by_jobid(jobId=10)<br />
print(response)<br />
