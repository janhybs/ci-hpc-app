#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

module purge
module load metabase
module load gcc-6.4.0
module load mpich-3.0.2-gcc
module load cmake/3.15.3
module load /storage/liberec3-tul/home/jan-hybs/modules/python/3.7.4
module load /storage/praha1/home/jan-hybs/modules/ccache/3.4.2

export PYTHONPATH=$DIR/src
echo python3 src/cihpc/worker/schedule_worker.py -c projects/flow123d/config.yaml