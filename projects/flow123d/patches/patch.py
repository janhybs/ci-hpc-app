from pathlib import Path

class Patch:
    def __init__(self, loc, old, new):
        self.loc = loc
        self.old = old
        self.new = new


patches = [
    Patch(
        'src/mesh/mesh.cc',
        'for ( elm : this->elements_range() ) {', 
        'for ( auto elm : this->elements_range() ) {'
    )
]



for patch in patches:
    f = Path(patch.loc)
    if f.exists():
        lines = []
        for i, l in enumerate(f.read_text().splitlines()):
            if l.find(patch.old) != -1:
                lines.append(patch.new)
            else:
                lines.append(l)
        f.write_text(
            '\n'.join(lines)
        )
        print(f'File {patch.loc}:{i+1:2d} patched')
