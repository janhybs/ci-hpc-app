using System;
using System.Collections.Generic;
using System.Diagnostics;

namespace CC.Net.Utils
{
    public class TickTockItem
    {
        public string Name { get; set; }
        public TimeSpan Time { get; set; }

        override public string ToString()
        {
            return $"{Name}: {Time}";
        }
    }

    public class TickTock
    {
        private Stopwatch Stopwatch;
        private string Name { get; set; }
        public List<TickTockItem> Items = new List<TickTockItem>();

        public TickTock()
        {
        }

        public void Stop()
        {
            if(Stopwatch != null)
            {
                Stopwatch.Stop();
                Items.Add( new TickTockItem{
                    Name = Name,
                    Time = Stopwatch.Elapsed
                });
                Stopwatch = null;
                Name = null;
            }
        }

        public void Start(string name)
        {
            Stop();
            Name = name;
            Stopwatch = Stopwatch.StartNew();
        }

        public static TickTock StartNew(string name)
        {
            var tt = new TickTock();
            tt.Start(name);
            return tt;
        }
    }
}