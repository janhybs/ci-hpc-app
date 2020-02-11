using System.Collections.Generic;
using MongoDB.Bson;
using MongoDB.Bson.Serialization.Attributes;

namespace CC.Net.Collections
{
    [BsonIgnoreExtraElements]
    public class ColTimers
    {
        [BsonId]
        [BsonElement("_id")]
        public ObjectId Id { get; set; }
        public string objectId => Id.ToString();

        [BsonElement("index")]
        public IndexInfo Index { get; set; }

        [BsonElement("result")]
        public ColTimersResult Result { get; set; }
    }
}