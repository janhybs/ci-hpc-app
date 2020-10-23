using System.Collections.Generic;
using System.Linq;

namespace CC.Net.Collections.Shared

{
    public class DurInfoWrapper
    {
        public string Commit { get; set; }
        public string Path { get; set; }
        public string Frame => Path.Split('/').LastOrDefault();
        public DurInfo Duration { get; set; }
    }
}