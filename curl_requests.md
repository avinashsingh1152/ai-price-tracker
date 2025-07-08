# Example curl requests for AI Price Tracker API

## US Example
```
curl -X POST http://localhost:8000/fetch-prices \
  -H "Content-Type: application/json" \
  -d '{"country": "US", "query": "iPhone 16 Pro, 128GB"}'
```

## IN Example
```
curl -X POST http://localhost:8000/fetch-prices \
  -H "Content-Type: application/json" \
  -d '{"country": "IN", "query": "boAt Airdopes 311 Pro"}'
``` 