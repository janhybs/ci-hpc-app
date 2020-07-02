using System;
using System.Collections.Generic;
using System.Linq;
using CC.Net.Collections.Shared;
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

            for (var i = 10; i < notBroken.Count() - 10; i++)
            {
                var cmt = notBroken[i];
                var test = cmt.Welch;
                if(test?.Significant == true)
                {
                    var type = cmt.WelchType;
                    var cmtLine = new List<SimpleTimers>();
                    cmtLine.AddRange(notBroken.Commits(repoInfo, i, -10));
                    cmtLine.AddRange(notBroken.Commits(repoInfo, i, +10));
                    var testSeq = cmtLine.FindSequence(
                        i => i.WelchType == type,
                        cmtLine.FindIndex(i => i.Commit == cmt.Commit)
                    );
                    if(testSeq.Count() > 1)
                    {
                        if(testSeq.Any(i => i.Commit == "41e620f7af62f7951d803305cdec15713b4ed2ea"))
                        {
                            Console.WriteLine("cas");
                        }
                        var (minIndex, diff) = testSeq.FindMaxDiff();
                        if(minIndex > 0)
                        {
                            foreach(var r in testSeq.Where((i, j) => j != minIndex))
                            {
                                if(r.WelchType != WelchType.Unknown)
                                {
                                    // r.Welch.Significant = false;
                                }
                            }
                            
                        }
                    }
                }
            }
        }
    }

    public static class SimpleTimersExtensions
    {

        public static (int Index, double Diff) FindMaxDiff(this List<SimpleTimers> items) 
        {
            var diff = double.MinValue;
            var minIndex = -1;
            for (int i = 0; i < items.Count()-1; i++)
            {
                var a = items[i+0];
                var b = items[i+1];
                var newDiff = Math.Abs(b.Durations.Average() - a.Durations.Average());
                if(newDiff > diff)
                {
                    diff = newDiff;
                    minIndex = i+1;
                }
            }
            return (minIndex, diff);
        }

        public static List<SimpleTimers> FindSequence(this List<SimpleTimers> items, Func<SimpleTimers, bool> comparator, int index = 0) 
        {
            var sequence = new List<SimpleTimers>();

            for (int i = index; i < items.Count(); i++)
            {
                var item = items[i];

                if(comparator(item))
                {
                    sequence.Add(item);
                }
                else
                {
                    break;
                }
            }

            for (int i = index - 1; i >= 0 ; i--)
            {
                var item = items[i];

                if(comparator(item))
                {
                    sequence.Insert(0, item);
                }
                else
                {
                    break;
                }
            }

            return sequence;
        }
    }
}