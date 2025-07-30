__version__ = '0.0.1'

import sys

import rwx.log

log = rwx.log.get_logger(__name__)


class Build:

    def __init__(self):
        self.input_mirror = None
        self.output_root = None

    def check(self):
        log.info('Build.check')

    def init(self):
        log.info('Build.init')

    def build(self):
        log.info('Build.build')

    def squash(self):
        log.info('Build.squash')

    def run(self):
        self.check()
        self.init()
        self.build()
        self.squash()


def main():
    print(sys.argv)
