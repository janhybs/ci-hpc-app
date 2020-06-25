using System;
using System.Collections.Generic;
using CC.Net.Db;
using MongoDB.Bson;
using MongoDB.Bson.Serialization.Attributes;

namespace CC.Net.Collections
{
    [BsonIgnoreExtraElements]
    public class ColRepoInfo: ICollection
    {
        [BsonId]
        [BsonElement("_id")]
        public ObjectId Id { get; set; }
        public string objectId => Id.ToString();


        [BsonElement("branches")]
        public List<string> Branches { get; set; }

        [BsonElement("author")]
        public string Author { get; set; }

        [BsonElement("email")]
        public string Email { get; set; }

        [BsonElement("commit")]
        public string Commit { get; set; }

        [BsonElement("branch")]
        public string Branch { get; set; }

        [BsonElement("authored_datetime")]
        public DateTime AuthoredDatetime { get; set; }

        [BsonElement("committed_datetime")]
        public DateTime CommittedDatetime { get; set; }

        [BsonElement("message")]
        public string Message { get; set; }

        [BsonElement("distance")]
        public int Distance { get; set; }

        [BsonElement("parents")]
        public List<string> Parents { get; set; }

        [BsonElement("children")]
        public List<string> Children { get; set; }

        [BsonIgnore]
        public List<double> Durations { get; set; }
    }
}