using CC.Net.Collections.Shared;
using CC.Net.Db;
using MongoDB.Bson;
using MongoDB.Bson.Serialization.Attributes;

namespace CC.Net.Collections
{
    [BsonIgnoreExtraElements]
    public class ColScheduler: ICollection
    {
        [BsonId]
        [BsonElement("_id")]
        public ObjectId Id { get; set; }
        public string objectId => Id.ToString();


        [BsonElement("details")]
        public ColSchedulerDetails Details { get; set; }


        [BsonElement("index")]
        public IndexInfo Index { get; set; }


        [BsonElement("status")]
        public ColSchedulerStatus Status { get; set; }
        

        [BsonElement("worker")]
        public string Worker { get; set; }

    }
}