# Illumina Run Publisher

Watch a path for new illumina runs to arrive. When they arrive, parse the `SampleSheet.csv` file for the run and publish the details to a tcp port.

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
  "timestamp": "2020-10-01T17:23:52.561107",
  "event": "new_run",
  "path": "./test/sequencer-01/201001_M00325_0210_000000000-A5B31",
  "experiment_name": "Truly Insightful Experiment"
}
```