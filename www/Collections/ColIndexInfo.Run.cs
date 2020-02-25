using System.Collections.Generic;
using cc.net.Collections.Shared;
using MongoDB.Bson;
using MongoDB.Bson.Serialization.Attributes;

namespace CC.Net.Collections
{
    [BsonIgnoreExtraElements]
    public class ColIndexInfoRun
    {

        [BsonElement("duration")]
        public double Duration { get; set; }


        [BsonElement("returncode")]
        public int Returncode { get; set; }

        public bool IsBroken => Returncode != 0;
    }
}