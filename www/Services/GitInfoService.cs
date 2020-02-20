using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using CC.Net.Config;
using LibGit2Sharp;

namespace CC.Net.Services
{
    public class GitInfoService
    {
        public AppOptions _appOptions { get; }
        public Repository _repo { get; }

        public Dictionary<string, GitInfo> _commits { get; }

        public GitInfoService(AppOptions appOptions)
        {
            _appOptions = appOptions;
            var project = appOptions.Projects.First();
            var location = new DirectoryInfo(Path.Combine(
                ".", "..", ".tmp", $".{project.Name.ToLower()}.gitinfo"
            )).FullName;

            if (!Repository.IsValid(location))
            {
                var result = Repository.Clone(project.Url, location);
            }

            _repo = new Repository(location);
            Commands.Fetch(_repo, "origin", new string[0], new FetchOptions(), null);

            _commits = new Dictionary<string, GitInfo>();
            foreach (var branch in _repo.Branches)
            {
                var branchName = branch.FriendlyName;
                branchName = branchName.StartsWith("origin/") ? branchName.Substring(7) : branchName;

                var current = branch.Tip;
                _commits[current.Id.Sha] = GitInfo.From(current, branchName);

                while(current != null && current.Parents.Count() == 1) {
                    current = current.Parents.First();
                    _commits[current.Id.Sha] = GitInfo.From(current, branchName);
                }
            }
        }

        public GitInfo Get(string sha)
        {
            var cmt = (Commit) _repo.Lookup(new ObjectId(sha));
            return _commits.GetValueOrDefault(sha, GitInfo.From(cmt, "--uknown--"));
        }
    }
}