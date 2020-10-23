using CC.Net.Collections.Shared;
using System.Collections.Generic;

namespace CC.Net.Dto
{

    public class CompareCommitFilter
    {
        public string CommitA { get; set; }
        public string CommitB { get; set; }
        public List<string> Commits { get; set; }
        public string Frame { get; set; }
        public IndexInfo Info { get; set; } 
    }
}