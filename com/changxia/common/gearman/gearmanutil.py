#!/usr/bin/python
#-*-coding:utf-8-*-
import time
from gearman import *
import json
from setting import *
from gearman import DataEncoder
from common.util import *
import json
"""Json Data Encoder 目的是定义gearman的传输协议 """
class JSONDataEncoder(DataEncoder):
    @classmethod
    def encode(cls, encodable_object):
        return json.dumps(encodable_object)

    @classmethod
    def decode(cls, decodable_string):
        return json.loads(decodable_string)

def getTasksNum(task_prefix):
    for server in JOBSERVER:
        gm_admin_client = GearmanAdminClient([server ])
        # Inspect server state
        status_response = gm_admin_client.get_status()
        version_response = gm_admin_client.get_version()
        workers_response = gm_admin_client.get_workers()
        tasks = {}
        for item in workers_response:
            if len(item["tasks"]) > 0:
                task_name = item["tasks"][0].strip()
                if cmp(task_name, "") <> 0 and task_name.find(task_prefix) ==0 :
                    tasks[item["tasks"]] = 1
        if len(tasks) == 0:
            reportNagios("baidudownloader-worker wrong", NAGIOS_CRITICAL, "BaiduDownloader")
        else:
            reportNagios("baidudownloader-worker OK", NAGIOS_OK, "BaiduDownloader")
        print tasks
        return len(tasks)

def check_request_status(job_request):
    if job_request.complete:
        print "Job %s finished!  Result: %s - %s" % (job_request.job.unique, job_request.state, job_request.result)
    elif job_request.timed_out:
        print "Job %s timed out!" % job_request.unique
    elif job_request.state == JOB_UNKNOWN:
        print "Job %s connection failed!" % job_request.unique

