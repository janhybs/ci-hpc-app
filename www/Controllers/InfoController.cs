using System.Collections.Generic;
using CC.Net.Dto;
using Microsoft.AspNetCore.Mvc;

namespace CC.Net.Controllers
{

    [ApiController]
    [Route("api/info")]
    public class InfoController:  ControllerBase
    {
        [HttpGet("/baselines")]
        public List<CommitBaseline> GetBaselines()
        {
            return new List<CommitBaseline>{
                new CommitBaseline("6b54fcf046d36cb37bfcc53bd6e613eca1459bda", "v3.0.0"),
                new CommitBaseline("b04af7fb08d423036b30ea00c3b8941b0c91e3c0", "v2.2.1"),
                new CommitBaseline("f72c4b41f40db374168cc91ca59e6e7d87555596", "v3.0.2"),
                new CommitBaseline("4db4b481073edc73c22031aeb86c31c9b633025a", "v3.0.4"),
            };
        }
    }
}