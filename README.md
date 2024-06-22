
To check Milvus installation send an HTTP request to http://localhost:19530/v1/vector/collections
```bash
curl "http://localhost:19530/v1/vector/collections"
```

Output 
```json
{"code":200,"data":[]}
```

Then you can continue managing Milvus system via Attu web interface at http://localhost:8080