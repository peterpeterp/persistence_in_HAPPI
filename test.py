import time
import subprocess as sub

def wait_timeout(proc, seconds):
    """Wait for a process to finish, or raise exception after timeout"""
    start = time.time()
    end = start + seconds
    interval = min(seconds / 1000.0, .25)

    while True:
        result = proc.poll()
        if result is not None:
            return result
        if time.time() >= end:
            raise RuntimeError("Process timed out")
        time.sleep(interval)


os.chdir('/Users/peterpfleiderer/Documents/Projects/Persistence/data/tests/raw/')

proc=sub.Popen('cdo bandpass,60,180 tas_Aday_NorESM1-HAPPI_All-Hist_est1_v1-0_run010_20060101-20160630.nc test.nc',shell=True)
wait_timeout(proc, 10)
