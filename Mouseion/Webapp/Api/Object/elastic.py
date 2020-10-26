from elasticsearch import Elasticsearch

es = Elasticsearch(["http://elasticsearch:9200"])

mapping = {
    "settings": {
        "number_of_shards": 10,
        "index": {
          "analysis": {
            "analyzer": {
              "my_analyzer": {
                "type": "custom",
                "tokenizer": "keyword",
                "filter": [
                  "lowercase",
                  "reverse",
                  "suffixes",
                  "reverse"
                ]
              }
            },
            "filter": {
              "suffixes": {
                "type": "edgeNGram",
                "min_gram": 1,
                "max_gram": 20
              }
            }
          }
        }
      },
    "mappings" : {
      "properties" : {
        "date" : {
          "type" : "text",
          "fields" : {
            "keyword" : {
              "type" : "keyword",
              "ignore_above" : 256
            }
          }
        },
        "folder" : {
          "type" : "text",
          "fields" : {
            "keyword" : {
              "type" : "keyword",
              "ignore_above" : 256
            }
          }
        },
        "lang" : {
          "type" : "text",
          "fields" : {
            "keyword" : {
              "type" : "keyword",
              "ignore_above" : 256
            }
          }
        },
        "lexiq" : {
          "type": "text",
          "analyzer": "my_analyzer",
          "search_analyzer": "standard"
        },
        "map" : {
            "type": "object",
            "enabled": False
        },
        "restriction" : {
          "type" : "text",
          "fields" : {
            "keyword" : {
              "type" : "keyword",
              "ignore_above" : 256
            }
          }
        },
        "text" : {
          "type" : "text",
          "fields" : {
            "keyword" : {
              "type" : "keyword",
              "ignore_above" : 256
            }
          }
        },
        "title" : {
          "type" : "text",
          "fields" : {
            "keyword" : {
              "type" : "keyword",
              "ignore_above" : 256
            }
          }
        },
        "type" : {
          "type" : "text",
          "fields" : {
            "keyword" : {
              "type" : "keyword",
              "ignore_above" : 256
            }
          }
        },
        "url" : {
          "type" : "text",
          "fields" : {
            "keyword" : {
              "type" : "keyword",
              "ignore_above" : 256
            }
          }
        }
      }
    }
  }
