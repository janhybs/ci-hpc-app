using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using YamlDotNet.Serialization;

namespace CC.Net.Dto
{

    public class BenchmarksConfig : List<BenchmarkConfig>
    {
    }

    public class BenchmarkConfig
    {
        [YamlMember(Alias = "matrix")]
        public List<BenchmarksConfigMatrix> Matrix { get; set; }
    }

    public class BenchmarksConfigMatrix: Dictionary<string, List<string>>
    {
        public string Name => Keys.First();
        public List<string> Items => Values.First();
    }
}
