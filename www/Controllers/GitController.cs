using System;
using System.Collections;
using System.Collections.Generic;
using CC.Net.Collections;
using CC.Net.Services;
using Microsoft.AspNetCore.Mvc;

namespace CC.Net.Controllers
{

    [ApiController]
    [Route("api/git")]
    public class GitController
    {
        private readonly RepoInfoCache _repoInfo;

        public GitController(RepoInfoCache repoInfo)
        {
            _repoInfo = repoInfo;
        }

        [HttpGet]
        [Route("list/{days}")]
        public IEnumerable<ColRepoInfo> List(int days = 2)
        {
            return _repoInfo.GetAll(
                DateTime.Now.AddDays(-days)
            );
        }
    }
}