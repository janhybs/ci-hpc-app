# Configuration for CI server
# debug build

# main config
set(FLOW_BUILD_TYPE         release)
set(CMAKE_VERBOSE_MAKEFILE  YES)
set(USE_CCACHE              YES)
set(USE_PYTHON              YES)
set(PLATFORM_NAME           "linux_x86_64")

# set prefix based on a env variable FLOW123D_HOME
set(CMAKE_INSTALL_PREFIX    $ENV{FLOW123D_HOME})

# # external libraries
set(PACKAGE_DIR             /software/flow123d/packages)

set(PETSC_DIR               ${PACKAGE_DIR}/petsc-3.8.3/)
set(BDDCML_ROOT             ${PACKAGE_DIR}/bddcml-2.5.0/bddcml)
set(Armadillo_ROOT_HINT     ${PACKAGE_DIR}/armadillo-8.3.4)
set(YamlCpp_ROOT_HINT       ${PACKAGE_DIR}/yamlcpp-0.5.2)
set(PugiXml_ROOT_HINT       ${PACKAGE_DIR}/pugixml-1.9.0)

# 2.2.1
# external libraries
# set(PACKAGE_DIR             /software/flow123d/packages)
#
# set(PETSC_DIR               ${PACKAGE_DIR}/petsc-3.6.1/)
# set(BDDCML_ROOT             ${PACKAGE_DIR}/bddcml-2.4.0/bddcml)
# set(Armadillo_ROOT_HINT     ${PACKAGE_DIR}/armadillo-3.4.3)
# set(YamlCpp_ROOT_HINT       ${PACKAGE_DIR}/yamlcpp-0.5.2)
# set(PugiXml_ROOT_HINT       ${PACKAGE_DIR}/pugixml-1.9.0)

# klice820
