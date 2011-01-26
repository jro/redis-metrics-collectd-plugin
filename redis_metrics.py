# redis-metrics-collectd-plugin - redis_metrics.py
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; only version 2 of the License is applicable.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA
#
# Authors:
#   Jason Rohwedder <jason@viewpoints.com>
#
# About this plugin:
#   This plugin uses 
#
# collectd:
#   http://collectd.org
# Redis:
#   http://redis.googlecode.com
# collectd-python:
#   http://collectd.org/documentation/manpages/collectd-python.5.shtml
# redis-py
#   https://github.com/andymccurdy/redis-py
#
# Based on:
# redis-collectd-plugin
#   https://github.com/powdahound/redis-collectd-plugin

import collectd
import socket
import redis

# Host to connect to. Override in config by specifying 'Host'.
REDIS_HOST = 'localhost'

# Port to connect on. Override in config by specifying 'Port'.
REDIS_PORT = 6379

# Verbose logging on/off. Override in config by specifying 'Verbose'.
VERBOSE_LOGGING = False

# Name for hash containing metrics.  Override in config by specifying 'Metrics_Hash'.
METRICS_HASH = 'metrics'

# Record as X data type: defaults to counter
RECORD_AS_COUNTER = True
RECORD_AS_DERIVE = False
RECORD_AS_GAUGE = False
RECORD_AS_ABSOLUTE = False

def fetch_metrics():
    """Connect to Redis server and request info"""
    try:
        s = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
        log_verbose('Connected to Redis at %s:%s' % (REDIS_HOST, REDIS_PORT))
    except socket.error, e:
        collectd.error('redis_metrics plugin: Error connecting to %s:%d - %r'
                       % (REDIS_HOST, REDIS_PORT, e))
        return None
    log_verbose('Retrieving data')
    data = s.hgetall(METRICS_HASH)
    log_verbose('Recieved data: %s' % data)

    return data


def configure_callback(conf):
    """Receive configuration block"""
    global REDIS_HOST, REDIS_PORT, VERBOSE_LOGGING, METRICS_HASH
    global RECORD_AS_COUNTER, RECORD_AS_DERIVE, RECORD_AS_GAUGE, RECORD_AS_ABSOLUTE
    for node in conf.children:
        if node.key == 'Host':
            REDIS_HOST = node.values[0]
        elif node.key == 'Port':
            REDIS_PORT = int(node.values[0])
        elif node.key == 'Verbose':
            VERBOSE_LOGGING = bool(node.values[0])
        elif node.key == 'Metrics_Hash':
            METRICS_HASH = node.values[0]
        elif node.key == 'Counter':
            RECORD_AS_COUNTER = bool(node.values[0])
        elif node.key == 'Derive':
            RECORD_AS_DERIVE = bool(node.values[0])
        elif node.key == 'Gauge':
            RECORD_AS_GAUGE = bool(node.values[0])
        elif node.key == 'Absolute':
            RECORD_AS_ABSOLUTE = bool(node.values[0])
        else:
            collectd.warning('redis_metrics plugin: Unknown config key: %s.'
                             % node.key)
    log_verbose('Configured with host=%s, port=%s' % (REDIS_HOST, REDIS_PORT))


def dispatch_value(metric, value, type):
    """Dispatch a metric into collectd"""
    log_verbose('Sending metric: %s=%s as type %s' % (metric, value,type))

    val = collectd.Values(plugin='redis_metrics')
    val.type = type
    val.type_instance = metric
    val.values = [value]
    val.dispatch()


def read_callback():
    log_verbose('Read callback called')
    metrics = fetch_metrics()

    if not metrics:
        collectd.error('redis_metrics plugin: No metrics received')
        return

    for metric, value in metrics.iteritems():
        log_verbose('Dispatching metric %s : %s' % (metric,value))
        if RECORD_AS_COUNTER:
          dispatch_value(metric,value,'counter')
        if RECORD_AS_DERIVE:
          dispatch_value(metric,value,'derive')
        if RECORD_AS_GAUGE:
          dispatch_value(metric,value,'gauge')
        if RECORD_AS_ABSOLUTE:
          dispatch_value(metric,value,'absolute')

def log_verbose(msg):
    if not VERBOSE_LOGGING:
        return
    collectd.info('redis_metrics plugin [verbose]: %s' % msg)


# register callbacks
collectd.register_config(configure_callback)
collectd.register_read(read_callback)
