using CC.Net.Dto;
using CC.Net.Collections;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using CC.Net.Collections.Shared;

namespace CC.Net.Dto
{
    public class ConfigurationDto
    {
        public List<ColRepoInfo> Branches { get; set; }

        public IEnumerable<string> BranchNames => Branches
            .SelectMany(i => i.Branches)
            .OrderBy(i => i)
            .Distinct();

        public FrontendConfig FrontendConfig { get; set; }
        public List<IndexInfo> BenchmarkList { get; set; }
    }
}
