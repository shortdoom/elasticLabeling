from elasticsearch import Elasticsearch
import time
import pandas as pd

es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

# https://elasticsearch-py.readthedocs.io/en/master/
# https://www.elastic.co/guide/en/elasticsearch/reference/current/rest-apis.html

def save_columns(dataframe):

    '''Saves three files, keywords - category - main category to working directory.
       This servers as input for ElasticSearch matching.
       You need file in this format for function to work. Otherwise, skip or edit this step.
    '''

    tags = dataframe.reset_index()
    for column in tags.columns:
        tags[column].to_csv(column + '.txt', index=None)
        tags[column].to_csv(column + '.txt', index=None)
        tags[column].to_csv(column + '.txt', index=None)

def search(query, tag, tagList):

    '''This function calls elasticsearch with query, looks for a match and returns list.
       cateList and main_cateList are lists of categories corresponding to keyword list.
       Those files are generated using save_columns() function. You can comment those out
       and just match on your keyword list (ie. you are not working with multiple labels).
       Remember to edit list items if you are to do so. (matched list)
    '''

    cateList = [line.rstrip('\n') for line in open('/category_list.txt')]
    main_cateList = [line.rstrip('\n') for line in open('/main_category_list.txt')]

    result = es.search(index='temp_keyword', body=query, size=10000)
    num = result['hits']['total']['value']
    matched = []
    count = 0

    for hit in result['hits']['hits']:
        count += 1
        print(hit['_score'], hit['_source']['title'], 'MATCH ON ', tag)

        if hit['_source']['title'] is not None:

            tagIndex = tagList.index(tag)

            matched.append({'title': hit['_source']['title'],
                            'tag': tag,
                            'category': cateList[tagIndex],
                            'main category': main_cateList[tagIndex]})

            print(
                "NUM", num,
                "COUNT", count

            )
        if count == num:
            return matched

def query_input():

    '''Load list of keywords to match on.'''

    tagList = [line.rstrip('\n') for line in
               open('/keyword_list.txt')]

    matched = []
    start_time = time.time()

    '''Construct query with keyword list in a loop. Because keywords are usually few tokens long, we need to disable
       default Elastic tokenizer and use custom one. Analyzer needs to be specified at index level, so you will need to 
       re-map your index appropriately. You can find lower_phrase analyzer specification in separate file.
    '''

    for tag in tagList:
            query = { "explain": True,
                      "query": {
                        "match_phrase": {
                            "title": {
                                "query":tag,
                                "analyzer": "lower_phrase"
                    }
                }
            }
        }

            '''Call elasticsearch with constructed query. Append matches.'''

            match = search(query, tag, tagList)
            matched.append(match)

    print("--- %s seconds --- (took to model) " % (time.time() - start_time))

    '''Filter all empty objects and load data into dataframe'''

    matches_df = [x for x in filter(None, matched)]
    matches_df = pd.DataFrame([x for x in matches_df for x in x])

    '''Reconstruct dataframe. You want to have four columns. 
       First with matched document (title),
       Second with keyword on which match appeared (tag),
       Third with category of a keyword (category),
       Fourth with main category to which category belongs (main category)
    '''

    matches_df = matches_df.groupby('title')[['tag', 'category', 'main category']].\
                 agg({'tag': ', '.join, 'category': ', '.join, 'main category': ', '.join}).reset_index()

    return matches_df