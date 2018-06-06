import time,os,signal
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
			os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
			return 'failed'
		time.sleep(interval)


def try_several_times(command,trials,seconds):
	for trial in range(trials):
		proc=sub.Popen(command,stdout=sub.PIPE,
                       shell=True, preexec_fn=os.setsid)
		print(os.getpgid(proc.pid))
		result=wait_timeout(proc,seconds)
		if result!='failed':
			break
	return(result)


os.chdir('/Users/peterpfleiderer/Documents/Projects/Persistence/data/tests/raw/')

result=try_several_times('cdo bandpass,60,180 tas_Aday_NorESM1-HAPPI_All-Hist_est1_v1-0_run010_20060101-20160630.nc test.nc',5,2)
