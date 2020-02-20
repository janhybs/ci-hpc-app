using System;
using LibGit2Sharp;

namespace CC.Net.Services
{
    public class GitInfo
    {
        public string Branch { get; set; }
        public DateTimeOffset Date { get; set; }
        public string Message { get; set; }

        public static GitInfo From(Commit commit, string branch = null)
        {
            return new GitInfo{
                Date = commit.Author.When,
                Message = commit.MessageShort,
                Branch = branch
            };
        }
    }
}