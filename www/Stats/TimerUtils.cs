using System;
using System.Collections.Generic;
using System.Linq;
using CC.Net.Collections.Flex;
using CC.Net.Collections.Shared;
using CC.Net.Extensions;
using CC.Net.Services;

namespace CC.Net.Stats
{
    public static class DictionaryExtensions
    {
        public static GroupedTimer Get(this Dictionary<string, GroupedTimer> map, string key)
        {
            var hasKey = map.TryGetValue(key, out var result);
            return hasKey ? result : null;
        }
    }

    public class TimerUtils
    {
        public static void ComputeWelch(IList<GroupedTimer> items)
        {
            var minTimers = 4;
            var map = items.ToDictionary(i => i.Commit, j => j);
            var info = new List<int[]>();
            for (int i = 0; i < items.Count(); i++)
            {
                var timer = items[i];
                var parents = GetParents(timer, map, 10);
                var children = GetChildren(timer, map, 10);

                var b = parents.SelectMany(i => i.Durations).ToArray();
                var a = children.SelectMany(i => i.Durations).ToArray();

                var welch = (Welch)null;

                if (a.Length > minTimers && b.Length > minTimers)
                {
                    welch = Welch.TTest(a, b, 10);
                    timer.Welch = welch;
                    timer.Left = parents.Select(i => i.Commit).Reverse().ToList();
                    timer.Right = children.Select(i => i.Commit).ToList();
                }
                else
                {
                    continue;
                }

                // in case we detect some change, we'll try to "zoom in"
                if (welch.Significant)
                {
                    for (var j = 9; j > 1; j--)
                    {
                        var subParents = parents.Take(j);
                        var subChildren = children.Take(j);

                        b = subParents.SelectMany(i => i.Durations).ToArray();
                        a = subChildren.SelectMany(i => i.Durations).ToArray();

                        // until we still detect change
                        // and there is atleast 20 samples
                        if (a.Length > minTimers && b.Length > minTimers)
                        {
                            welch = Welch.TTest(a, b, j);
                            timer.Left = subParents.Select(i => i.Commit).Reverse().ToList();
                            timer.Right = subChildren.Select(i => i.Commit).ToList();
                            timer.Welch = welch;
                        }
                        else
                        {
                            break;
                        }
                    }
                }
            }
        }

        public static void SmoothDetections(List<GroupedTimer> items)
        {
            for (var i = 0; i < items.Count(); i++)
            {
                var timer = items[i];
                var map = items.ToDictionary(i => i.Commit, j => j);
                var test = timer.Welch;
                if (test?.Significant == true)
                {
                    var type = timer.WelchType;
                    var cmtLine = new List<GroupedTimer>()
                        .Concat(GetParents(timer, map, 10))
                        .Concat(GetChildren(timer, map, 10))
                        .ToList();

                    var testSeq = cmtLine.FindSequence(
                        i => i.WelchType == type,
                        cmtLine.FindIndex(i => i.Commit == timer.Commit)
                    );
                    if (testSeq.Count() > 1)
                    {
                        var (minIndex, diff) = testSeq.FindMaxDiff();
                        if (minIndex > 0)
                        {
                            foreach (var r in testSeq.Where((i, j) => j != minIndex))
                            {
                                if (r.WelchType != WelchType.Unknown)
                                {
                                    r.Welch.Significant = false;
                                }
                            }

                        }
                    }
                }
            }
        }

        public static List<GroupedTimer> GetParents(GroupedTimer timer, Dictionary<string, GroupedTimer> map, int count = 10)
        {
            if (timer == null)
            {
                return new List<GroupedTimer>();
            }

            var result = new List<GroupedTimer>();
            var parent = timer;
            foreach (var i in Enumerable.Range(0, count))
            {
                parent = parent.Info.Parents.Take(1).Select(i => map.Get(i)).FirstOrDefault();
                if (parent == null)
                {
                    break;
                }
                result.Add(parent);
            }
            return result;
        }

        public static List<GroupedTimer> GetChildren(GroupedTimer timer, Dictionary<string, GroupedTimer> map, int count = 10)
        {
            if (timer == null)
            {
                return new List<GroupedTimer>();
            }

            var result = new List<GroupedTimer>();
            var child = timer;
            result.Add(child);
            foreach (var i in Enumerable.Range(0, count - 1))
            {
                child = child.Info.Children.Take(1).Select(i => map.Get(i)).FirstOrDefault();
                if (child == null)
                {
                    break;
                }
                result.Add(child);
            }
            return result;
        }

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
                var welch = (Welch)null;
                if (a.Length > minTimers && b.Length > minTimers)
                {
                    welch = Welch.TTest(b, a, 10);
                    notBroken[i].Left = commitPrev.Select(i => i.Commit).Reverse().ToList();
                    notBroken[i].Right = commitNext.Select(i => i.Commit).ToList();
                    notBroken[i].Welch = welch;
                }
                else
                {
                    continue;
                }


                // in case we detect some change, we'll try to "zoom in"
                if (welch.Significant)
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
                if (test?.Significant == true)
                {
                    var type = cmt.WelchType;
                    var cmtLine = new List<SimpleTimers>();
                    cmtLine.AddRange(notBroken.Commits(repoInfo, i, -10));
                    cmtLine.AddRange(notBroken.Commits(repoInfo, i, +10));
                    var testSeq = cmtLine.FindSequence(
                        i => i.WelchType == type,
                        cmtLine.FindIndex(i => i.Commit == cmt.Commit)
                    );
                    if (testSeq.Count() > 1)
                    {
                        if (testSeq.Any(i => i.Commit == "41e620f7af62f7951d803305cdec15713b4ed2ea"))
                        {
                            Console.WriteLine("cas");
                        }
                        var (minIndex, diff) = testSeq.FindMaxDiff();
                        if (minIndex > 0)
                        {
                            foreach (var r in testSeq.Where((i, j) => j != minIndex))
                            {
                                if (r.WelchType != WelchType.Unknown)
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

    public interface IDurations
    {
        double[] Durations {get;set;}
    }

    public static class SimpleTimersExtensions
    {

        public static (int Index, double Diff) FindMaxDiff<T>(this List<T> items)
        where T: IDurations
        {
            var diff = double.MinValue;
            var minIndex = -1;
            for (int i = 0; i < items.Count() - 1; i++)
            {
                var a = items[i + 0];
                var b = items[i + 1];
                var newDiff = Math.Abs(b.Durations.Average() - a.Durations.Average());
                if (newDiff > diff)
                {
                    diff = newDiff;
                    minIndex = i + 1;
                }
            }
            return (minIndex, diff);
        }

        public static List<T> FindSequence<T>(this List<T> items, Func<T, bool> comparator, int index = 0)
        {
            var sequence = new List<T>();

            for (int i = index; i < items.Count(); i++)
            {
                var item = items[i];

                if (comparator(item))
                {
                    sequence.Add(item);
                }
                else
                {
                    break;
                }
            }

            for (int i = index - 1; i >= 0; i--)
            {
                var item = items[i];

                if (comparator(item))
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