using System;
using System.Collections.Generic;
using CC.Net.Db;
using MongoDB.Driver;

namespace CC.Net.Services
{
    public class CachedCollection<T>
        where T : ICollection
    {
        public readonly IMongoCollection<T> Collection;

        protected readonly Dictionary<string, T> _cache;

        public CachedCollection(IMongoCollection<T> collection)
        {
            Collection = collection;
            _cache = new Dictionary<string, T>();
        }

        public T GetDocument(string index, Func<T> getter) {
            if (!_cache.ContainsKey(index))
            {
                _cache[index] = getter();
            }
            return _cache[index];
        }
    }
}