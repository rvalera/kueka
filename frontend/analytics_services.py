from kueka.settings import graph, db
import wikipedia
from datetime import timedelta, datetime
import json
from traceback import print_exc

def most_important_actors(entity_type, date_from=None, date_to=None, amount=10):
    results = []
    cypher = graph.cypher

    if date_to is None:
        date_to = datetime.now()
        date_to = date_to.replace(hour=23, minute=59, second=59)
        
    if date_from is None:    
        date_from = date_to.replace(hour=0, minute=0, second=0) - timedelta(days=1)    

    cquery = '''
MATCH (me:Person)-[r1:TAGGED]-(news:News)
WHERE news.created >= {date_from} AND news.created <= {date_to}  
WITH  DISTINCT(me), COUNT(DISTINCT r1) as countNews 
ORDER BY countNews DESC
LIMIT {limit}
RETURN me,countNews
    ''' if entity_type == 'Person' else '''
MATCH (me:Organization)-[r1:TAGGED]-(news:News)
WHERE news.created >= {date_from} AND news.created <= {date_to}  
WITH  DISTINCT(me), COUNT(DISTINCT r1) as countNews 
ORDER BY countNews DESC
LIMIT {limit}
RETURN me,countNews
    '''
    cypher_result = cypher.execute(cquery, date_from=date_from, date_to=date_to, limit=amount)
    for r in cypher_result:
        results.append({'name' : r['me']['name']})

    return results


def most_important_locations(date_from=None, date_to=None, amount=10):
    results = []
    cypher = graph.cypher

    if date_to is None:
        date_to = datetime.now()
        date_to = date_to.replace(hour=23, minute=59, second=59)
        
    if date_from is None:    
        date_from = date_to.replace(hour=0, minute=0, second=0) - timedelta(days=1)    


    cquery = '''
MATCH (me:Location)-[r1:LOCATED]-(news:News)
WHERE news.created >= {date_from} AND news.created <= {date_to}  
WITH  DISTINCT(me), COUNT(DISTINCT r1) as countNews 
ORDER BY countNews DESC
LIMIT {limit}
RETURN me,countNews
    '''
    cypher_result = cypher.execute(cquery, date_from=date_from, date_to=date_to, limit=amount)
    for r in cypher_result:
        results.append({'name' : r['me']['name'], 'latitude' : r['me']['latitude'], 'longitude' : r['me']['longitude']})

    return results

def most_important_sources(date_from=None, date_to=None, amount=10):
    results = []
    cypher = graph.cypher

    if date_to is None:
        date_to = datetime.now()
        date_to = date_to.replace(hour=23, minute=59, second=59)
        
    if date_from is None:    
        date_from = date_to.replace(hour=0, minute=0, second=0) - timedelta(days=1)    


    cquery = '''
MATCH (me:Source)-[r1:CREATED]-(news:News)
WHERE news.created >= {date_from} AND news.created <= {date_to}  
WITH  DISTINCT(me), COUNT(DISTINCT r1) as countNews 
ORDER BY countNews DESC
LIMIT {limit}
RETURN me,countNews
    '''
    cypher_result = cypher.execute(cquery, date_from=date_from, date_to=date_to, limit=amount)
    for r in cypher_result:
        results.append({'name' : r['me']['name']})

    return results


def get_actor_relationships(entity_type,name,relationship_type,date_from=None, date_to=None, amount=10):
    results = []
    cypher = graph.cypher

    if date_to is None:
        date_to = datetime.now()
        date_to = date_to.replace(hour=23, minute=59, second=59)
        
    if date_from is None:
        date_from = date_to.replace(hour=0, minute=0, second=0) - timedelta(days=1)    
    
    if relationship_type == 'Source':
        partial_query_1 = 'MATCH (me:%s)-[r1:TAGGED]-(news:News)-[r2:CREATED]-(other:Source)' % entity_type
    else:
        partial_query_1 = 'MATCH (me:%s)-[r1:TAGGED]-(news:News)-[r2:%s]-(other:%s)' % (entity_type,'LOCATED' if relationship_type == 'Location' else 'TAGGED' ,relationship_type)
    
    
    partial_query_2 =  '''
WHERE news.created >= {date_from} AND news.created <= {date_to} AND me.name = {name} 
WITH  DISTINCT(other), COUNT(DISTINCT r2) as countNews 
ORDER BY countNews DESC
LIMIT {limit}
RETURN other,countNews
    ''' 
    
    cquery = '%s %s' % (partial_query_1,partial_query_2)

    cypher_result = cypher.execute(cquery, name = name, date_from=date_from, date_to=date_to, limit=amount)
    for r in cypher_result:
        if (relationship_type == 'Location'):
            results.append({'name' : r['other']['name'], 'latitude' : r['other']['latitude'], 'longitude' : r['other']['longitude']})
        else:
            results.append({'name' : r['other']['name']})

    return results

def get_summary_wikipedia(name):
#     wikipedia.set_lang("en")
    wiki = None
    try:
        wiki=wikipedia.summary(name)
    except Exception as e:
        pass            

    return wiki

def get_metadata_wikipedia(name):
    metadata = {}
    metadata['images'] = []            
    metadata['text'] = 'Description Not Found'            
#     wikipedia.set_lang("es")
    try:
        wiki=wikipedia.WikipediaPage(name)
        if not wiki is None:
            try:
                tuple_coordinates = wiki.coordinates
                metadata['latitude'] = tuple_coordinates[0]
                metadata['longitude'] = tuple_coordinates[1]            
            except Exception as e:
                pass            
            
            metadata['images'] = wiki.images            
            metadata['text'] = wiki.summary            
    except Exception as e:
        pass            

    return metadata
    

def get_actor(entity_type,name,date_from=None, date_to=None, amount=10):
    results = {}
    results['name'] = name

#     results['text'] = get_summary_wikipedia(name)
    results.update(get_metadata_wikipedia(name))
    
    relationships = {}
    relationships['person'] = get_actor_relationships(entity_type,name,'Person', date_from, date_to, amount)
    relationships['organization'] = get_actor_relationships(entity_type,name,'Organization',date_from, date_to, amount)
    relationships['location'] = get_actor_relationships(entity_type,name,'Location',date_from, date_to, amount)
    relationships['source'] = get_actor_relationships(entity_type,name,'Source',date_from, date_to, amount)
    

    results['relationships'] = relationships
    return results


def get_location_relationships(name, relationship_type, date_from=None, date_to=None, amount=10):
    results = []
    cypher = graph.cypher

    if date_to is None:
        date_to = datetime.now()
        date_to = date_to.replace(hour=23, minute=59, second=59)
        
    if date_from is None:    
        date_from = date_to.replace(hour=0, minute=0, second=0) - timedelta(days=1)    
    
    if relationship_type == 'Source':
        partial_query_1 = 'MATCH (me:Location)-[r1:LOCATED]-(news:News)-[r2:CREATED]-(other:Source)'
    else:
        partial_query_1 = 'MATCH (me:Location)-[r1:LOCATED]-(news:News)-[r2:%s]-(other:%s)' % ('LOCATED' if relationship_type == 'Location' else 'TAGGED' ,relationship_type)
    
    
    partial_query_2 =  '''
WHERE news.created >= {date_from} AND news.created <= {date_to} AND me.name = {name} 
WITH  DISTINCT(other), COUNT(DISTINCT r2) as countNews 
ORDER BY countNews DESC
LIMIT {limit}
RETURN other,countNews
    ''' 
    
    cquery = '%s %s' % (partial_query_1,partial_query_2)

    cypher_result = cypher.execute(cquery, name = name, date_from=date_from, date_to=date_to, limit=amount)
    for r in cypher_result:
        if (relationship_type == 'Location'):
            results.append({'name' : r['other']['name'], 'latitude' : r['other']['latitude'], 'longitude' : r['other']['longitude']})
        else:
            results.append({'name' : r['other']['name']})

    return results


def get_location(name,date_from=None, date_to=None, amount=10):
    results = {}
    results['name'] = name

#     results['text'] = get_summary_wikipedia(name)
    results.update(get_metadata_wikipedia(name))
    
    relationships = {}
    relationships['person'] = get_location_relationships(name,'Person', date_from, date_to, amount)
    relationships['organization'] = get_location_relationships(name,'Organization',date_from, date_to, amount)
    relationships['location'] = get_location_relationships(name,'Location',date_from, date_to, amount)
    relationships['source'] = get_location_relationships(name,'Source',date_from, date_to, amount)

    results['relationships'] = relationships
    return results


def get_source_relationships(name, relationship_type, date_from=None, date_to=None, amount=10):
    results = []
    cypher = graph.cypher

    if date_to is None:
        date_to = datetime.now()
        date_to = date_to.replace(hour=23, minute=59, second=59)
        
    if date_from is None:    
        date_from = date_to.replace(hour=0, minute=0, second=0) - timedelta(days=1)    
    
    partial_query_1 = 'MATCH (me:Source)-[r1:CREATED]-(news:News)-[r2:%s]-(other:%s)' % ('LOCATED' if relationship_type == 'Location' else 'TAGGED' ,relationship_type)
    
    
    partial_query_2 =  '''
WHERE news.created >= {date_from} AND news.created <= {date_to} AND me.name = {name} 
WITH  DISTINCT(other), COUNT(DISTINCT r2) as countNews 
ORDER BY countNews DESC
LIMIT {limit}
RETURN other,countNews
    ''' 
    
    cquery = '%s %s' % (partial_query_1,partial_query_2)

    cypher_result = cypher.execute(cquery, name = name, date_from=date_from, date_to=date_to, limit=amount)
    for r in cypher_result:
        if (relationship_type == 'Location'):
            results.append({'name' : r['other']['name'], 'latitude' : r['other']['latitude'], 'longitude' : r['other']['longitude']})
        else:
            results.append({'name' : r['other']['name']})

    return results



def get_source(name,date_from=None, date_to=None, amount=10):
    results = {}
    
    results['name'] = name

#     results['text'] = get_summary_wikipedia(name)
#    results.update(get_metadata_wikipedia(name))
    
    relationships = {}
    relationships['person'] = get_source_relationships(name,'Person', date_from, date_to, amount)
    relationships['organization'] = get_source_relationships(name,'Organization',date_from, date_to, amount)
    relationships['location'] = get_source_relationships(name,'Location',date_from, date_to, amount)

    results['relationships'] = relationships
    return results

def get_news(date_from=None, date_to=None, page_number=0, page_size=10):

    if date_to is None:
        date_to = datetime.now()
        date_to = date_to.replace(hour=23, minute=59, second=59)
    range_to = int(date_to.strftime("%s"))
        
    if date_from is None:    
        date_from = date_to.replace(hour=0, minute=0, second=0) - timedelta(days=1)    
    range_from = int(date_from.strftime("%s"))

    query = {'created' : {'$gte' : range_from, '$lte' :  range_to}}

    news_col = db['news'] 
    total_count = news_col.find(query).count()
    total_pages = int(total_count / page_size) + 1

    start_pos = page_number * page_size

    cursor = news_col.find(query).skip(start_pos).limit(page_size)
    
    result = {}
    content = []
    for doc in cursor:
        object_id = doc['_id']
        del(doc['_id'])
        doc['_id'] = str(object_id)
        content.append(doc)

    result['page_number'] = page_number
    result['page_size'] = page_size
    result['total_pages'] = total_pages
    result['total_elements'] = total_count
    result['number_elements'] = len(content)
    result['content'] = content

    return result


def get_news_by_actor(entity_type, name, date_from=None, date_to=None, page_number=0, page_size=10):

    if date_to is None:
        date_to = datetime.now()
        date_to = date_to.replace(hour=23, minute=59, second=59)
    range_to = int(date_to.strftime("%s"))
        
    if date_from is None:    
        date_from = date_to.replace(hour=0, minute=0, second=0) - timedelta(days=1)    
    range_from = int(date_from.strftime("%s"))

    query = {'created' : {'$gte' : range_from, '$lte' :  range_to}}
    
    if entity_type == 'Person':
        query['person'] = name
    else:
        query['organization'] = name
         

    news_col = db['news'] 
    total_count = news_col.find(query).count()
    total_pages = int(total_count / page_size) + 1

    start_pos = page_number * page_size

    cursor = news_col.find(query).skip(start_pos).limit(page_size)
    
    result = {}
    content = []
    for doc in cursor:
        object_id = doc['_id']
        del(doc['_id'])
        doc['_id'] = str(object_id)
        content.append(doc)

    result['page_number'] = page_number
    result['page_size'] = page_size
    result['total_pages'] = total_pages
    result['total_elements'] = total_count
    result['number_elements'] = len(content)
    result['content'] = content

    return result


def get_news_by_location(name, date_from=None, date_to=None, page_number=0, page_size=10):

    if date_to is None:
        date_to = datetime.now()
        date_to = date_to.replace(hour=23, minute=59, second=59)
    range_to = int(date_to.strftime("%s"))
        
    if date_from is None:    
        date_from = date_to.replace(hour=0, minute=0, second=0) - timedelta(days=1)    
    range_from = int(date_from.strftime("%s"))

    query = {'created' : {'$gte' : range_from, '$lte' :  range_to}, 'location' : name}

    news_col = db['news'] 
    total_count = news_col.find(query).count()
    total_pages = int(total_count / page_size) + 1

    start_pos = page_number * page_size

    cursor = news_col.find(query).skip(start_pos).limit(page_size)
    
    result = {}
    content = []
    for doc in cursor:
        object_id = doc['_id']
        del(doc['_id'])
        doc['_id'] = str(object_id)
        content.append(doc)

    result['page_number'] = page_number
    result['page_size'] = page_size
    result['total_pages'] = total_pages
    result['total_elements'] = total_count
    result['number_elements'] = len(content)
    result['content'] = content

    return result

def get_news_by_source(name, date_from=None, date_to=None, page_number=0, page_size=10):

    if date_to is None:
        date_to = datetime.now()
        date_to = date_to.replace(hour=23, minute=59, second=59)
    range_to = int(date_to.strftime("%s"))
        
    if date_from is None:    
        date_from = date_to.replace(hour=0, minute=0, second=0) - timedelta(days=1)    
    range_from = int(date_from.strftime("%s"))

    query = {'created' : {'$gte' : range_from, '$lte' :  range_to}, 'source' : name}

    news_col = db['news'] 
    total_count = news_col.find(query).count()
    total_pages = int(total_count / page_size) + 1

    start_pos = page_number * page_size

    cursor = news_col.find(query).skip(start_pos).limit(page_size)
    
    result = {}
    content = []
    for doc in cursor:
        object_id = doc['_id']
        del(doc['_id'])
        doc['_id'] = str(object_id)
        content.append(doc)

    result['page_number'] = page_number
    result['page_size'] = page_size
    result['total_pages'] = total_pages
    result['total_elements'] = total_count
    result['number_elements'] = len(content)
    result['content'] = content

    return result

from bson.son import SON

def get_sentiment_frecuencies(sentiment, date_from=None, date_to=None):
    if date_to is None:
        date_to = datetime.now()
        date_to = date_to.replace(hour=23, minute=59, second=59)
    range_to = int(date_to.strftime("%s"))
        
    if date_from is None:    
        date_from = date_to.replace(hour=0, minute=0, second=0) - timedelta(days=5)    
    range_from = int(date_from.strftime("%s"))

    query = {'created' : {'$gte' : range_from, '$lte' :  range_to}, 'sentiment' : sentiment}
    
    news_col = db['news'] 
    pipeline = [ {"$match": query},{"$group": {"_id": {'sentiment' : "$sentiment", 'created' : '$created'}, "count": {"$sum": 1} }  },{'$limit' : 5}, 
                {"$sort": SON([("count", -1), ("_id", -1), ('created', -1) ])}]
    results = list(news_col.aggregate(pipeline))
    frecuencies = ','.join([str(e['count']) for e in results])
    return frecuencies

def get_general_statistics(date_from=None, date_to=None):
    if date_to is None:
        date_to = datetime.now()
        date_to = date_to.replace(hour=23, minute=59, second=59)
    range_to = int(date_to.strftime("%s"))
        
    if date_from is None:    
        date_from = date_to.replace(hour=0, minute=0, second=0) - timedelta(days=5)    
    range_from = int(date_from.strftime("%s"))

    query = {'created' : {'$gte' : range_from, '$lte' :  range_to}}

    statistics = {}
    
    news_col = db['news']
    statistics['news'] = news_col.find(query).count()      

    cypher = graph.cypher

    cquery = 'MATCH (me:Person) RETURN COUNT(me) '
    cypher_result = cypher.execute(cquery, date_from=date_from, date_to=date_to)
    count_persons = cypher_result[0][0]

    cquery = 'MATCH (me:Organization) RETURN COUNT(me) '
    cypher_result = cypher.execute(cquery, date_from=date_from, date_to=date_to)
    count_organizations = cypher_result[0][0]
    statistics['actors'] = count_organizations + count_persons      

    cquery = 'MATCH (me:Source) RETURN COUNT(me) '
    cypher_result = cypher.execute(cquery, date_from=date_from, date_to=date_to)
    count_sources = cypher_result[0][0]
    statistics['sources'] = count_sources      
    
    cquery = 'MATCH (me:Location) RETURN COUNT(me) '
    cypher_result = cypher.execute(cquery, date_from=date_from, date_to=date_to)
    count_locations = cypher_result[0][0]
    statistics['locations'] = count_locations      

    return statistics



if __name__ == '__main__':

#     print(get_sentiment_frecuencies('neutral'))
    print(get_general_statistics())

#     results = most_important_actors('Person')
#     print results
#  
#     results = most_important_actors('Organization')
#     print results
#  
#     results = most_important_locations()
#     print results
#  
#     results = get_news(page_number=3)
#     print results
#  
#     results = get_news_by_actor('Person', 'Henrique Capriles')
#     print results
#          
#     results = get_actor('Person', 'Henrique Capriles')
#     print(json.dumps(results, sort_keys=True, indent=4, separators=(',', ': ')))
#  
#     results = get_actor('Organization', 'Empresas Polar')
#     print(json.dumps(results, sort_keys=True, indent=4, separators=(',', ': ')))
#  
#     results = get_location('Cuba')
#     print(json.dumps(results, sort_keys=True, indent=4, separators=(',', ': ')))
#   
#     results = get_source('http://www.elimpulso.com/feed')
#     print(json.dumps(results, sort_keys=True, indent=4, separators=(',', ': ')))
