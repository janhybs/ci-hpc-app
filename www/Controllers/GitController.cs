using System;
using System.Collections;
using System.Collections.Generic;
using CC.Net.Collections;
using CC.Net.Db;
using CC.Net.Services;
using Microsoft.AspNetCore.Mvc;
using MongoDB.Driver;

namespace CC.Net.Controllers
{
    [ApiController]
    [Route("api/git")]
    public class GitController
    {
        private readonly RepoInfoCache _repoInfo;
        private readonly CachedCollection<ColIndexInfo> _indexInfo;

        public GitController(RepoInfoCache repoInfo, DbService dbService)
        {
            _repoInfo = repoInfo;
            _indexInfo = dbService.CachedColIndexInfo;
        }

        private ColIndexInfo FindByCommit(string commit)
        {
            return _indexInfo.Collection
                .Find(i => i.Index.Commit == commit && i.Index.Job == "compile")
                .FirstOrDefault();
        }

        [HttpGet]
        [Route("get/{commit}")]
        public object Get(string commit)
        {
            var item = _repoInfo[commit];
            return new
            {
                Git = item,
                Info = _indexInfo.GetDocument(
                            item.Commit,
                            () => FindByCommit(item.Commit)
                        )?.Run
            };
        }

        [HttpGet]
        [Route("list/{days}")]
        public IEnumerable<object> List(int days = 2)
        {
            var items = _repoInfo.GetAll(DateTime.Now.AddDays(-days));

            foreach (var item in items)
            {
                yield return new
                {
                    Git = item,
                    Info = _indexInfo.GetDocument(
                            item.Commit,
                            () => FindByCommit(item.Commit)
                        )?.Run
                };
            }
        }
    }
}