#!/usr/bin/python3
import unshare
import argparse
import os
from os import path
import sys
from cgroups import Cgroup

ctrlgrp = Cgroup('root')

def uts_namespace(args):
    unshare.unshare(unshare.CLONE_NEWUTS)
    os.system("hostname -b "+args.hostname)

def net_namespace(args):
    unshare.unshare(unshare.CLONE_NEWNET)
    os.system("modprobe dummy")
    os.system("ip link add veth1 type dummy")
    os.system(f'ip addr add {args.ip_addr} dev veth1')
    os.system("ip link set veth1 up")

def mnt_namespace(args):
    unshare.unshare(unshare.CLONE_NEWNS)

def pid_namespace(args):
    unshare.unshare(unshare.CLONE_NEWPID)

def cpu_cgroup(args):
    os.system("echo $$")

def mem_cgroup(args):
    ctrlgrp.set_memory_limit(args.mem_size)

def exe_bash(args):
    new_pid = os.fork()
    if new_pid == 0:
        ctrlgrp.add(os.getpid())
        os.system("echo $$ > /tasks")
        os.chdir(args.root_path)
        os.chroot('.')
        os.system(f'hostname {args.hostname}')
        os.system('mount -t proc proc /proc')
        os.execle('/bin/bash', '/bin/bash', os.environ)
        print("Exiting Bash exe")
    else:
        os.wait()
        os.system(f'umount {args.root_path}/proc')

if __name__ == "__main__":
    print ("*************************")
    print ("*                       *")
    print ("*      Mini Docker      *")
    print ("*                       *")
    print ("*************************")

    parser = argparse.ArgumentParser(description='This is a miniDocker.')

    parser.add_argument('--hostname', action="store", dest="hostname", type=str, default="administrator",
                    help='set the container\'s hostname')
    parser.add_argument('--ip_addr', action="store", dest="ip_addr", type=str, default="10.0.0.1",
                    help='set the container\'s ip address')
    parser.add_argument('--mem', action="store", dest="mem_size", type=int, default=10,
                    help='set the container\'s memory size (MB)')
    parser.add_argument('--cpu', action="store", dest="cpu_num", type=int, default=1,
                    help='set the container\'s cpu number')
    parser.add_argument('--root_path', action="store", dest="root_path", type=str, default="./new_root",
                    help='set the new root file system path of the container')
    args = parser.parse_args()


    #create hostname namespace
    uts_namespace(args)
    #create network namespace
    net_namespace(args)
    #create filesystem namespace
    mnt_namespace(args)
    #create cpu cgroup
    cpu_cgroup(args)
    #create memory cgroup
    mem_cgroup(args)
    #create pid namespace
    pid_namespace(args)
    #execute the bash process "/bin/bash"
    exe_bash(args)
