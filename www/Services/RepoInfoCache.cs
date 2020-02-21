using System.Collections.Generic;
using CC.Net.Collections;
using CC.Net.Db;
using MongoDB.Driver;

namespace CC.Net.Services
{
    public class RepoInfoCache
    {
        public IMongoCollection<ColRepoInfo> _repoInfo { get; }
        private Dictionary<string, ColRepoInfo> _cache = new Dictionary<string, ColRepoInfo>();

        public RepoInfoCache(DbService dbService)
        {
            _repoInfo = dbService.ColRepoInfo;
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