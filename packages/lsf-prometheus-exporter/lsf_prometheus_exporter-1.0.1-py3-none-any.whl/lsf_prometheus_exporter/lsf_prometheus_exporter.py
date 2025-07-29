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

import os
import time
import asyncio
import prometheus_client as prom
if __name__ == "__main__":
    from cmdline_collectors import BqueuesCollector, BadminCollector, BhostsCollector, LsloadCollector, LsidCollector
    from lib_collectors import PsutilCollector
    from metrics_utils import Utils
else:
    from lsf_prometheus_exporter.cmdline_collectors import BqueuesCollector, BadminCollector, BhostsCollector, LsloadCollector, LsidCollector
    from lsf_prometheus_exporter.lib_collectors import PsutilCollector
    from lsf_prometheus_exporter.metrics_utils import Utils

class LsfMetrics:
    """
    Representation of Prometheus metrics and loop to fetch and transform
    application metrics into Prometheus metrics.
    """

    def __init__(self):
        self.__initialize_environment_variables__()
        self.utils = Utils(self.debug, self.lsf_bindir, self.detailed_host_status, self.exclude_compute_nodes, self.mgr_host_only)

    def __initialize_environment_variables__(self):
        # Exporter will poll LSF for data based on this interval
        self.polling_interval_seconds = int(os.getenv("LSF_PROMETHEUS_POLLING_INTERVAL_SECONDS", "10"))

        self.lsf_bindir = os.getenv('LSF_BINDIR', '')

        # Exporter will print debug messages to stdout if set to Y
        debug = os.getenv('LSF_PROMETHEUS_DEBUG', 'N')
        if debug.upper() == 'Y':
            self.debug = True
        else:
            self.debug = False

        # Enabled detailed status info for lsf_host_status
        detailed_host_status = os.getenv('LSF_PROMETHEUS_HOST_STATUS_DETAIL', 'N')
        if detailed_host_status.upper() == 'Y':
            self.detailed_host_status = True
        else:
            self.detailed_host_status = False

        # Exclude compute nodes metric collection
        exclude_compute_nodes = os.getenv('LSF_PROMETHEUS_EXCLUDE_COMPUTE_NODES', 'N')
        if exclude_compute_nodes.upper() == 'Y':
            self.exclude_compute_nodes = True
        else:
            self.exclude_compute_nodes = False

        # For LSF HA deployment where multiple management nodes are configured.
        # Enable this parameter to check if the current management node is active, and only collect metrics if it is.
        # This is to ensure metrics are not duplicated if multiple exporters are installed and running on multiple hosts in the same cluster.
        self.mgr_host_only = True
        mgrhost = os.getenv("LSF_PROMETHEUS_MGR_HOST_ONLY", 'Y')
        if mgrhost.upper() == 'N':
            self.mgr_host_only = False
        elif mgrhost.upper() == 'Y':
            self.mgr_host_only = True
        else:
            print("Invalid value for LSF_PROMETHEUS_MGR_HOST_ONLY. Using default")

        # Server configuration
        self.binding_address = os.getenv("LSF_PROMETHEUS_BINDING_ADDRESS", "127.0.0.1")
        self.exporter_port = int(os.getenv("LSF_PROMETHEUS_PORT", "9405"))

        # HTTPS configuration
        self.cert_file = os.getenv("LSF_PROMETHEUS_HTTPS_CERT_FILE", None)
        self.key_file = os.getenv("LSF_PROMETHEUS_HTTPS_KEY_FILE", None)

        self.client_auth = False

        # optional mTLS configuration
        if os.getenv("LSF_PROMETHEUS_HTTPS_MTLS_ENABLE", "N").upper() == "Y":
            self.client_auth = True
        self.client_cafile = os.getenv("LSF_PROMETHEUS_HTTPS_MTLS_CAFILE", None)
        self.client_capath = os.getenv("LSF_PROMETHEUS_HTTPS_MTLS_CAPATH", None)

        # Enable async collectors
        self.async_collectors = False
        if os.getenv("LSF_PROMETHEUS_ASYNC_COLLECTORS", "N").upper() == "Y":
            self.async_collectors = True

    def __initialize_collectors__(self):
        """Initialize collectors Pyhton object.
        """
        self.bqueues = BqueuesCollector(self.utils)
        self.badmin = BadminCollector(self.utils)
        self.bhosts = BhostsCollector(self.utils)
        self.lsload = LsloadCollector(self.utils)
        self.lsid = LsidCollector(self.utils)
        self.psutil = PsutilCollector(self.utils)

    def __reset_prom_collectors__(self) -> None:
        """Resets collectors in the default Prometheus registry.
        Modifies the `REGISTRY` registry. Supposed to be called at the beginning
        of individual test functions. Else registry is reused across test functions
        and so we can run into errors like duplicate metrics or unexpected values
        for metrics.
        """
        # Unregister all collectors.
        collectors = list(prom.REGISTRY._collector_to_names.keys())
        if self.debug:
            print(f"Unregistering following collectors={collectors}")
        for collector in collectors:
            prom.REGISTRY.unregister(collector)

    def __run_metrics_loop__(self):
        """Metrics fetching loop"""
        collectors_initialized = False
        already_reset = False
        while True:
            # try/catch needed in case of switch between master
            # output of self.__lsid_output() (lsid command) could contain 'lsid: ls_getentitlementinfo() failed: Master LIM is down; try later'
            try:
                #lsid called one time for all the scopes
                active_management, lsid_cluster_info = self.utils.get_lsid_output()
                if active_management:
                    if already_reset:
                        already_reset = False
                    if not collectors_initialized:
                        collectors_initialized = True
                        self.__initialize_collectors__()
                    if not self.async_collectors:
                        self.__fetch__(lsid_cluster_info)
                    else:
                        asyncio.run(self.__fetch_async__(lsid_cluster_info), debug=self.debug)
                else:
                    if not already_reset:
                        already_reset = True
                        self.__reset_prom_collectors__()
                    if collectors_initialized:
                        collectors_initialized = False
                    if self.debug:
                        print("Not active management! Skipping fetch cycle")
            except Exception as err:
                if self.debug:
                    print(Exception, err)
                pass
            time.sleep(self.polling_interval_seconds)


    def __fetch__(self, lsid_cluster_info):
        """
        Get metrics from application and refresh Prometheus metrics with
        new values.
        """
        with asyncio.Runner(debug=self.debug) as runner:
            runner.run(self.bqueues.fetch_async(lsid_cluster_info))
            runner.run(self.badmin.fetch_perfmon_view_async(lsid_cluster_info))
            runner.run(self.badmin.fetch_rc_view_async(lsid_cluster_info))
            runner.run(self.badmin.fetch_showstatus_async(lsid_cluster_info))
            runner.run(self.bhosts.fetch_async(lsid_cluster_info))
            runner.run(self.lsload.fetch_async(lsid_cluster_info))
            runner.run(self.psutil.fetch_async(lsid_cluster_info))
            runner.run(self.lsid.fetch_async(lsid_cluster_info))

    async def __fetch_async__(self, lsid_cluster_info):
        """
        Asynchronous version of __fetch__
        """
        async with asyncio.TaskGroup() as group:
            group.create_task(self.bqueues.fetch_async(lsid_cluster_info))
            group.create_task(self.badmin.fetch_perfmon_view_async(lsid_cluster_info))
            group.create_task(self.badmin.fetch_rc_view_async(lsid_cluster_info))
            group.create_task(self.badmin.fetch_showstatus_async(lsid_cluster_info))
            group.create_task(self.bhosts.fetch_async(lsid_cluster_info))
            group.create_task(self.lsload.fetch_async(lsid_cluster_info))
            group.create_task(self.psutil.fetch_async(lsid_cluster_info))
            group.create_task(self.lsid.fetch_async(lsid_cluster_info))

    def start(self):
        """Main entry point"""
        prom.start_http_server(port=self.exporter_port,
                          addr=self.binding_address,
                          certfile=self.cert_file,
                          keyfile=self.key_file,
                          client_cafile=self.client_cafile,
                          client_capath=self.client_capath,
                          client_auth_required=self.client_auth)

        #remove default metrics (eg: python metrics) from the exporter
        prom.REGISTRY.unregister(prom.PROCESS_COLLECTOR)
        prom.REGISTRY.unregister(prom.PLATFORM_COLLECTOR)
        prom.REGISTRY.unregister(prom.GC_COLLECTOR)

        #run loop function to fetch the metrics
        self.__run_metrics_loop__()

def main():
    lsf_metrics = LsfMetrics()
    lsf_metrics.start()

if __name__ == "__main__":
    main()
