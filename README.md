# elasticLabeling

Match (long) keywords from txt file to list of documents in ElasticSearch. Fast!

## What is it? What does it do?

In machine learning classification problems we often need a good chunk of hand labeled data. This varies depending on dataset, but often goes into thousands of documents for big corpus. More than often this tasks can be made easier with automatic labeling of documents. Of course, it's not always a case that we can use some set of domain based keywords, but sometimes - yes. What if we have thousand of keywords too? Libraries like ```spacy``` are not necessarily suited well for matching against long keywords list, especially if those are few words long ie. ```apple``` versus ```healthy apple tree``` can become very time consuming. Snorkel focuses more on using established logic to match documents. Matching long keywords purely in python seems to be troublesome. Therefore, we use speed and elasticity of ElasticSearch!

### In short
- Supply list of keywords you want to match on
- Supply list of categories for those keywords (**Need to be formatted line-by-line, use save_columns! Can be skipped**)
- Supply list of main categories to your categories (**You can skip it if you want**)
- Construct exact match query for documents in your elasticsearch index (**Your documents have to be already indexed in Elastic**)

### Necessary tweaks for ElasticSearch to perform exact matching

You can index your documents with as many fields as you desire, however, field on which you will perform exact string matching needs to be indexed with appropriate analyzer. Change your index ```settings``` and ```mapping``` of a field of interest to:

```
'analysis': {
  'analyzer': {
      'lower_phrase': {
       'filter': ['lowercase'],
       'type': 'custom',
       'tokenizer': 'whitespace'}
      }
   },
```

Use same analyzer for your query.

This is necessary because by default elasticsearch uses tokenizer which removes special signs and breaks down your document into separate tokens. It's fine if your keywords are one word long, it's bad if you match against long keywords.

### Why use it?

It's very fast :)

It can perform multiple other queries (including, similarity queries more_like_this, just rewrite your query!)

### TODO

Well, this can be easily extended into weak supervision engine for document classification:
  - More options for matching
  - Built-in similarity & clustering of found documents for validation of matches
  - Easier loading and indexing, right now you need to perform those operations on your own (ie. change analyzer)
  - Choice of different analyzers (You don't always want to lowercase!)
