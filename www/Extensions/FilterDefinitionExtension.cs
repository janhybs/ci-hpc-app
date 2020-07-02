using System;
using System.Collections.Generic;
using System.Linq;
using System.Linq.Expressions;
using CC.Net.Collections.Shared;
using CC.Net.Collections;
using CC.Net.Services;
using MongoDB.Bson;
using MongoDB.Driver;

namespace CC.Net.Extensions
{
    public static class FilterDefinitionExtensions
    {
        public static FilterDefinition<TDocument> Match<TDocument>(this FilterDefinitionBuilder<TDocument> filter,
            string field, string value)
        {
            return filter.Regex(field, new BsonRegularExpression(value, "i"));
        }
    }

    public static class IntExtensions
    {
        public static ObjectId AsPastObjectId(this int days)
        {
            return new ObjectId(DateTime.Today.AddDays(-Math.Abs(days)), 0, 0, 0);
        }
    }

    public static class ListExtensions
    {
        public static IEnumerable<T> Range<T>(this List<T> lst, int i, int size)
        {
            if(size > 0)
            {
                var t = lst.Count;
                var s = Math.Max(Math.Min(i, t - 1), 0);
                var c = Math.Max(Math.Min(s + size, t), 0);
                return lst.GetRange(s, c - s);
            }
            if (size < 0)
            {
                size = -size;
                var t = lst.Count;

                var s = Math.Max(Math.Min(i - size + 1, t - 1), 0);
                var c = Math.Max(Math.Min(i + 1, t), 0);
                return lst.GetRange(s, c - s);
            }
            return new List<T>();
        }

        public static double[] Durations(this List<SimpleTimers> lst, int i, int size, bool onlyMin=false)
        {
            if(onlyMin)
            {
                return lst
                    .Range(i, size)
                    .Select(i => i.Durations.Min())
                    .ToArray();
            }

            return lst
                .Range(i, size)
                .SelectMany(i => i.Durations)
                .ToArray();
        }
        public static List<SimpleTimers> Commits(this List<SimpleTimers> lst, RepoInfoCache repoInfo, int index, int size)
        {
            var result = new List<SimpleTimers>();
            var start = lst.SafeGet(index);
            var cut = 0;
            if (start == null || size == 0)
            {
                return result;
            }

            var getter = (Func<ColRepoInfo, List<string>>) null;
            if (size > 0)
            {
                getter = i => i.Children;
            }
            if (size < 0)
            {
                getter = i => i.Parents;
                size = Math.Abs(size) + 1;
                cut = 1;
            }

            result.Add(start);
            var currentCommit = start.Commit;
            var opMax = 5 * size;
            var op = 0;

            while(result.Count() < size)
            {
                if(++op > opMax)
                {
                    break;
                }

                var timerInfo = repoInfo[currentCommit];
                var nextCommit = getter(timerInfo).FirstOrDefault();
                if (string.IsNullOrEmpty(nextCommit))
                {
                    // we've reached start or end of the branch
                    break;
                }
                var currentTimer = lst.FirstOrDefault(i => i.Commit == nextCommit);
                if(currentTimer == null)
                {
                    // we skip this and search more
                    currentCommit = nextCommit;
                    continue;
                }
                currentCommit = currentTimer.Commit;
                result.Add(currentTimer);
            }
            return result.Skip(cut).ToList();
        }

        public static T SafeGet<T>(this IList<T> lst, int index)
            where T: class
        {
            return (index < 0 || index >= lst.Count()) ? null : lst[index];
        }
    }

}
