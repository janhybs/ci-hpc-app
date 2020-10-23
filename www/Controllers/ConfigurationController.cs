using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using CC.Net.Collections;
using CC.Net.Config;
using CC.Net.Db;
using CC.Net.Dto;
using CC.Net.Services;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using MongoDB.Bson;
using MongoDB.Driver;

// For more information on enabling MVC for empty projects, visit https://go.microsoft.com/fwlink/?LinkID=397860

namespace cc.net.Controllers
{

    [ApiController]
    [Route("api/configuration")]
    public class ConfigurationController : Controller
    {
        private RepoInfoCache _repoInfo;
        private DbService _dbService;
        private CachedCollection<ColIndexInfo> _indexInfo;
        private GitInfoService _gitInfo;
        private ILogger<ConfigurationController> _logger;
        private MongoDBConfig _dBConfig;

        public ConfigurationController(ILogger<ConfigurationController> logger, RepoInfoCache repoInfo, DbService dbService, GitInfoService gitInfo, MongoDBConfig dBConfig)
        {
            _repoInfo = repoInfo;
            _dbService = dbService;
            _indexInfo = dbService.CachedColIndexInfo;
            _gitInfo = gitInfo;
            _logger = logger;
            _dBConfig = dBConfig;
        }

        [HttpGet]
        [Route("full")]
        public async Task<ConfigurationDto> FullConfiguration()
        {
            _gitInfo.SetupProjects();
            var commitsCursor = await _dbService.ColTimers.DistinctAsync<string>("index.commit", "{}");
            var commits = await commitsCursor.ToListAsync();
            var branches = await _dbService.ColRepoInfo
                .Find(i => commits.Contains(i.Commit))
                .ToListAsync();

            return new ConfigurationDto
            {
                FrontendConfig = _gitInfo.FrontendConfig,
                BenchmarkList = _gitInfo.BenchmarkList,
                Branches = branches
                    .OrderByDescending(i => i.AuthoredDatetime)
                    .ToList(),
            };
        }
    }
}
