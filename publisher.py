#!/usr/bin/env python

import argparse
import zmq
import random
import os
import sys
import time
import json

from sample_sheet import SampleSheet

from pprint import pprint

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
        time.sleep(5)
        try:
            sample_sheet = SampleSheet(os.path.join(event.src_path, 'SampleSheet.csv'))
        except FileNotFoundError as e:
            print(e)

        sample_sheet_dict = json.loads(sample_sheet.to_json())

        messagedata = {
            "timestamp": now,
            "event": "run_directory_created",
            "path": os.path.abspath(event.src_path),
            "experiment_name": sample_sheet_dict['Header']['Experiment Name']
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
