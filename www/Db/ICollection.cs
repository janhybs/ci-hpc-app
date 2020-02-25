using MongoDB.Bson;

namespace CC.Net.Db
{
    public interface ICollection
    {
        ObjectId Id { get; set; }

        string CacheProperty => Id.ToString();
    }
}