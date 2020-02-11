using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using CC.Net.Collections;
using CC.Net.Db;
using CC.Net.Dto;
using CC.Net.Extensions;
using CC.Net.Utils;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using MongoDB.Bson;
using MongoDB.Driver;
using Newtonsoft.Json;

namespace CC.Net.Controllers
{
    [ApiController]
    [Route("api/scheduler")]
    public class SchedulerController : ControllerBase
    {

        private readonly ILogger<SchedulerController> _logger;
        private readonly DbService _dbService;

        public SchedulerController(ILogger<SchedulerController> logger, DbService dbService)
        {
            _logger = logger;
            _dbService = dbService;
        }

        [HttpPost]
        [Route("list")]
        public object ActionList(SchedulerFilter filter)
        {
            return _dbService.ColScheduler
                .Find(i => i.Status == filter.status)
                .Limit(filter.limit)
                .SortBy(i => i.Id)
                .ToList();
        }

    }
}
