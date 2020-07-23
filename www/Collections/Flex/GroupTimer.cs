using System;
using System.Collections.Generic;
using System.Text.Json.Serialization;
using CC.Net.Stats;
using MongoDB.Bson.Serialization.Attributes;

namespace CC.Net.Collections.Flex
{
    [BsonIgnoreExtraElements]
    public class GroupedTimer: IDurations
    {
        [BsonElement("commit")]
        public string Commit { get; set; }


        [BsonElement("durations")]
        public double[] Durations { get; set; }


        [BsonElement("info")]
        public ColRepoInfo Info { get; set; }



        [BsonIgnore]
        public int Count => Durations.Length;

        [BsonIgnore]
        public Welch Welch { get; set; }

        [BsonIgnore]
        public List<string> Left { get; set; }

        [BsonIgnore]
        public List<string> Right { get; set; }

        [BsonIgnore]
        [JsonIgnore]
        public WelchType WelchType => Welch == null
            ? WelchType.Unknown
            : Welch.EstimatedValue1 > Welch.EstimatedValue2
                ? WelchType.Improvement
                : WelchType.Decline;
        

        override public string ToString()
        {
            return $"{Commit?.Substring(0, 6)} {WelchType}";
        }
    }
}