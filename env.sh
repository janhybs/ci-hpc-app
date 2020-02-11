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

RCol='\e[0m'    # Text Reset
# Regular       Bold             High Intensity   BoldHigh Intens   Background       High Intensity Backgrounds
Bla='\e[0;30m'; BBla='\e[1;30m'; IBla='\e[0;90m'; BIBla='\e[1;90m'; On_Bla='\e[40m'; On_IBla='\e[0;100m';
Red='\e[0;31m'; BRed='\e[1;31m'; IRed='\e[0;91m'; BIRed='\e[1;91m'; On_Red='\e[41m'; On_IRed='\e[0;101m';
Gre='\e[0;32m'; BGre='\e[1;32m'; IGre='\e[0;92m'; BIGre='\e[1;92m'; On_Gre='\e[42m'; On_IGre='\e[0;102m';
Yel='\e[0;33m'; BYel='\e[1;33m'; IYel='\e[0;93m'; BIYel='\e[1;93m'; On_Yel='\e[43m'; On_IYel='\e[0;103m';
Blu='\e[0;34m'; BBlu='\e[1;34m'; IBlu='\e[0;94m'; BIBlu='\e[1;94m'; On_Blu='\e[44m'; On_IBlu='\e[0;104m';
Pur='\e[0;35m'; BPur='\e[1;35m'; IPur='\e[0;95m'; BIPur='\e[1;95m'; On_Pur='\e[45m'; On_IPur='\e[0;105m';
Cya='\e[0;36m'; BCya='\e[1;36m'; ICya='\e[0;96m'; BICya='\e[1;96m'; On_Cya='\e[46m'; On_ICya='\e[0;106m';
Whi='\e[0;37m'; BWhi='\e[1;37m'; IWhi='\e[0;97m'; BIWhi='\e[1;97m'; On_Whi='\e[47m'; On_IWhi='\e[0;107m';

function exec_command() {
    echo -e "$BIRed$*$RCol"
    echo -e "$BIGre    $($* | head -n 1)$RCol" 
}

module purge
module load metabase
# module load gcc-5.3.0
module load gcc-6.4.0
# module load cmake-3.14.5
module load cmake/3.15.3
module load mpich-3.0.2-gcc
module load python/3.8.0-gcc
module load flow123d/packages/ccache-3.7.7
module list

exec_command gcc --version
exec_command g++ --version
exec_command ccache --version
exec_command cmake --version
exec_command python --version

# set -x




export PYTHONPATH=$DIR/src
echo python3 src/cihpc/worker/schedule_worker.py -c projects/flow123d/config.yaml
