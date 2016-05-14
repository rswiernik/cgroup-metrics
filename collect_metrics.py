import os
import sys
import argparse
import time
import logging

import pickle
import redis


class container:
    def __init__(self, cid=None):
        if cid is None:
            cid = ""
        self.cid   = cid
        self.memory = {}
        self.cpu    = {}
        self.blkio  = {}
    
    def addMemItem(self, cid, item):
        self.memory[cid] = item
    
    def addCpuItem(self, cid, item):
        self.cpu[cid] = item

    def addBlkioItem(self, cid, item):
        self.blkio[cid] = item


def main(args):
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-v', '--verbose', help='enable verbose output', action='store_true')
    parser.add_argument('-p', '--container', action='store', dest='cid', type=str, help='The docker container id listed in \'docker ps\'', required=True)
    parser.add_argument('-r', '--remote', action='store', dest='redis_remote', type=str, help='The remote redis target that we are sending things to')
    args = parser.parse_args()

    LOG_FORMAT = '%(asctime)-15s %(message)s'
    LOG_DATE = '%m/%d/%Y %H:%M:%S %Z  '
    LOG_LVL = logging.INFO
    if args.verbose:
        LOG_LVL = logging.DEBUG
    logging.basicConfig(format=LOG_FORMAT, datefmt=LOG_DATE, level=LOG_LVL)
    logging.debug('Verbose output enabled')


    logging.debug("Starting - %s: %s" % ("Docker container", args.cid))

    redis_addr = args.redis_remote
    memory_path = ("/sys/fs/cgroup/memory/docker/%s/", args.cid)

    r = redis.StrictRedis(host=redis_addr, port=6379, db=0)
    
    instance = container(args.cid)

    logging.debug("Stopping - %s: %s" % ("Finished collecting metrics", args.cid))


if __name__ == '__main__':
    sys.exit(main(sys.argv))
