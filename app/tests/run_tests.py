#!/usr/bin/env python

import sys
import nose
from os.path import abspath, dirname


def run_all(argv=None):
    # called by setuptools
    if argv is None:
        argv = ['nosetests']

    if len(argv) == 1:  # only the command itself is in argv
        argv += [
            #'--with-coverage', 
            '--cover-erase',
            '--with-xunit', '--nocapture', '--stop',
        ]

    nose.run_exit(argv=argv)


if __name__ == '__main__':
    run_all(sys.argv)
