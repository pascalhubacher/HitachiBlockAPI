#must me in .gitignore
import keyring

#remove
#set the ip for 58068
keyring.delete_password('StorageRestAPI', 'StorageIp')
keyring.set_password('StorageRestAPI', 'StorageSerial')

#set the ip and the port for Ops Center
keyring.delete_password('StorageRestAPI', 'OpsCenterIp')
keyring.delete_password('StorageRestAPI', 'OpsCenterPort')

#set the password for user hup
keyring.delete_password('StorageRestAPI', 'hup')