#!/usr/bin/env python

# Subscribers are created with ZMQ.SUB socket types.
# A zmq subscriber can connect to many publishers.
import sys
import zmq


port = "5556"
if len(sys.argv) > 1:
    port = sys.argv[1]
    int(port)


# Socket to talk to server
context = zmq.Context()
socket = context.socket(zmq.SUB)

print("Collecting updates from server...")
socket.connect("tcp://localhost:%s" % port)

# Subscribes to all topics you can selectively create multiple workers
# that would be responsible for reading from one or more predefined topics
# if you have used AWS SNS this is a simliar concept
socket.subscribe("")

while True:
    # Receives a string format message
    print(socket.recv())
