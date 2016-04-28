import libvirt
import loop
from threading import Thread
from gevent import sleep
import time

do_debug = False


def debug(msg):
    global do_debug
    if do_debug:
        print(msg)


class LibvirtEventBroker(Thread):

    def __init__(self, con_str='qemu:///system'):
        Thread.__init__(self)
        self._con_str = con_str
        self._subscriptions = set()

    def subscribe(self, subscriber):
        debug("Adding subscription")
        self._subscriptions.add(subscriber)
        return subscriber

    def unsubscribe(self, queue):
        debug("Removing Subscription")
        queue.put(StopIteration)
        self._subscriptions.remove(queue)

    def run(self):
        loop.virEventLoopPureRegister()
        libvirt.registerErrorHandler(error_handler, self)

        while True:
            conn = libvirt.openReadOnly(self._con_str)
            if not conn:
                print('Failed to open connection to the hypervisor')
                sleep(5)
                continue
            # XXX: This does not really stop the event loop when an error
            # occurs
            conn.registerCloseCallback(connection_close_callback, self)
            conn.domainEventRegister(lifecycle_callback, self)
            loop.virEventLoopPureRun()


def connection_close_callback(conn, reason, opaque):
    reasonStrings = ("Error", "End-of-file", "Keepalive", "Client",)
    print("myConnectionCloseCallback: %s: %s" %
          (conn.getURI(), reasonStrings[reason]))


def error_handler(unused, error, listener):
    print(error)


def lifecycle_callback(connection, domain, event, detail, listener):
    debug("event received")
    e = create_event(domain.name(), domain.UUIDString(), event, detail)
    for subscriber in listener._subscriptions:
        subscriber.put(e)


def create_event(name, uuid, event, reason):
    return {
        'domain_name': name,
        'domain_id': uuid,
        'timestamp': time.time(),
        'event_type': domEventToString(event),
        'reason': domDetailToString(event, reason)
    }


def domEventToString(event):
    domEventStrings = ("Defined",
                       "Undefined",
                       "Started",
                       "Suspended",
                       "Resumed",
                       "Stopped",
                       "Shutdown",
                       "PMSuspended",
                       "Crashed",
                       )
    return domEventStrings[event]


def domDetailToString(event, detail):
    domEventStrings = (
        ("Added", "Updated"),
        ("Removed", ),
        ("Booted", "Migrated", "Restored", "Snapshot", "Wakeup"),
        ("Paused", "Migrated", "IOError", "Watchdog",
         "Restored", "Snapshot", "API error"),
        ("Unpaused", "Migrated", "Snapshot"),
        ("Shutdown", "Destroyed", "Crashed",
         "Migrated", "Saved", "Failed", "Snapshot"),
        ("Finished", ),
        ("Memory", "Disk"),
        ("Panicked", ),
    )
    return domEventStrings[event][detail]
