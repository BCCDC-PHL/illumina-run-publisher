#!/usr/bin/env python

import argparse
import sys
import zmq
import zmq.auth

def main(args):

    # Socket to talk to server
    context = zmq.Context()
    socket = context.socket(zmq.SUB)

    if args.public_key and args.private_key:
        client_secret_file = args.private_key
        client_public, client_secret = zmq.auth.load_certificate(client_secret_file)
        socket.curve_secretkey = client_secret
        socket.curve_publickey = client_public
        server_public_file = args.public_key
        server_public, _ = zmq.auth.load_certificate(server_public_file)
        socket.curve_serverkey = server_public

    print("Collecting updates from server...")
    socket.connect("tcp://127.0.0.1:%s" % args.port)

    socket.subscribe("illumina_runs")

    while True:
        # Receives a string format message
        print(socket.recv_string())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', default=5556)
    parser.add_argument('--public_key')
    parser.add_argument('--private_key')
    args = parser.parse_args()
    main(args)
