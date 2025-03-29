from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9200")

index_name = "mock_index"

# Delete if already exists
if es.indices.exists(index=index_name):
    es.indices.delete(index=index_name)
    print(f"[TEST] Deleted existing index '{index_name}'")

# Create index with basic mapping
es.indices.create(index=index_name, body={
    "mappings": {
        "properties": {
            "UserID": { "type": "keyword" },
            "UserName": { "type": "text" },
            "Age": { "type": "integer" },
            "EmailAddress": { "type": "keyword" }
        }
    }
})

# Add sample documents
docs = [
    {"UserID": "U001", "UserName": "Alice", "Age": 30, "EmailAddress": "alice@example.com"},
    {"UserID": "U002", "UserName": "Bob", "Age": 25, "EmailAddress": "bob@example.com"},
    {"UserID": "U003", "UserName": "Charlie", "Age": 35, "EmailAddress": "charlie@example.com"}
]

for i, doc in enumerate(docs):
    es.index(index=index_name, id=i+1, body=doc)

es.indices.refresh(index=index_name)
print(f"[TEST] Test index '{index_name}' created with {len(docs)} documents.")
