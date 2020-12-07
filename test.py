import datetime
#import subprocess
import os

#2020-12-07 08:48:22.420969
datetime_object = datetime.datetime.now()
format = "%Y%m%d_%H%M%S"

#only one test by testmarker
#subprocess.check_output(['pytest', '-v', '--html=./reports/'+datetime_object.strftime(format)+'pytest.html', '-m storage_systems_get'])
#os.system('pytest --html=./reports/'+datetime_object.strftime(format)+'pytest.html -m storage_device_id_set')
#all
os.system('pytest --html=./reports/'+datetime_object.strftime(format)+'pytest.html')