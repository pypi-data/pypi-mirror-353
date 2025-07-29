# lsf_prometheus_exporter

Prometheus Exporter for LSF based on https://www.gaborsamu.com/blog/lsf_tig/ 

## System Requirements
- LSF 10.1.0.15 (Fix Pack 15) or newer
- Python 3.11 or newer
- **Should only be installed on LSF management or management candidate hosts**

## Run the exporter
### Install via pip
1. Run `pip install lsf_prometheus_exporter`
2. Ensure environment variables are set by running `$LSF_ROOTDIR/conf/profile.lsf`
3. Run exporter with `python -m lsf_prometheus_exporter` or `lsf_prometheus_exporter`

### Clone the repo
1. Ensure LSF cluster is installed and running.
2. Ensure environment variables are set by running `$LSF_ROOTDIR/conf/profile.lsf`
3. Install dependencies with `pip install -r requirements.txt`
4. Start exporter with `python lsf_prometheus_exporter.py`


For statistics from `badmin perfmon`, ensure perfmon service is started with `badmin perfmon start` or set `SCHED_METRIC_ENABLE=Y` in lsb.params

For statistics from `badmin rc view`, ensure resource connector service (ebrokerd) is running

## Test the exporter

Run the following command on the same host on which you started the exporter.

```
curl http://127.0.0.1:9405/metrics
```

This assumes that the exporter runs with the default port.

## Optional Configuration
Configuring the exporter is done via environment variables.

#### LSF_PROMETHEUS_DEBUG
Y|N (default N)

Exporter will print debug messages to stdout if set to Y

#### LSF_PROMETHEUS_POLLING_INTERVAL_SECONDS
Time in Seconds (default 10)

Exporter will poll LSF for data based on this interval

#### LSF_PROMETHEUS_PORT
Port number (default 9405)

Prometheus HTTP server port.

#### LSF_PROMETHEUS_BINDING_ADDRESS
Binding address (Default "127.0.0.1")

Prometheus HTTP binding address

#### LSF_PROMETHEUS_MGR_HOST_ONLY
Y|N (default Y)

For LSF HA deployment where multiple management nodes are configured. Enable this parameter to check if the current management node is active, and only collect metrics if it is. This is to ensure metrics are not duplicated if multiple exporters are installed and running on multiple hosts in the same cluster.

#### LSF_PROMETHEUS_HOST_STATUS_DETAIL
Y|N (default N)

Enabled detailed status info for lsf_host_status

#### LSF_PROMETHEUS_EXCLUDE_COMPUTE_NODES
Y|N (default N)

Exclude compute nodes metric collection

#### LSF_PROMETHEUS_IGNORE_METRICS
String (default "")

The above variable can be used to ignore metrics. Eg: export LSF_PROMETHEUS_IGNORE_METRICS="metric1,metric2,metric3,.........,metricn"

#### LSF_PROMETHEUS_ASYNC_COLLECTORS
Y|N (default N)
Enables the use of asynchronous fetch operations when querying data from LSF

### HTTPS Configuration

#### LSF_PROMETHEUS_HTTPS_CERT_FILE
Path to certificate file (Default None)

Path to SSL certificate file. Required along with key file to enable HTTPS

#### LSF_PROMETHEUS_HTTPS_KEY_FILE
Path to key file (Default None)

Path to SSL key file. Required along with certificate file to enable HTTPS

### mTLS Configuration
Use mutual TLS to authenticate clients. HTTPS must be enabled to enable mTLS

#### LSF_PROMETHEUS_HTTPS_MTLS_ENABLE
Y|N (Default N)

Enable mTLS authentication. If the the below mTLS parameters are not configured, then a default CA certificate chain will be used (see https://docs.python.org/3/library/ssl.html#ssl.SSLContext.load_default_certs)

#### LSF_PROMETHEUS_HTTPS_MTLS_CAFILE
Path to CA file (Default None)

CA file with certificate chain used to validate client certificates

#### LSF_PROMETHEUS_HTTPS_MTLS_CAPATH
Path to CA directory (Default None)

Directory containing CA certificate chain used to validate client certificates

## lsf_prometheus_exporter.py
Primary entry point. Instantiates exporter classes and starts the http server while running an infinite fetch loop
