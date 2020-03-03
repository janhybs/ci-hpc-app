make -C flow123d update-build-tree

# execute flow in serial for specific yaml file and mesh size
# results will be stored in a temp folder with unique ID, so they can be link
extraPath=<workdir()>/flow123d/src/python

export PYTHONPATH=$PYTHONPATH:$extraPath
flow123d/bin/flow123d \
    -i <mesh> \
    -o <workdir()>/.cihpc/.tmp/<uuid> \
    bench_data/benchmarks/<test>/<benchmark>

ls -la <workdir()>/.cihpc/.tmp/<uuid>/