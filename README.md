# StorageRestAPI<br />
Storage Rest API Class<br />

With this class it is a lot easier to work with the Configuration Rest API as it automatically gets the storage id and it creates/deletes sessions for all tasks.
Also the responses are formatted in JSON so can easily select or search for specific information.

## Available functions
### General
_storage_device_id_get -> get storage id
### Resource Group
resource_lock
resource_unlock

Please download the latest Hitachi Rest API documentation from:<br />
https://knowledge.hitachivantara.com/Documents/Management_Software/Configuration_Manager_REST_API<br />

<h2>Load RestAPI class</h2>
#If you have a Hitachi.py file in the same directory that contains the RestAPI class<br />
from Hitachi import RestAPI<br />
#import the logger of the Hitachi.py Module<br />
from Hitachi import logger<br />
#import the logging module to specify the logging level<br />
import logging<br />
#set logging level<br />
logger.setLevel(logging.INFO)<br />
#logger.setLevel(logging.DEBUG)<br />
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
<!-- 3845[dec] means 0F:05[hex]<br /> -->
response =rest.ldevs_get(ldevNumberDec=3845)<br />
print(response)<br />
