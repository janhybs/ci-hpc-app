using System;
using System.Collections.Generic;
using System.Linq;
using System.Linq.Expressions;
using cc.net.Collections.Shared;
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

        public static double[] Durations(this List<SimpleTimers> lst, int i, int size)
        {
            return lst
                .Range(i, size)
                .SelectMany(i => i.Durations)
                .ToArray();
        }
    }

}
