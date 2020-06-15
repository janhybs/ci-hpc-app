set -e

cd flow123d
ls -la

git checkout -- src/mesh/mesh.cc || true
git checkout -- src/fields/fe_value_handler.cc || true
python3 /storage/liberec3-tul/home/jan-hybs/ci-hpc/projects/flow123d/patches/patch.py || true


cat <<EOF > config.cmake
# main config
set(FLOW_BUILD_TYPE         release)
set(CMAKE_VERBOSE_MAKEFILE  YES)
set(USE_CCACHE              YES)
set(USE_PYTHON              YES)
set(PLATFORM_NAME           "linux_x86_64")

set(PACKAGE_DIR             /software/flow123d/packages)

set(PETSC_DIR               \${PACKAGE_DIR}/petsc-3.8.3/)
set(BDDCML_ROOT             \${PACKAGE_DIR}/bddcml-2.5.0/bddcml)
set(Armadillo_ROOT_HINT     \${PACKAGE_DIR}/armadillo-8.3.4)
set(YamlCpp_ROOT_HINT       \${PACKAGE_DIR}/yamlcpp-0.5.2)
set(PugiXml_ROOT_HINT       \${PACKAGE_DIR}/pugixml-1.9.0)
EOF

make update-build-tree
make -j12

bin/flow123d --version

VERSION=$(bin/flow123d --version 2>&1)
echo "Flow123d installed version: $VERSION"
echo "Required version <git.commit_short>"

if [[ $VERSION == *"<git.commit_short>"* ]]; then
    exit 0
else
    exit 1
fi
