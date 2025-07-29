#   Copyright 2023 Red Hat, Inc.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.

import logging
import os
from urllib import parse

from keystoneauth1 import adapter
from keystoneauth1.exceptions import catalog as keystone_exception
import yaml

from observabilityclient.prometheus_client import PrometheusAPIClient


DEFAULT_CONFIG_LOCATIONS = (
    [os.path.join(os.environ["HOME"], ".config/openstack/"), "/etc/openstack/"]
    if "HOME" in os.environ
    else ["/etc/openstack/"]
)
CONFIG_FILE_NAME = "prometheus.yaml"
LOG = logging.getLogger(__name__)


class ConfigurationError(Exception):
    pass


def get_config_file():
    if os.path.exists(CONFIG_FILE_NAME):
        LOG.debug("Using %s as prometheus configuration", CONFIG_FILE_NAME)
        return open(CONFIG_FILE_NAME, "r")
    for path in DEFAULT_CONFIG_LOCATIONS:
        full_filename = path + CONFIG_FILE_NAME
        if os.path.exists(full_filename):
            LOG.debug("Using %s as prometheus configuration", full_filename)
            return open(full_filename, "r")
    return None


def get_prometheus_client(session=None, adapter_options={}):
    host = None
    port = None
    ca_cert = None
    root_path = ""
    conf_file = get_config_file()
    if conf_file is not None:
        conf = yaml.safe_load(conf_file)
        if 'host' in conf:
            host = conf['host']
        if 'port' in conf:
            port = conf['port']
        if 'ca_cert' in conf:
            ca_cert = conf['ca_cert']
        if 'root_path' in conf:
            root_path = conf['root_path']
        conf_file.close()

    if session is not None and (host is None or port is None):
        try:
            endpoint = adapter.Adapter(
                session=session, **adapter_options
            ).get_endpoint()
            parsed_url = parse.urlparse(endpoint)
            host = parsed_url.hostname
            port = parsed_url.port if parsed_url.port is not None else 80
            root_path = parsed_url.path.strip('/')
            if parsed_url.scheme == "https" and ca_cert is None:
                # NOTE(jwysogla): Use the default CA certs if the scheme
                # is https, but keep the original value if already set,
                # so that a custom certificate can be set in the config
                # file, while the endpoint is retrieved from keystone.
                ca_cert = True
        except keystone_exception.EndpointNotFound:
            # NOTE(jwysogla): Don't do anything here. It's still possible
            # to get the correct endpoint configuration from the env vars.
            # If that doesn't work, the same error message is part of the
            # exception raised below.
            pass

    # NOTE(jwysogla): We allow to overide the prometheus.yaml by
    #                 the environment variables
    if 'PROMETHEUS_HOST' in os.environ:
        host = os.environ['PROMETHEUS_HOST']
    if 'PROMETHEUS_PORT' in os.environ:
        port = os.environ['PROMETHEUS_PORT']
    if 'PROMETHEUS_CA_CERT' in os.environ:
        ca_cert = os.environ['PROMETHEUS_CA_CERT']
    if 'PROMETHEUS_ROOT_PATH' in os.environ:
        root_path = os.environ['PROMETHEUS_ROOT_PATH']
    if host is None or port is None:
        raise ConfigurationError("Can't find prometheus host and "
                                 "port configuration and endpoint for service"
                                 "prometheus not found.")
    client = PrometheusAPIClient(f"{host}:{port}", session, root_path)
    if ca_cert is not None:
        client.set_ca_cert(ca_cert)
    return client


def get_client(obj):
    return obj.app.client_manager.observabilityclient


def format_labels(d: dict) -> str:
    def replace_doubled_quotes(string):
        if "''" in string:
            string = string.replace("''", "'")
        if '""' in string:
            string = string.replace('""', '"')
        return string

    ret = ""
    for key, value in d.items():
        ret += "{}='{}', ".format(key, value)
    ret = ret[0:-2]
    old = ""
    while ret != old:
        old = ret
        ret = replace_doubled_quotes(ret)
    return ret


def metrics2cols(m):
    # get all label keys
    cols = list(set().union(*(d.labels.keys() for d in m)))
    cols.sort()
    cols.append("value")
    fields = []
    for metric in m:
        row = [""] * len(cols)
        for key, value in metric.labels.items():
            row[cols.index(key)] = value
        row[cols.index("value")] = metric.value
        fields.append(row)
    return cols, fields
