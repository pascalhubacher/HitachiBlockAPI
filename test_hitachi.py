import pytest
import keyring

'''@fixture
def hitachi():
    from StorageRestAPI.Hitachi import RestAPI
    return RestAPI()

def test_add(hitachi):
    assert hitachi.add(1,2) == 3
'''

import json
from StorageRestAPI.Hitachi import RestAPI
#import the logger of the Hitachi.py Module
from StorageRestAPI.Hitachi import logger
#import the logging module to specify the logging level
import logging

#set logging level
logger.setLevel(logging.DEBUG)

#check if string is of json format
def is_json(myjson:str):
    try:
        json_object = json.loads(myjson)
    except ValueError as e:
        return False
    return True

#PF REST API
#storage = RestAPI(fqdn_ip=keyring.get_password('StorageRestAPI', 'StorageIp'), username='hup', password=keyring.get_password('StorageRestAPI', 'hup'))
# Ops Center CM REST API
storage = RestAPI(fqdn_ip=keyring.get_password('StorageRestAPI', 'OpsCenterIp'), port=keyring.get_password('StorageRestAPI', 'OpsCenterPort'), username='hup', password=keyring.get_password('StorageRestAPI', 'hup'))

@pytest.mark.storage_systems_get
def test_storage_systems_get():
    result = storage.storage_systems_get()
    #must be of type list
    assert type(result) == list

@pytest.mark.storage_device_id_get
def test_storage_device_id_get():
    result = storage._storage_device_id_get()
    #must be of type list
    assert type(result) == str
    assert len(result) == 12

@pytest.mark.storage_details_get
def test_storage_details_get():
    result = storage.storage_details_get()
    #must be json compatible
    assert type(result) == str
    assert is_json(result) == True
    if is_json(result):
        #must be of type dict
        assert type(json.loads(result)) == dict

@pytest.mark.storage_summaries_get
def test_storage_summaries_get():
    result = storage.storage_summaries_get()
    #must be json compatible
    assert type(result) == str
    assert is_json(result) == True
    if is_json(result):
        #must be of type dict
        assert type(json.loads(result)) == dict

@pytest.mark.jobs_all
def test_jobs_all():
    result = storage._jobs_get()
    #must be of type list or None (empty job list)
    if not result == None:
        assert type(result) == list

        def test_jobs_last_get():
            result = storage._jobs_last_get()
            #must be of type dict
            assert type(result) == dict
            #set variable for the next test
            global jobId
            jobId = str(result['jobId'])
        
        def test_jobs_by_id_get():
            result = storage._jobs_by_id_get(jobId=jobId)
            #must be of type dict
            assert type(result) == dict

