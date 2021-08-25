#!/usr/bin/env python3

import sys
import subprocess
import xml.etree.cElementTree as ET
from time import sleep

SLEEP_TIME = 30
jobid = sys.argv[1]

try:
    res = subprocess.run("qstat -f -x {}".format(jobid), check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)

    xmldoc = ET.ElementTree(ET.fromstring(res.stdout.decode())).getroot()
    job_state = xmldoc.findall('.//job_state')[0].text

    if job_state == "C":
        exit_status = xmldoc.findall('.//exit_status')[0].text
        if exit_status == '0':
            sleep(SLEEP_TIME) # wait before reporting success to deal with NFS latency
            print("success")
        else:
            print("failed")
    else:
        print("running")

except (subprocess.CalledProcessError, IndexError, KeyboardInterrupt) as e:
    # check log file instead; this can report a failure if the job is no longer
    # reported by qstat
    # print("failed")
    failure = True
    import os
    from datetime import date
    from glob import glob
    log_directory = f"/oasis/tscc/scratch/{os.getlogin()}/TORQUE/logs/{date.today()}"
    error_logs = glob(f"{log_directory}/*.e{jobid}")
    if len(error_logs) == 1:
        with open(error_logs[0]) as log_fh:
            for line in log_fh:
                pass
        if line.endswith("(100%) done\n"):
            failure = False
            print("success")
    if failure:
        print("failed")
