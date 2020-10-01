#!/usr/bin/env python

# A publisher has no connected subscribers, then it will simply drop all messages.
# If you’re using TCP, and a subscriber is slow, messages will queue up on the publisher.
# In the current versions of ØMQ, filtering happens at the subscriber side, not the publisher side.

import argparse
import zmq
import random
import sys
import time
import json

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from datetime import datetime

class RunEventHandler(FileSystemEventHandler):
    def __init__(self, socket):
        self.recursive=False
        self.socket = socket
        
    def on_created(self, event):
        topic = "illumina_runs"
        now = datetime.now().isoformat()
        messagedata = {
            "timestamp": now,
            "event": "new_run",
            "path": event.src_path,
        }
        message = json.dumps(messagedata)
        print("%s %s" % (topic, message))
        self.socket.send_string("%s %s" % (topic, message))

def heartbeat(socket):
    topic = "illumina_runs"
    now = datetime.now().isoformat()
    messagedata = {
        "timestamp": now,
        "event": "heartbeat",
    }
    message = json.dumps(messagedata)
    print("%s %s" % (topic, message))
    socket.send_string("%s %s" % (topic, message))
        
def main(args):

    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind("tcp://*:%s" % args.port)

    run_event_handler = RunEventHandler(socket)
    observer = Observer()
    observer.schedule(run_event_handler, args.path, recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
            heartbeat(socket)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', default=5556)
    parser.add_argument('--path')
    args = parser.parse_args()
    main(args)
