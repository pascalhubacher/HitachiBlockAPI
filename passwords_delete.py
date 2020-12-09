#must me in .gitignore
import keyring

#remove
#set the ip for 58068
keyring.delete_password('HitachiBlockAPI', 'StorageIp')
keyring.delete_password('HitachiBlockAPI', 'StorageSerial')

#set the ip and the port for Ops Center
keyring.delete_password('HitachiBlockAPI', 'OpsCenterIp')
keyring.delete_password('HitachiBlockAPI', 'OpsCenterPort')

#set the password for user hup
keyring.delete_password('HitachiBlockAPI', 'hup')