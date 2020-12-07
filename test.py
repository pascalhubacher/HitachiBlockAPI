import datetime
import subprocess

#2020-12-07 08:48:22.420969
datetime_object = datetime.datetime.now()
format = "%Y%m%d_%H%M%S"

#only one test by testmarker
#subprocess.check_output(['pytest', '--html=./reports/'+datetime_object.strftime(format)+'pytest.html', '-m storage_systems_get'])
#all
subprocess.check_output(['pytest', '--html=./reports/'+datetime_object.strftime(format)+'pytest.html'])