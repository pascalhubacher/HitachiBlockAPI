#must me in .gitignore
import keyring

#remove
#set the ip for 58068
keyring.delete_password('HitachiBlockRestAPI', 'StorageIp')
keyring.delete_password('HitachiBlockRestAPI', 'StorageSerial')

#set the ip and the port for Ops Center
keyring.delete_password('HitachiBlockRestAPI', 'OpsCenterIp')
keyring.delete_password('HitachiBlockRestAPI', 'OpsCenterPort')

#set the password for user hup
keyring.delete_password('HitachiBlockRestAPI', 'hup')