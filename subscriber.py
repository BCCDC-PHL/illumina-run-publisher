#!/usr/bin/env python

import sys
import zmq


def main(args):

    # Socket to talk to server
    context = zmq.Context()
    socket = context.socket(zmq.SUB)

    print("Collecting updates from server...")
    socket.connect("tcp://localhost:%s" % args.port)

    socket.subscribe("illumina_runs")

    while True:
        # Receives a string format message
        print(socket.recv())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', default=5556)
    args = parser.parse_args()
    main(args)
