using System.Collections.Generic;
using System.Linq;
using CC.Net.Collections;
using CC.Net.Collections.Shared;
using CC.Net.Db;
using CC.Net.Services;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using MongoDB.Driver;

namespace CC.Net.Controllers
{

    [ApiController]
    [Route("api/log")]
    public class LogController
    {


        private readonly ILogger<LogController> _logger;
        private readonly DbService _dbService;

        private readonly RepoInfoCache _repoInfo;

        private readonly GitInfoService _gitInfo;

        private readonly CachedCollection<ColIndexInfo> _indexInfo;

        public LogController(ILogger<LogController> logger, DbService dbService, RepoInfoCache repoInfo)
        {
            _logger = logger;
            _dbService = dbService;
            _repoInfo = repoInfo;
            _indexInfo = dbService.CachedColIndexInfo;
        }
        

        [HttpGet]
        [Route("list")]
        public List<CommitRun> LastBuilds()
        {
             var timers = _dbService.ColIndexInfo
                 .Find(i =>
                     i.Index.Project == "flow123d"
                 )
                 .ToEnumerable()
                 .ToList();
                 
            var commits = _repoInfo
                .GetAll(30 * 3)
                .GroupJoin(
                    timers,
                    i => i.Commit,
                    j => j.Index.Commit,
                    (i, j) => new CommitRun{
                        Commit = i,
                        Runs = j
                            .Select(k => new ColIndexInfoRun {
                                Duration = k.Run.Duration,
                                Returncode = k.Run.Returncode,
                                Job = k.Index.Job
                            })
                            .ToList()
                    })
                .ToList();
            
            // var timers = _dbService.ColIndexInfo
            //     .Find(i =>
            //         i.Index.Project == "flow123d"
            //         && (i.Index.Job == "test" || i.Index.Job == "compile")
            //     )
            //     .ToEnumerable()
            //     .GroupJoin(commits,
            //         i => i.Index.Commit,
            //         j => j.Commit,
            //         (i, j) => new {
            //             indexInfo = i,
            //             cmts = j.ToList()
            //         }
            //     )
            //     .ToList();

            return commits;
        }
    }
}