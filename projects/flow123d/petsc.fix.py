from pathlib import Path

cmakelists = Path('CMakeLists.txt')
lines = []

for line in cmakelists.read_text().splitlines():
    # print(line == "find_package(PETSc 3.6.0 REQUIRED)", line)

    if line == "find_package(PETSc 3.6.0 REQUIRED)":
        lines.append(line)
        lines.append("include_directories(/software/mpich-3.0.2/gcc/include/)")
        continue

    if line == "include_directories(/software/mpich-3.0.2/gcc/include/)":
        continue

    lines.append(line)

cmakelists.write_text('\n'.join(lines))
# print('\n'.join(lines))
