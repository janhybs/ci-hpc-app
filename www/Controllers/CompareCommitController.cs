using System.Collections.Generic;
using System.Linq;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using CC.Net.Collections;
using CC.Net.Collections.Shared;
using CC.Net.Db;
using CC.Net.Dto;
using CC.Net.Services;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using MongoDB.Bson;
using MongoDB.Driver;

namespace CC.Net.Controllers
{

    [ApiController]
    [Route("api/compare-commit")]
    public class CompareCommitController : ControllerBase
    {

        private readonly ILogger<TimersController> _logger;
        private readonly DbService _dbService;

        private readonly RepoInfoCache _repoInfo;

        private readonly GitInfoService _gitInfo;

        private readonly CachedCollection<ColIndexInfo> _indexInfo;

        public CompareCommitController(ILogger<TimersController> logger, DbService dbService, RepoInfoCache repoInfo)
        {
            _logger = logger;
            _dbService = dbService;
            _repoInfo = repoInfo;
        }


        [HttpPost("compare-ab")]
        public async Task<object> Courses(CompareCommitFilter filter)
        {
            var cmts = new List<string>{filter.CommitA, filter.CommitB};
            var ro = RegexOptions.Compiled | RegexOptions.IgnoreCase;
            var regex = new Regex($"^{filter.Frame}/[a-zA-Z0-9-]+$", ro);
            // var regex2 = new Regex($"^{filter.Frame}/[a-zA-Z0-9-]+/[a-zA-Z0-9-]+$", ro);
            var allResults = await _dbService.ColTimers.Find(
                    i => cmts.Contains(i.Index.Commit)
                    && i.Index.Project == filter.Info.Project
                    && i.Index.Mesh == filter.Info.Mesh
                    && i.Index.Test == filter.Info.Test
                    && (i.Result.Path == filter.Frame || regex.IsMatch(i.Result.Path))
                )
                .ToListAsync();
            
            var aResults = allResults
                .Where(i => i.Index.Commit == filter.CommitA)
                .GroupBy(i => i.Result.Path, i => i.Result)
                .Where(i => i.Count() > 0)
                .Select(i => new DurInfoWrapper{
                    Path = i.Key,
                    Duration = new DurInfo(i)
                });

            var bResults = allResults
                .Where(i => i.Index.Commit == filter.CommitB)
                .GroupBy(i => i.Result.Path, i => i.Result)
                .Where(i => i.Count() > 0)
                .Select(i => new DurInfoWrapper{
                    Path = i.Key,
                    Duration = new DurInfo(i)
                });
                
            
            var rootA = aResults.First(i => i.Path == filter.Frame);
            var rootB = bResults.First(i => i.Path == filter.Frame);

            var levelA = aResults.Where(i => i.Path != filter.Frame).ToList();
            var levelB = bResults.Where(i => i.Path != filter.Frame).ToList();

            return new CompareCommitDto {
                RootA = rootA,
                RootB = rootB,
                CommitA = levelA,
                CommitB = levelB,
            };
        }
    }
}