using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using cc.net.Collections.Shared;
using CC.Net.Collections;
using CC.Net.Db;
using CC.Net.Dto;
using CC.Net.Extensions;
using CC.Net.Services;
using CC.Net.Utils;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using MongoDB.Bson;
using MongoDB.Driver;
using Newtonsoft.Json;

namespace CC.Net.Controllers
{
    [ApiController]
    [Route("api/timers")]
    public class TimersController : ControllerBase
    {

        private readonly ILogger<TimersController> _logger;
        private readonly DbService _dbService;

        private readonly RepoInfoCache _repoInfo;

        private readonly GitInfoService _gitInfo;

        private readonly CachedCollection<ColIndexInfo> _indexInfo;

        public TimersController(ILogger<TimersController> logger, DbService dbService, RepoInfoCache repoInfo)
        {
            _logger = logger;
            _dbService = dbService;
            _repoInfo = repoInfo;
            _indexInfo = dbService.CachedColIndexInfo;
        }

        [HttpPost]
        [Route("list")]
        public object ActionList(TimersFilter filter)
        {
            // var cmd = @"
            //     {'pipeline': [
            //         {
            //             '$match': {
            //                 'index.project': '<project>',
            //                 'index.test': '<test>',
            //                 'index.mesh': '<mesh>',
            //                 'index.benchmark': '<benchmark>',
            //                 'index.cpus': <cpus>,
            //                 'index.frame': 'whole-program'
            //             }
            //         }
            //     ]}";
            var items = _dbService.ColTimers
                .Find(i =>
                    i.Index.Project == filter.info.Project
                    && i.Index.Test == filter.info.Test
                    && i.Index.Mesh == filter.info.Mesh
                    && i.Index.Benchmark == filter.info.Benchmark
                    && i.Index.Cpus == filter.info.Cpus
                    && i.Index.Frame == "whole-program"
                )
                .Sort(Builders<ColTimers>.Sort.Descending("_id"))
                .Limit(filter.limit)
                .SortBy(i => i.Id)
                .Project(i => new SimpleTimer
                {
                    objectId = i.objectId,
                    Commit = i.Index.Commit,
                    Branch = i.Index.Branch,
                    Duration = i.Result.Duration,
                })
                .ToList()
                .GroupBy(
                    i => i.Commit,
                    (k, i) => new SimpleTimers
                    {
                        Commit = k,
                        Info = GitInfo.From(_repoInfo[k]),
                        Branch = i.First().Branch,
                        Durations = i.Select(j => j.Duration)
                            .OrderBy(i => i)
                            .ToArray()
                    }
                )
                .ToList();
                // .Prepend(new SimpleTimers()
                // {
                //     Commit = "aaa",
                //     Branch = "none",
                //     Info = GitInfo.Empty(),
                //     Durations = new double[] { 0, 0, 0 }
                // });

            var cmts = _repoInfo
                .GetAll(90)
                .Where(i => _indexInfo
                    .GetDocument(i.Commit, () => FindByCommit(i.Commit))
                    ?.Run?.IsBroken == true)
                .ToList();
            
            items.AddRange(
                cmts.Select(i => 
                    new SimpleTimers(){
                        Commit = i.Commit,
                        Branch = i.Branch,
                        Info = GitInfo.From(i),
                        isBroken = true,
                        Durations = new double[] { 0, 0, 0 }
                    })
            );


            return items;
        }

        private ColIndexInfo FindByCommit(string commit)
        {
            return _indexInfo.Collection
                .Find(i => i.Index.Commit == commit && i.Index.Job == "compile")
                .FirstOrDefault();
        }
    }
}
