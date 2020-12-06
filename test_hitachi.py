import pytest
import keyring

'''@fixture
def hitachi():
    from StorageRestAPI.Hitachi import RestAPI
    return RestAPI()
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
#element_number = 0

# Ops Center CM REST API
storage = RestAPI(fqdn_ip=keyring.get_password('StorageRestAPI', 'OpsCenterIp'), port=keyring.get_password('StorageRestAPI', 'OpsCenterPort'), username='hup', password=keyring.get_password('StorageRestAPI', 'hup'))
element_number = 1
portId='CL1-B'
ldevNumber=0
portId_hostGroupId='CL1-B,5'
replicationType='GAD'

@pytest.mark.storage_systems_get
def test_storage_systems_get():
    result = storage.storage_systems_get()
    #must be of type list
    assert type(result) == list

@pytest.mark.storage_device_id_set
def test_storage_device_id_set():
    result = storage.storage_device_id_set(element_number=element_number)
    #must be of type list
    assert type(result) == str
    assert len(result) == 12

@pytest.mark.storage_device_id_get
def test_storage_device_id_get():
    result = storage.storage_device_id_get()
    #must be of type list
    assert type(result) == str
    assert len(result) == 12

@pytest.mark.storage_details_get
def test_storage_details_get():
    result = storage.storage_device_id_set(element_number=element_number)
    #must be of type str
    assert type(result) == str
    assert len(result) == 12
    result = storage.storage_details_get()
    #must be json compatible
    assert type(result) == dict

@pytest.mark.storage_summaries_get
def test_storage_summaries_get():
    result = storage.storage_device_id_set(element_number=element_number)
    #must be of type str
    assert type(result) == str
    assert len(result) == 12
    result = storage.storage_summaries_get(timeout=90)
    #must be json compatible
    assert type(result) == dict

@pytest.mark.jobs_all
def test_jobs_all():
    result = storage.storage_device_id_set(element_number=element_number)
    #must be of type str
    assert type(result) == str
    assert len(result) == 12
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

@pytest.mark.session_all
def test_session_all():
    def test_session_get():
        result = storage.storage_device_id_set(element_number=element_number)
        #must be of type str
        assert type(result) == str
        assert len(result) == 12
        result = storage._session_get()
        assert type(result) == str
        assert result == ''
    def test_session_create():
        result = storage._session_create()
        assert type(result) == None
    def test_session_get():
        result = storage._session_get()
        assert type(result) == list
    def test_session_delete():
        result = storage._session_delete()
        assert type(result) == str
        assert result == ''

@pytest.mark.resource_group
def test_resource_group_get():
    result = storage.storage_device_id_set(element_number=element_number)
    #must be of type str
    assert type(result) == str
    assert len(result) == 12
    result = storage.resource_group_get()
    #must be of type dict
    assert type(result) == dict

@pytest.mark.pools_get
def test_pools_get():
    result = storage.storage_device_id_set(element_number=element_number)
    #must be of type str
    assert type(result) == str
    assert len(result) == 12
    result = storage.pools_get()
    #must be of type dict
    assert type(result) == dict

@pytest.mark.pools_get_pool0
def test_pools_get():
    result = storage.storage_device_id_set(element_number=element_number)
    #must be of type list
    assert type(result) == str
    assert len(result) == 12
    result = storage.pools_get(poolId=0)
    #must be of type dict
    assert type(result) == dict

@pytest.mark.ports_get
def test_ports_get():
    result = storage.storage_device_id_set(element_number=element_number)
    #must be of type list
    assert type(result) == str
    assert len(result) == 12
    result = storage.ports_get(timeout=90)
    #must be of type dict
    assert type(result) == dict

@pytest.mark.ports_get_1port
def test_ports_get_1port():
    result = storage.storage_device_id_set(element_number=element_number)
    #must be of type list
    assert type(result) == str
    assert len(result) == 12
    result = storage.ports_get(portId=portId)
    #must be of type dict
    assert type(result) == dict

@pytest.mark.ldevs_get_1ldev
def test_ldevs_get_1ldev():
    result = storage.storage_device_id_set(element_number=element_number)
    #must be of type list
    assert type(result) == str
    assert len(result) == 12
    result = storage.ldevs_get(ldevNumber=ldevNumber)
    #must be of type dict
    assert type(result) == dict

@pytest.mark.ldevs_get
def test_ldevs_get():
    result = storage.storage_device_id_set(element_number=element_number)
    #must be of type list
    assert type(result) == str
    assert len(result) == 12
    result = storage.ldevs_get()
    #must be of type dict
    assert type(result) == dict

@pytest.mark.host_groups_one_port_get
def test_host_groups_one_port_get():
    result = storage.storage_device_id_set(element_number=element_number)
    #must be of type list
    assert type(result) == str
    assert len(result) == 12
    result = storage.host_groups_one_port_get(portId=portId)
    #must be of type dict
    assert type(result) == dict

@pytest.mark.host_groups_all_ports_get
def test_host_groups_all_ports_get():
    result = storage.storage_device_id_set(element_number=element_number)
    #must be of type list
    assert type(result) == str
    assert len(result) == 12
    result = storage.host_groups_all_ports_get()
    #must be of type dict
    assert type(result) == dict

@pytest.mark.luns_get_portId_hostGroupId
def test_luns_get_portId_hostGroupId():
    result = storage.storage_device_id_set(element_number=element_number)
    #must be of type list
    assert type(result) == str
    assert len(result) == 12
    result = storage.luns_get(portId_hostGroupId=portId_hostGroupId)
    #must be of type dict
    assert type(result) == dict

@pytest.mark.luns_one_port_get
def test_luns_one_port_get():
    result = storage.storage_device_id_set(element_number=element_number)
    #must be of type list
    assert type(result) == str
    assert len(result) == 12
    result = storage.luns_one_port_get(portId=portId)
    #must be of type dict
    assert type(result) == dict

@pytest.mark.luns_all_ports_get
def test_luns_all_ports_get():
    result = storage.storage_device_id_set(element_number=element_number)
    #must be of type list
    assert type(result) == str
    assert len(result) == 12
    result = storage.luns_all_ports_get()
    #must be of type dict
    assert type(result) == dict

@pytest.mark.wwns_get_portId_hostGroupId
def test_wwns_get_portId_hostGroupId():
    result = storage.storage_device_id_set(element_number=element_number)
    #must be of type list
    assert type(result) == str
    assert len(result) == 12
    result = storage.wwns_get(portId_hostGroupId=portId_hostGroupId)
    #must be of type dict
    assert type(result) == dict

@pytest.mark.wwns_one_port_get
def test_wwns_one_port_get():
    result = storage.storage_device_id_set(element_number=element_number)
    #must be of type list
    assert type(result) == str
    assert len(result) == 12
    result = storage.wwns_one_port_get(portId=portId)
    #must be of type dict
    assert type(result) == dict

@pytest.mark.wwns_all_ports_get
def test_wwns_all_ports_get():
    result = storage.storage_device_id_set(element_number=element_number)
    #must be of type list
    assert type(result) == str
    assert len(result) == 12
    result = storage.wwns_all_ports_get()
    #must be of type dict
    assert type(result) == dict

@pytest.mark.replication_get_gad
def test_replication_get_gad():
    result = storage.storage_device_id_set(element_number=element_number)
    #must be of type list
    assert type(result) == str
    assert len(result) == 12
    result = storage.replication_get(replicationType=replicationType)
    #must be of type dict
    assert type(result) == dict

@pytest.mark.replication_get
def test_replication_get():
    result = storage.storage_device_id_set(element_number=element_number)
    #must be of type list
    assert type(result) == str
    assert len(result) == 12
    result = storage.replication_get()
    #must be of type dict
    assert type(result) == dict

@pytest.mark.snapshots_get
def test_snapshots_get():
    result = storage.storage_device_id_set(element_number=element_number)
    #must be of type list
    assert type(result) == str
    assert len(result) == 12
    result = storage.snapshots_get()
    #must be of type dict
    assert type(result) == dict
