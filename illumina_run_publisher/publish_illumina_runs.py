#!/usr/bin/env python

import argparse
import json
import os
import re
import sys
import threading
import time

from datetime import datetime
from pprint import pprint

import zmq
import zmq.auth
from zmq.auth.thread import ThreadAuthenticator

from sample_sheet import SampleSheet

from watchdog.observers import Observer
from watchdog.events import RegexMatchingEventHandler


__version__ = '0.2.0-SNAPSHOT'
__author__ = 'Dan Fornika'
__email__ = 'dan.fornika@bccdc.ca'


class RunDirEventHandler(RegexMatchingEventHandler):
    def __init__(self, socket, regexes):
        super().__init__(regexes)
        self.socket = socket

    def on_modified(self, event):
        pass

    def on_moved(self, event):
        if re.search("SampleSheet.csv.[a-zA-Z0-9]{6}$", event.src_path) and re.search("SampleSheet.csv$", event.dest_path):
            now = datetime.now().isoformat()
            topic = "illumina_runs"
            experiment_name = ""

            messagedata = {
                "timestamp": now,
                "event": "sample_sheet_created",
                "path": None,
                "run_id": None,
                "experiment_name": None,
                "instrument_type": None,
                "investigator_name": None,
            }
        
            try:
                path = os.path.abspath(event.dest_path)
                run_id = str(os.path.basename(os.path.dirname(event.dest_path)))
                sample_sheet = SampleSheet(event.dest_path)
                sample_sheet_dict = json.loads(sample_sheet.to_json())
                experiment_name = sample_sheet_dict['Header']['Experiment Name']
                instrument_type = sample_sheet_dict['Header']['Instrument Type']
                investigator_name = sample_sheet_dict['Header']['Investigator Name']
            except Exception as e:
                print(e)

            messagedata['path'] = path
            messagedata['run_id'] = run_id
            messagedata['experiment_name'] = experiment_name
            messagedata['instrument_type'] = instrument_type
            messagedata['investigator_name'] = investigator_name

            message = json.dumps(messagedata)
            print("%s %s" % (topic, message))
            self.socket.send_string("%s %s" % (topic, message))
        else:
            pass

    def on_created(self, event):
        print(event.src_path)
        miseq_run_dir_regex = ".+/\d{6}_[A-Z0-9]{6}_\d{4}_\d{9}-[A-Z0-9]{5}$"
        miseq_sample_sheet_regex = ".+/.+/\d{6}_[A-Z0-9]{6}_\d{4}_\d{9}-[A-Z0-9]{5}/SampleSheet\.csv$"
        
        path = os.path.abspath(event.src_path)

        if re.search(miseq_run_dir_regex, event.src_path):
            topic = "illumina_runs"
            experiment_name = ""
            now = datetime.now().isoformat()

            messagedata = {
                "timestamp": now,
                "event": "run_directory_created",
                "path": None,
                "run_id": None,
                "run_date": None,
                "instrument_id": None,
                "flowcell_id": None
            }
        
            try:
                # path = os.path.abspath(event.src_path)
                run_dir_name = os.path.basename(path)
                run_id = run_dir_name
                date_short, instrument_id, run_num, flowcell_id = run_dir_name.split('_')
                run_date = datetime.strptime('20' + date_short, '%Y%m%d').date()
                run_date_isoformat = run_date.isoformat()
            except Exception as e:
                print(e)

            messagedata['path'] = path
            messagedata['run_id'] = run_id
            messagedata['run_date'] = run_date_isoformat
            messagedata['instrument_id'] = instrument_id
            messagedata['flowcell_id'] = flowcell_id

            message = json.dumps(messagedata)
            print("%s %s" % (topic, message))
            self.socket.send_string("%s %s" % (topic, message))



def heartbeat(socket, heartbeat_interval, print_heartbeat=False):
    topic = "illumina_runs"
    while True:
        now = datetime.now().isoformat()
        messagedata = {
            "timestamp": now,
            "event": "heartbeat",
        }
        message = json.dumps(messagedata)
        if (print_heartbeat):
            print("%s %s" % (topic, message))
        socket.send_string("%s %s" % (topic, message))
        time.sleep(heartbeat_interval)


def main(args):

    context = zmq.Context()
    socket = context.socket(zmq.PUB)

    auth = ThreadAuthenticator(context)
    auth.start()
    auth.allow('127.0.0.1')
    
    if args.public_key and args.private_key:
        auth.configure_curve(domain='*', location=zmq.auth.CURVE_ALLOW_ANY)

        server_public_file = args.public_key
        server_secret_file = args.private_key
        server_public, server_secret = zmq.auth.load_certificate(server_secret_file)
    
        socket.curve_secretkey = server_secret
        socket.curve_publickey = server_public
        socket.curve_server = True

    socket.bind("tcp://*:%s" % args.port)

    miseq_run_dir_regex = ".+/\d{6}_[A-Z0-9]{6}_\d{4}_\d{9}-[A-Z0-9]{5}$"
    miseq_sample_sheet_regex = ".+/\d{6}_[A-Z0-9]{6}_\d{4}_\d{9}-[A-Z0-9]{5}/SampleSheet.csv"
    illumina_run_dir_regexes = [
        miseq_sample_sheet_regex,
        miseq_run_dir_regex,
    ]

    run_dir_event_handler = RunDirEventHandler(socket, regexes=illumina_run_dir_regexes)

    observers = []
    for path in args.path:
        observer = Observer()
        observer.schedule(run_dir_event_handler, path, recursive=True)
        observer.start()
        observers.append(observer)

    heartbeat_thread = threading.Thread(target=heartbeat, args=([socket, args.heartbeat_interval, args.print_heartbeat]), daemon=True)
    heartbeat_thread.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        for observer in observers:
            observer.stop()
            observer.join()
        auth.stop()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', default=5556)
    parser.add_argument('--path', action='append')
    parser.add_argument('--heartbeat_interval', type=int, default=1)
    parser.add_argument('--print_heartbeat', action='store_true')
    parser.add_argument('--public_key')
    parser.add_argument('--private_key')
    args = parser.parse_args()
    main(args)
