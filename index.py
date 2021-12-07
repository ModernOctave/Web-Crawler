from elasticsearch import Elasticsearch
import json

class Index:
	esClient = Elasticsearch(['http://localhost:9200'])
	mapping = {
		"settings": {
			"analysis": {
				"analyzer": {
					"customAnalyzer": {
						"type": "custom",
						"tokenizer": "standard",
				        "filter": [ "stemmer", "lowercase", "stop"]
					}
				}
			}
		},
		"mappings": {
			"properties": {
				"path": {"type": "text"},
				"data": {"type": "text", "analyzer": "customAnalyzer"}
			}
		}
	}
	createIndex = esClient.indices.create(index='searchapp', body=mapping, ignore=400) #ignore 400 ignores creation of index if already present
	print(createIndex)

	def IndexFile(self, data):
		res = self.esClient.index(index='searchapp', doc_type='_doc', document=data)
		print(res)

def main():
	file = open("data.json")
	data = json.load(file)
	index = Index()
	for doc in data:
		index.IndexFile(doc)
	
if __name__ == '__main__':
    main()