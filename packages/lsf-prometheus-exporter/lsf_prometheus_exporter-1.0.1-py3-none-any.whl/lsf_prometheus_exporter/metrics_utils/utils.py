# Copyright International Business Machines Corp, 2025
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import asyncio
import json
import subprocess
import os
from prometheus_client import Gauge, Info, Counter
import socket

class Utils:
    """
    Utils module for metrics
    """
    def __init__(self, debug_flag:bool, lsf_bindir:str, detailed_host_status:bool, filter_metrics_compute_nodes:bool, mgr_host_only:bool) -> None:
        assert lsf_bindir
        self.debug = debug_flag
        self.lsf_bindir = lsf_bindir
        self.detailed_host_status = detailed_host_status
        self.filter_metrics_compute_nodes = filter_metrics_compute_nodes
        self.mgr_host_only = mgr_host_only

    def create_metrics(self, metrics_list):
        try:
            # env variable use to ignore metrics: export LSF_PROMETHEUS_IGNORE_METRICS="metric1,metric2,metric3,.........,metricn"
            ignored_metrics = os.environ["LSF_PROMETHEUS_IGNORE_METRICS"].join(",")
        except:
            ignored_metrics = []

        updated_metrics = metrics_list
        if len(ignored_metrics) > 0:
            updated_metrics = []
            for (name, desc, metric_type, labels_list, label) in metrics_list:
                if name not in ignored_metrics:
                    updated_metrics.append((name, desc, metric_type, labels_list, label))

        result_metrics = []
        for (name, desc, metric_type, labels_list, label) in updated_metrics:
            if metric_type == "Gauge":
                metric = Gauge(name, desc, labels_list)
            if metric_type == "Info":
                metric = Info(name, desc)
            if metric_type == "Counter":
                metric = Counter(name, desc)
            result_metrics.append((metric, name, label))
        return result_metrics

    def collect_data(self, command, env, print1, print2):
        try:
            command[0] = self.lsf_bindir + "/" + command[0]
        except:
            pass
        if env != "":
            p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, env=env)
        else:
            p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        stdout, stderr = p.communicate()
        if p.returncode != 0:
            if self.debug:
                print(print1, print2)
            return "", "", False
        try:
            return json.loads(stdout), stdout, True
        except:
            return "", stdout, True

    async def collect_data_async(self, command, env, print1, print2):
        try:
            command[0] = self.lsf_bindir + "/" + command[0]
        except:
            pass
        if env != "":
            p = await asyncio.subprocess.create_subprocess_shell(' '.join(command), stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL, env=env)
        else:
            p = await asyncio.subprocess.create_subprocess_shell(' '.join(command), stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL)

        stdout, stderr = await p.communicate()
        returncode = await p.wait()
        if returncode != 0:
            if self.debug:
                print(print1, print2)
            return "", "", False
        try:
            output = stdout.decode()
            return json.loads(output), output, True
        except json.JSONDecodeError:
            return "", stdout.decode(), True
        except UnicodeError:
            return "", "", False

    def __is_active_management__(self, lsid_fail, lsid_mgmt_name) -> bool:
        """
        Determine if the host this script is running
        on is the active LSF management host
        """
        if not self.mgr_host_only:
            return True

        # Determine if the host is active LSF management node
        # Grab management host name from lsid
        if lsid_fail:
            return False

        # Grab current host name
        curr_host_name = socket.gethostname().lower()
        if self.debug:
            print(f"hostname={curr_host_name}")
        if curr_host_name.find(lsid_mgmt_name) < 0 and lsid_mgmt_name.find(curr_host_name) < 0:
            return False
        else:
            return True

    def get_lsid_output(self):
        lsid_cluster_name, lsid_cluster_version, lsid_mgmt_name = "", "", ""
        _, stdout, return_bool = self.collect_data("lsid", "", "lsid fail", "")
        lsid_fail = True
        if return_bool:
            lines = stdout.splitlines()
            lsid_cluster_version = lines[0]
            if len(lines) >= 6:
                lsid_fail = False
                if lines[-2].find("My cluster name is ") >= 0:
                    lsid_cluster_name = lines[-2].replace("My cluster name is ", "").lower()
                if lines[-1].find("My master name is ") >= 0:
                    lsid_mgmt_name = lines[-1].replace("My master name is ", "").lower()
                if self.debug:
                    print(f"ibm_lsid_cluster_name={lsid_cluster_name}\nmgmt_host_name={lsid_mgmt_name}")
            else:
                # lsid failed somehow
                if self.debug:
                    print("unexpected lsid output")
        active_management = self.__is_active_management__(lsid_fail, lsid_mgmt_name)
        lsid_cluster_info = {"cluster_name": lsid_cluster_name, "cluster_version": lsid_cluster_version}
        return active_management, lsid_cluster_info
