using System.Collections.Generic;
using System.Linq;
using System.Text.Json.Serialization;
using CC.Net.Services;
using NumSharp;

namespace cc.net.Collections.Shared
{
    public class SimpleTimers
    {
        public string Commit { get; set; }
        public string Branch { get; set; }

        public bool isBroken { get; set; } = false;

        public GitInfo Info { get; set; }

        [JsonIgnore]
        public double[] Durations { get; set; }

        public int Count => Durations.Length;

        public double Median
        {
            get
            {
                return Durations
                    [Durations.Count() / 2];
            }
        }

        public double Q1
        {
            get
            {
                var l = Durations.Count();
                return Durations
                    [(int)(l * 0.25)];
            }
        }

        public double Q3
        {
            get
            {
                var l = Durations.Count();
                return Durations
                    [(int)(l * 0.75)];
            }
        }

        public double Low => Durations.Min();

        public double High => Durations.Max();
    }
}