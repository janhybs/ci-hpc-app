namespace CC.Net.Dto
{
    public class CommitBaseline
    {
        public string Value  { get; set; }
        public string Name  { get; set; }

        public CommitBaseline(string commit, string name)
        {
            this.Value = commit;
            this.Name = name;
        }
    }
}