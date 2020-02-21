using CC.Net.Collections;
using CC.Net.Config;
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
        }
    }
}