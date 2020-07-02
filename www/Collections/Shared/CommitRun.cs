using System.Collections.Generic;

namespace CC.Net.Collections.Shared

{
    public class CommitRun
    {
        public ColRepoInfo Commit { get; set; }
        public List<ColIndexInfoRun> Runs { get; set; }
    }
}