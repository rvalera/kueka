from django.conf.urls import patterns, include, url
from django.contrib import admin
from views import *


urlpatterns = patterns('',
    url(r'^/all-news', rest_get_news, name='get_news'),    
    url(r'^/load-data', rest_load_data, name='load_data'),    

    url(r'^/actor/', rest_get_actor, name='get_actor'),    
    url(r'^/most-important-actors/', rest_most_important_actors, name='most_important_actors'),    
    url(r'^/news-by-actor', rest_get_news_by_actor, name='get_news_by_actor'),    

    url(r'^/source/', rest_get_source, name='get_source'),    
    url(r'^/most-important-sources/', rest_most_important_sources, name='most_important_sources'),    
    url(r'^/news-by-source/', rest_get_news_by_source, name='get_news_by_source'),    

    url(r'^/location/', rest_get_location, name='get_location'),    
    url(r'^/most-important-locations/', rest_most_important_locations, name='most_important_locations'),    
    url(r'^/news-by-location/', rest_get_news_by_location, name='get_news_by_location'),    
)

