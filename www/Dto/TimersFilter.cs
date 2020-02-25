using cc.net.Collections.Shared;

namespace CC.Net.Dto
{

    public class TimersFilter
    {
        public IndexInfo info{ get; set; }
        public int limit { get; set; } = 10;
    }
}