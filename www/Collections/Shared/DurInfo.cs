using System.Collections.Generic;
using System.Linq;

namespace CC.Net.Collections.Shared

{
    public class DurInfo
    {
        public DurInfo(IEnumerable<ColTimersResult> timers)
        {
            var durations = timers.Select(i => i.Duration).ToArray();
            if(durations.Any())
            {
                N = durations.Length;
                Avg = durations.Average();
                Min = durations.Min();
                Max = durations.Max();
            }
        }

        public double Avg { get; set; } = 0.0;
        public double Min { get; set; } = 0.0;
        public double Max { get; set; } = 0.0;
        public int N { get; set; } = 0;
    }
}