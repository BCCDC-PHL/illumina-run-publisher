import pathlib
from setuptools import setup

HERE = pathlib.Path(__file__).parent
INSTALL_REQUIRES = (HERE / "requirements.txt").read_text().splitlines()

config = {
    '__author__': None,
    '__email__': None,
    '__version__': None,
}

with open("illumina_run_publisher/publish_illumina_runs.py") as fp:
    for line in fp:
        if line.startswith("__"):
            key, value = line.strip().split("=")
            config[key.strip()] = value.strip().strip("\'")

setup(
    name='illumina-run-publisher',
    author=config['__author__'],
    version=config['__version__'],
    author_email=config['__email__'],
    scripts=['illumina_run_publisher/publish_illumina_runs.py'],
    url='https://github.com/BCCDC-PHL/illumina-run-pulisher',
    license='GPLv3',
    description='Watch directories for the creation of illumina sequencer outputs. When detected, publish messages with details of the run to a TCP socket.',
    install_requires=INSTALL_REQUIRES,
)
