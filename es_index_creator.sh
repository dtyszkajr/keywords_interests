# creates elasticsearch index used in the rss_reader_folha scipt

curl -XPUT 'http://localhost:9200/i_rsslinks_v1' -d '{
    "settings": {
        "index": {
            "refresh_interval": "15s",
            "number_of_shards": "1",
            "number_of_replicas": "0"
        }
    },
    "mappings": {
        "m_rsslinks_v1": {
            "properties": {
                "title": {
                    "type": "string",
                    "index": "not_analyzed"
                },
                "link": {
                    "type": "string",
                    "index": "not_analyzed"
                },
                "category": {
                    "type": "string",
                    "index": "not_analyzed"
                }
            }
        }
    }
}'
