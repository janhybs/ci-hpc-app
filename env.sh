#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# # module purge
# # module load metabase
# # module load gcc-6.4.0
# # module load mpich-3.0.2-gcc
# # module load cmake/3.15.3
# # module load /storage/liberec3-tul/home/jan-hybs/modules/python/3.7.4
# # module load /storage/praha1/home/jan-hybs/modules/ccache/3.4.2

# module load cmake-3.14.5
# module load mpich-3.0.2-gcc
# module list
# module purge
# module load metabase
# module load gcc-6.4.0
# module load mpich-3.0.2-gcc
# module load cmake/3.15.3
# module load /storage/liberec3-tul/home/jan-hybs/modules/python/3.7.4
# module load /storage/praha1/home/jan-hybs/modules/ccache/3.4.2

module purge
module load metabase
module load cmake-3.14.5
module load mpich-3.0.2-gcc
module load python/3.8.0-gcc
module list
set -x


export PYTHONPATH=$DIR/src
echo python3 src/cihpc/worker/schedule_worker.py -c projects/flow123d/config.yaml