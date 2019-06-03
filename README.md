# StorageRestAPI
Storage Rest API Class

Please download the latest Hitachi Rest API documentation from:
https://knowledge.hitachivantara.com/Documents/Management_Software/Configuration_Manager_REST_API

#If you have a Hitachi.py file in the same directory that contains the RestAPI class
from Hitachi import RestAPI
ip = '10.10.10.10'
rest = RestAPI(storage_fqdn_ip=ip, username='[user]', password='[password]')
