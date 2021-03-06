using System;
using System.Collections.Generic;
using CC.Net.Collections;
using CC.Net.Db;
using MongoDB.Driver;

namespace CC.Net.Services
{
    public class RepoInfoCache
    {
        public IMongoCollection<ColRepoInfo> _repoInfo { get; }
        public  DateTime MinDateTime = DateTime.Now.AddMonths(-6);
        private Dictionary<string, ColRepoInfo> _cache = new Dictionary<string, ColRepoInfo>();

        public RepoInfoCache(DbService dbService)
        {
            _repoInfo = dbService.ColRepoInfo;
        }

        public IEnumerable<ColRepoInfo> GetAll()
        {
            return GetAll(MinDateTime);
        }
        public IEnumerable<ColRepoInfo> GetAll(int daysOld)
        {
            return GetAll(DateTime.Now.AddDays(-daysOld));
        }

        public List<ColRepoInfo> GetAll(DateTime minDateTime)
        {
            Console.WriteLine("");
            var items = _repoInfo
                .Find(i => i.CommittedDatetime > minDateTime)
                .SortBy(i => i.CommittedDatetime)
                .ToList();

            foreach (var item in items)
            {
                _cache[item.Commit] = item;
                // yield return item;
            }
            return items;
        }

        public ColRepoInfo this[string index]
        {
            get 
            {
                if(!_cache.ContainsKey(index))
                {
                    _cache[index] = _repoInfo
                        .Find(i => i.Commit == index)
                        .FirstOrDefault();
                }
                return _cache[index];
            }
        }

    }
}