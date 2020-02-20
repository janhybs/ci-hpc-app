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
        [
            'for ( auto elm : this->elements_range() ) {'
        ]
    ),
    Patch(
        'src/fields/fe_value_handler.cc',
        'FEValues<elemdim,spacedim> fe_values(quad, *dh_->ds()->fe(elm).get<elemdim>(), update_values);',
        [
            '',
            'MixedPtr<FiniteElement> fe_mixed_ptr = dh_->ds()->fe(elm);',
            'std::shared_ptr<FiniteElement<elemdim>> fe_ptr = fe_mixed_ptr.get<elemdim>();',
            'FEValues<elemdim,spacedim> fe_values(quad, *fe_ptr, update_values);',
        ]
    ),
    Patch(
        'src/fields/fe_value_handler.cc',
        'FEValues<elemdim,3> fe_values(*this->get_mapping(), quad, *dh_->ds()->fe(elm).get<elemdim>(), update_values);',
        [
            '',
            'MixedPtr<FiniteElement> fe_mixed_ptr = dh_->ds()->fe(elm);',
            'std::shared_ptr<FiniteElement<elemdim>> fe_ptr = fe_mixed_ptr.get<elemdim>();',
            'FEValues<elemdim,3> fe_values(*this->get_mapping(), quad, *fe_ptr, update_values);',
        ]
    )
]



for patch in patches:
    f = Path(patch.loc)
    if f.exists():
        lines = []
        for i, l in enumerate(f.read_text().splitlines()):
            if l.find(patch.old) != -1:
                lines.extend(patch.new)
            else:
                lines.append(l)
        f.write_text(
            '\n'.join(lines)
        )
        print(f'File {patch.loc}:{i+1:2d} patched')
