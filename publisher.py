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
from watchdog.events import RegexMatchingEventHandler

from datetime import datetime

class RunEventHandler(RegexMatchingEventHandler):
    def __init__(self, socket, regexes):
        super().__init__(regexes)
        self.socket = socket

    def on_created(self, event):
        topic = "illumina_runs"
        experiment_name = ""
        now = datetime.now().isoformat()
        time.sleep(5)

        try:
            sample_sheet = SampleSheet(os.path.join(event.src_path, 'SampleSheet.csv'))
            sample_sheet_dict = json.loads(sample_sheet.to_json())
            experiment_name = sample_sheet_dict['Header']['Experiment Name']
        except Exception as e:
            print(e)

        messagedata = {
            "timestamp": now,
            "event": "run_directory_created",
            "path": os.path.abspath(event.src_path),
            "experiment_name": experiment_name
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

    miseq_run_dir_regex = ".+/\d{6}_[A-Z0-9]{6}_\d{4}_\d{9}-[A-Z0-9]{5}$"
    illumina_run_dir_regexes = [
        miseq_run_dir_regex,
    ]

    run_event_handler = RunEventHandler(socket, regexes=illumina_run_dir_regexes)
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
