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
using CC.Net.Stats;
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

            var commits = _repoInfo.GetAll(365 * 1).ToList();
            var minId = filter.days.AsPastObjectId();
            var result = commits
                .Select(i =>
                    new SimpleTimers(i)
                    {
                        Commit = i.Commit,
                        Branch = i.Branch,
                        Info = GitInfo.From(i),
                        isBroken = true,
                        Durations = new double[] { 0, 0, 0 }
                    })
                .ToList();

            var dbItems = _dbService.ColTimers
                .Find(i =>
                    i.Index.Project == filter.info.Project
                    && i.Index.Test == filter.info.Test
                    && i.Index.Mesh == filter.info.Mesh
                    && i.Index.Benchmark == filter.info.Benchmark
                    && i.Index.Frame == "whole-program"
                    && i.Id > minId
                )
                .Sort(Builders<ColTimers>.Sort.Descending("_id"));

            var simple = dbItems
                .Project(i =>
                new
                {
                    i.Index.Commit,
                    i.Result.Duration
                })
                .ToList()
                .GroupBy(i => i.Commit, i => i.Duration);

            var cmts = simple.Select(i => i.Key).ToList();

            foreach(var s in simple)
            {
                var singleResult = result.FirstOrDefault(i => i.Commit == s.Key);
                if(singleResult != null)
                {
                    singleResult.isBroken = false;
                    singleResult.Durations = s.ToArray();
                }
            }

            var ratio = result.Count(i => !i.isBroken) / ((double)result.Count());

            result = result
                .OrderBy(i => i.Info.Date)
                .ToList();

            var firstValid = result.FindIndex(i => i.isBroken == false);
            if(firstValid != -1)
            {
                result = result
                    .Skip(firstValid)
                    .ToList();
            }
            var onlyMin = false;
            var minTimers = onlyMin ? 4 : 30;
            var notBroken = result.Where(i => !i.isBroken).ToList();
            for(var i = 10; i < notBroken.Count() - 10; i++)
            {
                if(notBroken[i].Commit == "1943bc6cf08ac7d04caebc93c15d402fd62ca74d")
                {
                    Console.WriteLine(notBroken[i]);
                }

                // we run ttest
                var commitPrev = notBroken.Commits(_repoInfo, i, -10);
                var commitNext = notBroken.Commits(_repoInfo, i, +10);
                var a = commitPrev.Durations(0, 10); //notBroken.Durations(i + 1, +10);
                var b = commitNext.Durations(0, 10); //notBroken.Durations(i + 0, -10);
                var r = (Welch)null;
                if (a.Length > minTimers && b.Length > minTimers)
                {
                    r = Welch.TTest(b, a, 10);
                    notBroken[i].Left = commitPrev.Select(i => i.Commit).Reverse().ToList();
                    notBroken[i].Right = commitNext.Select(i => i.Commit).ToList();
                    notBroken[i].Welch = r;
                }
                else
                {
                    continue;
                }
                

                // in case we detect some change, we'll try to "zoom in"
                if (r.Significant)
                {
                    for (var j = 9; j > 1; j--)
                    {
                        var aj = commitPrev.Durations(0, j); //notBroken.Durations(i + 0, +j);
                        var bj = commitNext.Durations(0, j); //notBroken.Durations(i - 1, -j);

                        // until we still detect change
                        // and there is atleast 20 samples
                        if (aj.Length > minTimers && bj.Length > minTimers)
                        {
                            var rj = Welch.TTest(bj, aj, j);
                            notBroken[i].Left = commitPrev.Take(j).Select(i => i.Commit).Reverse().ToList();
                            notBroken[i].Right = commitNext.Take(j).Select(i => i.Commit).ToList();
                            notBroken[i].Welch = rj;
                        }
                        else
                        {
                            break;
                        }
                    }
                }

            }

            return new {
                Data = result,
                Ratio = ratio
            };
        }
    }
}
