using System.Collections.Generic;
using MongoDB.Bson;
using MongoDB.Bson.Serialization.Attributes;

namespace CC.Net.Collections
{
    [BsonIgnoreExtraElements]
    public class ColTimersResult
    {
        [BsonElement("duration")]
        public double Duration { get; set; }

        [BsonElement("executed")]
        public double Executed { get; set; }

        [BsonElement("cnt_alloc")]
        public double CntAlloc { get; set; }

        [BsonElement("cnt_dealloc")]
        public double CntDealloc { get; set; }

        [BsonElement("mem_alloc")]
        public double MemAlloc { get; set; }

        [BsonElement("mem_dealloc")]
        public double MemDealloc { get; set; }

        [BsonElement("file_path")]
        public string FilePath { get; set; }

        [BsonElement("function")]
        public string Function { get; set; }

        [BsonElement("name")]
        public string Name { get; set; }

        [BsonElement("file_line")]
        public int FileLine { get; set; }

        [BsonElement("dur_ratio")]
        public double DurRatio { get; set; }

        [BsonElement("path")]
        public string Path { get; set; }

    }
}