

namespace CC.Net.Config
{
    public class MongoDBConfig
    {
        public string Host { get; set; }
        public string AuthSource { get; set; }
        public string AuthMechanism { get; set; }
        public string Username { get; set; }
        public string Password { get; set; }
        public string Database { get; set; }
        public string CollectionTimers { get; set; }
        public string CollectionScheduler { get; set; }
        public string CollectionIndexInfo { get; set; }
        public string CollectionRepoInfo { get; set; }
    }
}