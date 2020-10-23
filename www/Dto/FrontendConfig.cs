using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using YamlDotNet.Serialization;

namespace CC.Net.Dto
{
    public class FrontendConfig
    {
        [YamlMember(Alias = "baselines")]
        public List<Baseline> Baselines { get; set; }
    }

    public class Baseline
    {
        [YamlMember(Alias = "commit")]
        public string Commit { get; set; }

        [YamlMember(Alias = "title")]
        public string Title{ get; set; }
    }
}
