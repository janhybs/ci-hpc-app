module purge
module load metabase
module load gcc-6.4.0
module load mpich-3.0.2-gcc
module load python-3.6.2-gcc
module load python36-modules-gcc
module load /storage/praha1/home/jan-hybs/modules/cmake/3.12.0
module load /storage/praha1/home/jan-hybs/modules/ccache/3.4.2

module list

function exec_command() {
    echo $*
    echo "    $($* | head -n 1)" 
}

exec_command gcc --version
exec_command g++ --version
exec_command ccache --version
exec_command cmake --version
exec_command python --version

echo "Env: "
env