using System.Collections.Generic;
using System.Linq;
using CC.Net.Collections;

namespace CC.Net.Utils
{

    public static class TimerExtensions
    {
        public static IEnumerable<ColTimers> Join(this IEnumerable<ColTimers> items, IList<ColRepoInfo> info)
        {
            foreach (var item in items)
            {
                item.Info = info.FirstOrDefault(i => i.Commit == item.Index.Commit);
                yield return item;
            }
        }

        public static void Join(this IEnumerable<ColRepoInfo> info, IEnumerable<ColTimers> items)
        {
        }
    }
}