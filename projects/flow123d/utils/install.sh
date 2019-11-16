set -e

cd flow123d
ls -la

make update-build-tree
cp config/config-jenkins-docker-debug.cmake config.cmake
make -j4
bin/flow123d --version

VERSION=$(bin/flow123d --version 2>&1)
echo "Flow123d installed version: $VERSION"
echo "Required version <git.commit_short>"

if [[ $VERSION == *"<git.commit_short>"* ]]; then
    exit 0
else
    exit 1
fi