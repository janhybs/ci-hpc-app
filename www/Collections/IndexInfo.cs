using System.Collections.Generic;
using MongoDB.Bson;
using MongoDB.Bson.Serialization.Attributes;

namespace CC.Net.Collections
{
    [BsonIgnoreExtraElements]
    public class IndexInfo
    {
        [BsonElement("project")]
        public string Project { get; set; }

        [BsonElement("commit")]
        public string Commit { get; set; }
        public string CommitShort => string.IsNullOrEmpty(Commit) ? "" : Commit.Substring(0, 8);

        [BsonElement("branch")]
        public string Branch { get; set; }

        [BsonElement("job")]
        public string Job { get; set; }

        [BsonElement("test")]
        public string Test { get; set; }

        [BsonElement("benchmark")]
        public string Benchmark { get; set; }

        [BsonElement("mesh")]
        public string Mesh { get; set; }

        [BsonElement("cpus")]
        public int Cpus { get; set; }

        [BsonElement("frame")]
        public string Frame { get; set; }

        [BsonElement("uuid")]
        public object Uuid { get; set; }

        [BsonElement("host")]
        public object Host { get; set; }

        [BsonElement("mesh_cpus")]
        public object MeshCpus { get; set; }

        [BsonElement("mesh_size")]
        public object MeshSize { get; set; }

    }
}