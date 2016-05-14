import os
import sys
import argparse
import time
import logging

import pickle
import redis
from os import walk

class container:
    def __init__(self, cid=None):
        if cid is None:
            cid = ""
        self.cid   = cid
        self.memory = {}
        self.cpu    = {}
        self.blkio  = {}
    
    def addSubsystemItem(self, subsystem, name, metric):
        if(subsystem == 'memory'):
            self.memory[name] = metric
        if(subsystem == 'cpu'):
            self.cpu[name] = metric
        if(subsystem == 'blkio'):
            self.blkio[name] = metric


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

    CID = args.cid
    redis_addr = args.redis_remote
    r = redis.StrictRedis(host=redis_addr, port=6379, db=0)
    c = container(args.cid)
    subsystem_name = ['memory', 'blkio', 'cpu']
    cgroup_path = "/sys/fs/cgroup/%s/docker/"
    for subsystem in subsystem_name:
        path = os.path.join((cgroup_path % subsystem), CID)
        logging.debug("Checking container at path: %s:" % path)
        cgroup_files = []
        for (dirpath, dirnames, filenames) in walk(path):
            cgroup_files.extend(filenames)
            break
        for filename in cgroup_files:
            fname = os.path.join(path, filename)
            logging.debug("Opening cgroup file at path: <%s>" % fname)
            contents = ""
            with open(fname, "r") as f:
                print f
                contents = f.read()

            c.addSubsystemItem(subsystem, filename, contents)

    pickled_object = pickle.dumps(c)
    r.set(CID, pickled_object)
    logging.info("Container %s information pushed to redis" % CID)

    logging.debug("Stopping - %s: %s" % ("Finished collecting metrics", args.cid))


if __name__ == '__main__':
    sys.exit(main(sys.argv))
