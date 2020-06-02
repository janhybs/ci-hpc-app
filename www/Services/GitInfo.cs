using System;
using System.Collections.Generic;
using CC.Net.Collections;
using LibGit2Sharp;

namespace CC.Net.Services
{
    public class GitInfo
    {
        public string Branch { get; set; }
        public DateTimeOffset Date { get; set; }
        public string Message { get; set; }
        public List<string> Branches { get; set; } = new List<string>();

        public static GitInfo From(Commit commit, string branch = null)
        {
            return new GitInfo
            {
                Date = commit.Author.When,
                Message = commit.MessageShort,
                Branch = branch,
            };
        }

        public static GitInfo From(ColRepoInfo repoInfo)
        {
            if (repoInfo == null)
            {
                return Empty();
            }

            return new GitInfo
            {
                Date = repoInfo.AuthoredDatetime, // commited date?
                Message = repoInfo.Message,
                Branch = repoInfo.Branch,
                Branches = repoInfo.Branches,
            };
        }
        public static GitInfo Empty()
        {
            return new GitInfo
            {
                Date = new DateTimeOffset(),
                Message = null,
                Branch = null,
            };
        }
    }
}