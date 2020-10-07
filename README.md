![Build Status](https://github.com/BCCDC-PHL/illumina-run-publisher/workflows/Test/badge.svg)

# Illumina Run Publisher

Watch a path for new illumina runs to arrive. When they arrive, parse the `SampleSheet.csv` file for the run and publish the details to a tcp port.

## Usage

### Creating Key Pairs

This service uses ZeroMQ CURVE authentication, which requires a public/private key pair.

One can use [generate_certificates.py](https://github.com/zeromq/pyzmq/blob/master/examples/security/generate_certificates.py) from the [pyzmq examples security repository](https://github.com/zeromq/pyzmq/tree/master/examples/security) to create these keys.

### Publisher

```
usage: publish_illumina_runs.py [-h] [--port PORT] [--path PATH]
                                [--heartbeat_interval HEARTBEAT_INTERVAL] --public_key PUBLIC_KEY
                                --private_key PRIVATE_KEY

optional arguments:
  -h, --help            show this help message and exit
  --port PORT
  --path PATH
  --heartbeat_interval HEARTBEAT_INTERVAL
  --public_key PUBLIC_KEY
  --private_key PRIVATE_KEY
```

Note: multiple paths can be watched simultaneously. eg:

```
publish_illumina_runs.py --path /path/to/sequencer-01 --path /path/to/sequencer-02
```

### Subscriber

A simple demo subscriber script is included. It simply prints messages from the `illumina_runs` topic to stdout.

```
usage: demo_subscriber.py [-h] [--port PORT] --public_key PUBLIC_KEY --private_key PRIVATE_KEY

optional arguments:
  -h, --help            show this help message and exit
  --port PORT
  --public_key PUBLIC_KEY
  --private_key PRIVATE_KEY
```

## Messages

Messages are published to the `illumina_runs` topic. There are currently two message types

```json
{
  "timestamp": "2020-10-01T17:23:56.597547",
  "event": "heartbeat"
}
```

```json
{
  "timestamp": "2020-10-05T15:42:09.605165",
  "event": "run_directory_created",
  "path": "/path/to/201001_M00325_0210_000000000-A5B31",
  "experiment_name": "Truly Insightful Experiment",
  "run_date": "2020-10-01",
  "instrument_type": "MiSeq",
  "instrument_id": "M00325",
  "flowcell_id": "000000000-A5B31",
  "investigator_name": "Dr. Sequencer",
}
```