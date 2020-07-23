using System;
using System.IO;
using System.Linq;
using MongoDB.Bson;
using MongoDB.Bson.Serialization;

namespace CC.Net.Db
{
    public static class Mongo
    {
        private static string _groupTimers = File.ReadAllText(
            Path.Join(Environment.CurrentDirectory, "mongo.group-timers.json")
        );

        public static string GroupTimers(string test, string mesh, string benchmark, string frame="whole-program", string branch="master")
            => _groupTimers
                .Replace("$$TEST$$", test)
                .Replace("$$MESH$$", mesh)
                .Replace("$$BENCHMARK$$", benchmark)
                .Replace("$$FRAME$$", frame)
                .Replace("$$BRANCH$$", branch);
    }

    public static class StringExtensions 
    {
        public static BsonDocument ASBsonDocument(this string json)
        {
            return BsonDocument.Parse(json);
        }

        public static BsonDocument[] AsBsonArray(this string json)
        {
            return BsonSerializer.Deserialize<BsonArray>(json)
                .Select(i => i.AsBsonDocument)
                .ToArray();
        }
    }
}