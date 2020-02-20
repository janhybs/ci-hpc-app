using System.Collections.Generic;
using MongoDB.Bson;
using MongoDB.Bson.Serialization.Attributes;

namespace CC.Net.Collections
{
    [BsonIgnoreExtraElements]
    public class ColSchedulerDetails
    {
        [BsonElement("priority")]
        public int Priority { get; set; }

        [BsonElement("repetitions")]
        public int Repetitions { get; set; }
    }
}