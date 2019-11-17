cd bench-stat
echo "Running test <test['name']> (id=<test['id']>)"

mkdir -p <tmpdir>/
benchmarks/O3.out <tmpdir>/result-<uuid>-<test['id']>.json <test['id']>