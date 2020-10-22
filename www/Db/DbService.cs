using CC.Net.Collections;
using CC.Net.Config;
using CC.Net.Services;
using MongoDB.Bson;
using MongoDB.Driver;
using System;

namespace CC.Net.Db
{
    public class DbService
    {
        private readonly MongoDBConfig _dBConfig;
        private readonly MongoClient _client;
        private readonly IMongoDatabase _dB;
        public readonly IMongoCollection<ColScheduler> ColScheduler;
        public readonly IMongoCollection<ColTimers> ColTimers;
        public readonly IMongoCollection<ColRepoInfo> ColRepoInfo;
        public readonly IMongoCollection<ColIndexInfo> ColIndexInfo;

        public readonly CachedCollection<ColIndexInfo> CachedColIndexInfo;

        public DbService(MongoDBConfig dBConfig)
        {
            _dBConfig = dBConfig;
            _client = new MongoClient(new MongoClientSettings()
            {
                Server = MongoServerAddress.Parse(_dBConfig.Host),
                Credential = MongoCredential.CreateCredential(
                    _dBConfig.AuthSource,
                    _dBConfig.Username,
                    _dBConfig.Password
                )
            });
            
            _dB = _client.GetDatabase(_dBConfig.Database);
            
            ColScheduler = _dB.GetCollection<ColScheduler>(_dBConfig.CollectionScheduler);
            ColTimers = _dB.GetCollection<ColTimers>(_dBConfig.CollectionTimers);
            ColRepoInfo = _dB.GetCollection<ColRepoInfo>(_dBConfig.CollectionRepoInfo);
            ColIndexInfo = _dB.GetCollection<ColIndexInfo>(_dBConfig.CollectionIndexInfo);

            CachedColIndexInfo = new CachedCollection<ColIndexInfo>(ColIndexInfo);
        }

        public IMongoCollection<BsonDocument> GetGenericCollection(string name)
        {
            return _dB.GetCollection<BsonDocument>(name);
        }
    }
}