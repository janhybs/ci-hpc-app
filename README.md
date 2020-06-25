# ci-hpc-app &middot; [![Actions Status](https://github.com/janhybs/ci-hpc-app/workflows/Python%20application/badge.svg)](https://github.com/janhybs/ci-hpc-app/actions) [![Coveralls github](https://img.shields.io/coveralls/github/janhybs/ci-hpc-app?logo=codeforces&logoColor=999&style=flat&labelColor=393939)](https://coveralls.io/github/janhybs/ci-hpc-app)


```js
db.getCollection('timers-2019-2').aggregate([
    {
        "$group": {
            "_id": "$index.cpus",
            "sum": { "$sum": 1 }
        }
    }
])

db.getCollection('timers-2019-2').find({"index.cpus": "< cpus >"})

db.getCollection('timers-2019-2').updateMany(
    { "index.cpus": "< cpus >" },
    {
        "$set": {
            "index.cpus": 1.0
        }
    }
)
```