### html loader
not working well in chinese pages.

[langchain html loader](https://python.langchain.com/docs/modules/data_connection/document_loaders/html/)
provide several ways to load data from html file.
static methods: UnstructuredHTMLLoader, BSHTMLLoader
SaaS methods: SpiderLoader, FireCrawlLoader, AzureAIDocumentIntelligenceLoader

## cloud functions
### purge user data (for testing)
deploy deleteUserData.js as cloud function, and call it by curl
```
curl -X DELETE 'https://xxx/deleteUserData?userId=...'
```