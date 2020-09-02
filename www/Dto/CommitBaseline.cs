namespace CC.Net.Dto
{
    public class CommitBaseline
    {
        public string Commit  { get; set; }
        public string Name  { get; set; }

        public CommitBaseline(string commit, string name)
        {
            this.Commit = commit;
            this.Name = name;
        }
    }
}