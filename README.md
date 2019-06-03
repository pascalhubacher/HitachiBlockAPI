# StorageRestAPI<br />
Storage Rest API Class<br />

Please download the latest Hitachi Rest API documentation from:<br />
https://knowledge.hitachivantara.com/Documents/Management_Software/Configuration_Manager_REST_API<br />

#If you have a Hitachi.py file in the same directory that contains the RestAPI class<br />
from Hitachi import RestAPI<br />
ip = '10.10.10.10'<br />
rest = RestAPI(storage_fqdn_ip=ip, username='[user]', password='[password]')<br />
