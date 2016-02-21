from fake_useragent.fake import UserAgent
import feedparser
from kueka.settings import mc, graph,\
    db, OPENSTREETMAP_USER, alchemyapi
from slugify import slugify
from py2neo.core import Graph, Relationship
from datetime import datetime
from traceback import print_exc
import requests
import json
import time
from newspaper import Config
from newspaper.article import Article

# Function to return the urls of news thrown for a particular RSS address
def extract_news_from_rss(url):
    feeds = []
    ua = UserAgent()
    
    d = feedparser.parse(url,agent=ua.chrome)

    print('Executing feedparser -> %s ' % len(d.entries))

    for entry in d.entries:
        link = entry.link
        slug = slugify(entry.title)

        obj_datetime = datetime.now()
        obj_datetime = obj_datetime.replace(hour=0, minute=0, second=0)
        now = time.mktime(obj_datetime.timetuple())
        
        feeds.append({'title' : entry.title,'slug' : slug ,'url' : link, 'description' : entry.description, 'source' : url, 'created' : now })

    return feeds

def get_static_content():
    content = {}
    content['language'] = ''
    content['text'] = ''
    content['image'] = ''
    content['videos'] = []
    return content

def extract_content(url):
    content = {}
    content = get_static_content()
    try:
        ua = UserAgent()
    
        config = Config()
        config.browser_user_agent = ua.chrome
        config.language = 'es'
        
        article = Article(url, config= config)
         
        article.download()    
     
        article.parse()    
        
        text = article.text
        content['text'] = text
        
        top_image = article.top_image
        content['image'] = top_image

        movielinks = []
        for movie in article.movies:
            movielinks.append(movie)
        content['videos'] = movielinks

    except Exception as e:
        print_exc(e)
    
    return content

def get_static_entities():
    entities = {}
    entities['person'] = ['Nicolas Maduro','John Kerry','Henrique Capriles']
    entities['organization'] = ['Empresas Polar','Cardenales de Lara']
    entities['location'] = ['Venezuela','Cuba','USA','California']
    
    return entities

def extract_entities(url):
    entities = {}
#     entities =  get_static_entities()
    entities =  get_static_entities()
    try:
        alchemy_entities = alchemyapi.entities('url',url)
        entities = {}
        for entity in alchemy_entities['entities']:
             
            entity_type = entity['type']
            if entity_type in ['CityTown','Country','City','Island','Kingdom','Location','Region','StateOrCounty','USCounty','USState','Facility']:
                entity_type = 'location'
             
            entity_type = entity_type.lower()
     
            if not entity_type in entities:
                entities[entity_type] = []
 
            entities[entity_type].append(entity['text'])
 
 
    except Exception as e:
        print_exc(e)

    return entities


def eval_geoloc(locations):
    valid_location = None

    for l in locations:
        if l['importance'] > 0.60:
            valid_location = {} 
            valid_location['longitude'] = float(l['lon'])
            valid_location['latitude'] = float(l['lat'])
            valid_location['display_name'] = l['display_name'] 
            valid_location['category'] = l['category'] 
            valid_location['type'] = l['type'] 
            valid_location['importance'] = l['importance'] 
            break;
            
    return valid_location    


def get_geoloc(text_location):
    definitive_location = None

    slug_location = slugify('loc_%s' % text_location.decode('utf8'))
    if (mc.get(slug_location) != None):
        definitive_location = mc.get(slug_location)
    else:
        data = {}
        data['q'] = text_location
        data['format'] = 'jsonv2'
        data['email'] = OPENSTREETMAP_USER

        locations = requests.get("http://nominatim.openstreetmap.org/search", params=data)
        result = locations.json() 
    
        definitive_location = eval_geoloc(result)
        if not definitive_location is None:
            definitive_location['name'] = text_location
            mc[slug_location] = definitive_location

    return definitive_location
 


def extract_geographic_locations(locations):
    data = {}
    try:
        data['geolocation'] = []
        for location in locations:
            geographic_data = get_geoloc(location)
            if not geographic_data is None and 'latitude' in geographic_data and 'longitude' in geographic_data: 
                data['geolocation'].append(geographic_data)
    except Exception as e:
        print_exc(e)
    return data

def extract_sentiment(url):
    data = {}
    data['sentiment'] = 'neutral'
    try:
        alchemy_result = alchemyapi.sentiment('url',url)
        if 'docSentiment' in alchemy_result:
            sentiment = alchemy_result['docSentiment']['type']
            data['sentiment'] = sentiment.lower()
    except Exception as e:
        print_exc(e)
    return data

def analize_news(list_news):
    for index,news in enumerate(list_news):
        analyzed = news
        
        text_info =  extract_content(analyzed['url'])
        if 'text' in text_info:
            analyzed.update(text_info)
            
            entities  =  extract_entities(analyzed['url'])
            analyzed.update(entities)

            if 'location' in analyzed:
                locations = extract_geographic_locations(analyzed['location'])
                analyzed.update(locations)

            entities  =  extract_sentiment(analyzed['url'])
            analyzed.update(entities)
            
            list_news[index] = analyzed

    return list_news

    
def store_analized_news(list_news):        
    news_col = db['news'] 
    for index,news in enumerate(list_news):
        qry = {'slug' : news['slug']}
        count = news_col.find(qry).count()
        if (count == 0):
            result = news_col.insert(news)
            news['id'] = result
        else:
            del(list_news[index])
        

def get_news_node(entity_news):
    news = graph.find_one("News", "title", entity_news['slug']) 
    return news

def create_news_node(entity_news):
    news = graph.merge_one("News", "title", entity_news['slug'])        
    news['id'] = str(entity_news['id'])
    news['url'] = entity_news['url']
    news['slug'] = entity_news['slug']
    news['sentiment'] = entity_news['sentiment'] if 'sentiment' in entity_news else ''
    news['created'] = datetime.now()
    news.push()
    return news

def get_tag_node(tagname,tagvalue):
    tag = graph.find_one(tagname, "name", tagvalue) 
    return tag

def create_tag_node(tagname,tagvalue):
    tag = graph.merge_one(tagname, "name", tagvalue)        
    tag.push()
    return tag

def get_or_create_tag_node(tagname,tagvalue):
    tag = get_tag_node(tagname,tagvalue) 
    if (tag is None):
        tag = create_tag_node(tagname,tagvalue)
    return tag

def create_tags_to_news(news,tagname,tags):
    for tagvalue in tags:
        tag = get_or_create_tag_node(tagname,tagvalue) 
        relationship = Relationship(news, "TAGGED", tag)
        graph.create_unique(relationship)        

def create_location_node(entity_location):
    location_node = graph.merge_one("Location", "name", entity_location['name'])        
    location_node['latitude'] = entity_location['latitude']
    location_node['longitude'] = entity_location['longitude']
    location_node.push()
    return location_node

def get_location_node(entity_location):
    location_node = graph.find_one('Location', "name", entity_location['name']) 
    return location_node


def get_or_create_location_node(location):
    location_node = get_location_node(location) 
    if (location_node is None):
        location_node = create_location_node(location)
        
    return location_node

def create_location_to_news(news,locations):
    for location in locations:
        tag = get_or_create_location_node(location) 
        relationship = Relationship(news, "LOCATED", tag)
        graph.create_unique(relationship)        

def get_source_node(url):
    source = graph.find_one('Source', "name", url) 
    return source

def create_source_node(url):
    source = graph.merge_one('Source', "name", url)        
    source.push()
    return source

def get_or_create_source_node(source):
    source_node = get_source_node(source) 
    if (source_node is None):
        source_node = create_source_node(source)
    return source_node

def create_source_to_news(news,url):
    source = get_or_create_source_node(url) 
    relationship = Relationship(news, "CREATED", source)
    graph.create_unique(relationship)

def create_graph_onenews(entity_news):
    news = get_news_node(entity_news)
    if news is None:
        news = create_news_node(entity_news)
        create_source_to_news(news,entity_news['source'])
        if 'person' in entity_news and len(entity_news['person']) > 0:
            create_tags_to_news(news,'Person',entity_news['person'])
        if 'organization' in entity_news and  len(entity_news['organization']) > 0:
            create_tags_to_news(news,'Organization',entity_news['organization'])
        if 'location' in entity_news and len(entity_news['location']) > 0:
            create_location_to_news(news,entity_news['geolocation'])
        
def generate_graph_news(list_news):
    for news in list_news:
        create_graph_onenews(news)

def load_data(url):
    process_result = {}
    try:
        list_news = extract_news_from_rss(url)
        analyzed_news = analize_news(list_news)
    #     print(json.dumps(analyzed_news, sort_keys=True, indent=4, separators=(',', ': ')))
        store_analized_news(analyzed_news)
        generate_graph_news(analyzed_news)
        process_result['processed_news'] = len(analyzed_news)
    except Exception as e:
        print_exc(e)    
        process_result['processed_news'] = 0

    return process_result
        
if __name__ == '__main__':
    load_data('http://www.elimpulso.com/feed')