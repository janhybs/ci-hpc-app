using System;
using System.Collections.Generic;
using System.Linq;
using cc.net.Collections.Shared;
using CC.Net.Extensions;
using CC.Net.Services;

namespace CC.Net.Stats
{
    public class TimerUtils
    {
        public static void ComputeWelch(IList<SimpleTimers> result, RepoInfoCache repoInfo)
        {
            var onlyMin = false;
            var minTimers = onlyMin ? 4 : 30;
            var notBroken = result.Where(i => !i.isBroken).ToList();
            for (var i = 10; i < notBroken.Count() - 10; i++)
            {
                // we run ttest
                var commitPrev = notBroken.Commits(repoInfo, i, -10);
                var commitNext = notBroken.Commits(repoInfo, i, +10);
                var a = commitPrev.Durations(0, 10); //notBroken.Durations(i + 1, +10);
                var b = commitNext.Durations(0, 10); //notBroken.Durations(i + 0, -10);
                var r = (Welch)null;
                if (a.Length > minTimers && b.Length > minTimers)
                {
                    r = Welch.TTest(b, a, 10);
                    notBroken[i].Left = commitPrev.Select(i => i.Commit).Reverse().ToList();
                    notBroken[i].Right = commitNext.Select(i => i.Commit).ToList();
                    notBroken[i].Welch = r;
                }
                else
                {
                    continue;
                }


                // in case we detect some change, we'll try to "zoom in"
                if (r.Significant)
                {
                    for (var j = 9; j > 1; j--)
                    {
                        var aj = commitPrev.Durations(0, j); //notBroken.Durations(i + 0, +j);
                        var bj = commitNext.Durations(0, j); //notBroken.Durations(i - 1, -j);

                        // until we still detect change
                        // and there is atleast 20 samples
                        if (aj.Length > minTimers && bj.Length > minTimers)
                        {
                            var rj = Welch.TTest(bj, aj, j);
                            notBroken[i].Left = commitPrev.Take(j).Select(i => i.Commit).Reverse().ToList();
                            notBroken[i].Right = commitNext.Take(j).Select(i => i.Commit).ToList();
                            notBroken[i].Welch = rj;
                        }
                        else
                        {
                            break;
                        }
                    }
                }

            }
        }
    }
}