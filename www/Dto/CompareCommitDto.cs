using System.Collections.Generic;
using CC.Net.Collections.Shared;

namespace CC.Net.Dto
{

    public class CompareCommitDto
    {
        public DurInfoWrapper RootA { get; set; }
        public DurInfoWrapper RootB { get; set; }
        public List<DurInfoWrapper> CommitA { get; set; }
        public List<DurInfoWrapper> CommitB { get; set; }
    }
}