from xml.etree import ElementTree
from datetime import datetime
from .conn import LibvirtConnection


class Collector:

    def __init__(self, conn=LibvirtConnection()):
        self._conn = conn

    def collect(self):
        stats = []
        with self._conn as conn:
            domainIDs = conn.listDomainsID()
            if not domainIDs:
                return stats
            for domainID in domainIDs:
                domain = conn.lookupByID(domainID)
                tree = ElementTree.fromstring(domain.XMLDesc())
                interfaces = []
                for iface in tree.findall('devices/interface/target'):
                    name = iface.get('dev')
                    ifStats = domain.interfaceStats(name)
                    interfaces.append({
                        'name': name,
                        'rx_bytes': ifStats[0],
                        'rx_packets': ifStats[1],
                        'rx_errors': ifStats[2],
                        'rx_drops': ifStats[3],
                        'tx_bytes': ifStats[4],
                        'tx_packets': ifStats[5],
                        'tx_errors': ifStats[6],
                        'tx_dropped': ifStats[7],
                    }
                    )
                disks = []
                for disk in tree.findall('devices/disk/target'):
                    name = disk.get('dev')
                    diskStats = domain.blockStats(name)
                    disks.append({
                        'name': name,
                        'rd_req': diskStats[0],
                        'rd_bytes': diskStats[1],
                        'wr_req': diskStats[2],
                        'wr_bytes': diskStats[3],
                        'errors': diskStats[4],
                    })
                domainName = domain.name()
                domainUUID = domain.UUIDString()
                domainStats = {}
                domainStats['uuid'] = domainUUID
                domainStats['name'] = domainName
                domainStats['memory'] = domain.memoryStats()
                domainStats['cpu'] = {
                    "usage": domain.getCPUStats(True)[0],
                    "per_cpu_usage": domain.getCPUStats(False),
                }
                domainStats['network'] = {
                    'interfaces': interfaces
                }
                domainStats['diskio'] = disks
                domainStats['timestamp'] = datetime.utcnow()
                stats.append(domainStats)
        return stats
