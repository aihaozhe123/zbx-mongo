#! /usr/bin/python
# -*- coding: utf-8 -*-

from pymongo import MongoClient, errors
from pyzabbix import ZabbixMetric, ZabbixSender
import sys


TIMEOUT = 10000


__author__ = 'Junior Lima'
__email__ = 'josiasjuniorx@gmail.com'
__license__ = 'GPL'
__version__ = '1.0'


"""
    Script para monitorar MongoDB
        Usage:
                zbx_mongo.py [MONGODB] [HOSTNAME] [ZABBIX_SERVER]

"""


def get_data(MONGOSERVER):
    try:
        connection = MongoClient(MONGOSERVER, serverSelectionTimeoutMS=TIMEOUT)
        database = connection.data
        server_status = database.command({"serverStatus": 1})
        connection.close()
    except errors.ServerSelectionTimeoutError:
        print "Connection error with MongoDB"
        sys.exit(1)
    return server_status


def build_information(data, HOSTNAME):
    all_metrics = [
        ZabbixMetric(HOSTNAME, 'uptime', data['uptime']),
        ZabbixMetric(HOSTNAME, 'version', data['version']),
        ZabbixMetric(HOSTNAME, 'opcounters.getmore', data['opcounters']['query']),
        ZabbixMetric(HOSTNAME, 'opcounters.query', data['opcounters']['getmore']),
        ZabbixMetric(HOSTNAME, 'opcounters.insert', data['opcounters']['insert']),
        ZabbixMetric(HOSTNAME, 'opcounters.update', data['opcounters']['update']),
        ZabbixMetric(HOSTNAME, 'opcounters.delete', data['opcounters']['delete']),
        ZabbixMetric(HOSTNAME, 'globalLock.activeClients.readers', data['globalLock']['activeClients']['readers']),
        ZabbixMetric(HOSTNAME, 'globalLock.activeClients.writers', data['globalLock']['activeClients']['writers']),
        ZabbixMetric(HOSTNAME, 'metrics.cursor.open.total', data['metrics']['cursor']['open']['total']),
        ZabbixMetric(HOSTNAME, 'metrics.cursor.timedOut', data['metrics']['cursor']['timedOut']),
        ZabbixMetric(HOSTNAME, 'metrics.cursor.open.noTimeout', data['metrics']['cursor']['open']['noTimeout']),
        ZabbixMetric(HOSTNAME, 'metrics.record.moves', data['metrics']['record']['moves']),
        ZabbixMetric(HOSTNAME, 'connections.current', data['connections']['current']),
        ZabbixMetric(HOSTNAME, 'connections.available', data['connections']['available']),
        ZabbixMetric(HOSTNAME, 'mem.virtual', data['mem']['virtual']),
        ZabbixMetric(HOSTNAME, 'mem.resident', data['mem']['resident']),
        ZabbixMetric(HOSTNAME, 'mem.mapped', data['mem']['mapped']),
        ZabbixMetric(HOSTNAME, 'mem.mappedWithJournal', data['mem']['mappedWithJournal']),
        ZabbixMetric(HOSTNAME, 'extra_info.page_faults', data['extra_info']['page_faults']),
        ZabbixMetric(HOSTNAME, 'globalLock.currentQueue.readers', data['globalLock']['currentQueue']['readers']),
        ZabbixMetric(HOSTNAME, 'globalLock.currentQueue.writers', data['globalLock']['currentQueue']['writers']),
        ZabbixMetric(HOSTNAME, 'asserts.msg', data['asserts']['msg']),
        ZabbixMetric(HOSTNAME, 'asserts.warning', data['asserts']['warning']),
        ZabbixMetric(HOSTNAME, 'asserts.regular', data['asserts']['regular']),
        ZabbixMetric(HOSTNAME, 'asserts.user', data['asserts']['user'])
    ]
    try:
        metrics_wired = [
            ZabbixMetric(HOSTNAME, 'wiredTiger.concurrentTransactions.read.out', data[
                         'wiredTiger']['concurrentTransactions']['read']['out']),
            ZabbixMetric(HOSTNAME, 'wiredTiger.concurrentTransactions.write.out', data[
                         'wiredTiger']['concurrentTransactions']['write']['out']),
            ZabbixMetric(HOSTNAME, 'wiredTiger.concurrentTransactions.read.available', data[
                         'wiredTiger']['concurrentTransactions']['read']['available']),
            ZabbixMetric(HOSTNAME, 'wiredTiger.concurrentTransactions.write.available', data[
                         'wiredTiger']['concurrentTransactions']['write']['available']),
            ZabbixMetric(HOSTNAME, 'wiredTiger.cache.bytes_currently_in_the_cache',
                         data['wiredTiger']['cache']['bytes currently in the cache']),
            ZabbixMetric(HOSTNAME, 'wiredTiger.cache.maximum_bytes_configured',
                         data['wiredTiger']['cache']['maximum bytes configured']),
            ZabbixMetric(HOSTNAME, 'wiredTiger.cache.tracked_dirty_bytes_in_the_cache',
                         data['wiredTiger']['cache']['tracked dirty bytes in the cache']),
            ZabbixMetric(HOSTNAME, 'wiredTiger.cache.unmodified_pages_evicted',
                         data['wiredTiger']['cache']['unmodified pages evicted']),
            ZabbixMetric(HOSTNAME, 'wiredTiger.cache.modified_pages_evicted',
                         data['wiredTiger']['cache']['modified pages evicted'])
        ]
        all_metrics.extend(metrics_wired)
    except:
        pass
    try:
        metrics_dur = [
            ZabbixMetric(HOSTNAME, 'dur.commits', data['dur']['commits']),
            ZabbixMetric(HOSTNAME, 'dur.journaledMB', data['dur']['journaledMB'])
        ]
        all_metrics.extend(metrics_dur)
    except:
        pass
    return all_metrics


def send_information_to_zabbix(ZABBIX_SERVER, information):
    try:
        send = ZabbixSender(ZABBIX_SERVER).send(information)
    except:
        print "An error occurred in sending the data"
        sys.exit()
    print "Succesful={}   Failed={}   Total={}   Elapsed Time={}".format(send.processed, send.failed, send.total, send.time)


def main(MONGO_SERVER, HOSTNAME, ZABBIX_SERVER):
    data = get_data(MONGO_SERVER)
    information = build_information(data, HOSTNAME)
    send_information_to_zabbix(ZABBIX_SERVER, information)


if __name__ == "__main__":
    if len(sys.argv) > 3:
        main(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        print "\nUsage: \nzbx_mongo.py [MONGODB] [HOSTNAME] [ZABBIX_SERVER]\n"
        sys.exit()
