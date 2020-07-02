using System.Collections.Generic;
using CC.Net.Collections.Shared;
using CC.Net.Db;
using MongoDB.Bson;
using MongoDB.Bson.Serialization.Attributes;

namespace CC.Net.Collections
{
    [BsonIgnoreExtraElements]
    public class ColIndexInfo: ICollection
    {
        [BsonId]
        [BsonElement("_id")]
        public ObjectId Id { get; set; }
        public string objectId => Id.ToString();


        [BsonElement("index")]
        public IndexInfo Index { get; set; }


        [BsonElement("run")]
        public ColIndexInfoRun Run { get; set; }

        string CacheProperty => Index?.Commit;
    }
}