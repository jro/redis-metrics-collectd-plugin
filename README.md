redis-metrics-collectd-plugin
=====================

A plugin for [collectd](http://collectd.org) that takes data out of a
hash in [Redis](http://redis.google.code.com).  Current use is for 
taking counter style data, but there could be other uses

Install
-------
 1. Place redis_metrics.py in  (or wherever you define for python
 plugins)
 2. Configure the plugin (see below).
 3. Restart collectd.

Configuration
-------------
Add the following to your collectd config **or** use the included
redis_metrics.conf.


  # Configure the redis-metrics plugin
  <Plugin python>
    ModulePath "/usr/lib64/collectd/plugins/python"
    Import "redis_metrics"
  
    <Module redis_metrics>
      Host "localhost"
      Port 6379
      Verbose true
      # Other RRD data type fly here too
      Counter true
      Gauge true
      # Name of the hash containing keys with data
      Metrics_Hash "my_metrics"
    </Module>
  </Plugin>


Requirements
------------
 * collectd 4.9+
 * [redis-py](https://github.com/andymccurdy/redis-py) python redis library
