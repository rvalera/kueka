from django.shortcuts import render,render_to_response

# Create your views here.
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render
from django.http import HttpResponseRedirect

import json
from frontend.analytics_services import most_important_locations, most_important_sources, most_important_actors,\
    get_actor, get_location, get_source, get_news, get_news_by_actor,\
    get_news_by_location, get_news_by_source, get_sentiment_frecuencies,\
    get_general_statistics

from frontend.load_services import load_data

    
def rest_load_data(request):
    context = RequestContext(request)
    if request.method == 'GET':
        if 'url' in request.GET and request.GET['url'] != None:
            url = request.GET['url']

            data = load_data(url)
            response = {}
            response['ok'] = True
            response['content'] = data
            return HttpResponse(json.dumps(response), content_type="application/json")    
        else:
            response = {}
            response['ok'] = 0
            response['message'] = 'Field url Not Found !!!'
            return HttpResponse(json.dumps(response), content_type="application/json")    
    else:
        response = {}
        response['ok'] = 0
        response['message'] = 'Get Method Not Supported!!!'
        return HttpResponse(json.dumps(response), content_type="application/json")    

def rest_get_actor(request):
    context = RequestContext(request)
    if request.method == 'GET':
        if 'type' in request.GET and 'name' in request.GET and request.GET['type'] != None and request.GET['name'] != None:
            type = request.GET['type']
            name = request.GET['name']
            data = get_actor(type,name)
            response = {}
            response['ok'] = True
            response['content'] = data
            return HttpResponse(json.dumps(response), content_type="application/json")    
        else:
            response = {}
            response['ok'] = 0
            response['message'] = 'Some Field Not Found (Type/Name) !!!'
            return HttpResponse(json.dumps(response), content_type="application/json")    
    else:
        response = {}
        response['ok'] = 0
        response['message'] = 'Get Method Not Supported!!!'
        return HttpResponse(json.dumps(response), content_type="application/json")    


def rest_most_important_actors(request):
    context = RequestContext(request)
    if request.method == 'GET':
        if 'type' in request.GET and request.GET['type'] != None:
            type = request.GET['type']
            data = most_important_actors(type)
            response = {}
            response['ok'] = True
            response['content'] = data
            return HttpResponse(json.dumps(response), content_type="application/json")    
        else:
            response = {}
            response['ok'] = 0
            response['message'] = 'Field Type Not Found!!!'
            return HttpResponse(json.dumps(response), content_type="application/json")    
    else:
        response = {}
        response['ok'] = 0
        response['message'] = 'Get Method Not Supported!!!'
        return HttpResponse(json.dumps(response), content_type="application/json")    

def rest_get_location(request):
    context = RequestContext(request)
    if request.method == 'GET':
        if 'name' in request.GET and request.GET['name'] != None:
            name = request.GET['name']
            data = get_location(name)
            response = {}
            response['ok'] = True
            response['content'] = data
            return HttpResponse(json.dumps(response), content_type="application/json")    
        else:
            response = {}
            response['ok'] = 0
            response['message'] = 'Name Field Not Found !!!'
            return HttpResponse(json.dumps(response), content_type="application/json")    
    else:
        response = {}
        response['ok'] = 0
        response['message'] = 'Get Method Not Supported!!!'
        return HttpResponse(json.dumps(response), content_type="application/json")    


def rest_most_important_locations(request):
    if request.method == 'GET':
        data = most_important_locations()
        response = {}
        response['ok'] = True
        response['content'] = data
        return HttpResponse(json.dumps(response), content_type="application/json")    
    else:
        response = {}
        response['ok'] = 0
        response['message'] = 'Get Method Not Supported!!!'
        return HttpResponse(json.dumps(response), content_type="application/json")    

def rest_get_source(request):
    context = RequestContext(request)
    if request.method == 'GET':
        if 'name' in request.GET and request.GET['name'] != None:
            name = request.GET['name']
            data = get_source(name)
            response = {}
            response['ok'] = True
            response['content'] = data
            return HttpResponse(json.dumps(response), content_type="application/json")    
        else:
            response = {}
            response['ok'] = 0
            response['message'] = 'Name Field Not Found !!!'
            return HttpResponse(json.dumps(response), content_type="application/json")    
    else:
        response = {}
        response['ok'] = 0
        response['message'] = 'Get Method Not Supported!!!'
        return HttpResponse(json.dumps(response), content_type="application/json")    

def rest_most_important_sources(request):
    if request.method == 'GET':
        data = most_important_sources()
        response = {}
        response['ok'] = True
        response['content'] = data
        return HttpResponse(json.dumps(response), content_type="application/json")    
    else:
        response = {}
        response['ok'] = 0
        response['message'] = 'Get Method Not Supported!!!'
        return HttpResponse(json.dumps(response), content_type="application/json")    

def rest_get_news(request):
    context = RequestContext(request)
    if request.method == 'GET':
        page_number = 0
        page_size = 10        
        if 'page_number' in request.GET :
            page_number = int(request.GET['page_number'])
        if 'page_size' in request.GET:
            page_size = int(request.GET['page_size'])
        data = get_news(page_number = page_number, page_size = page_size)
        response = {}
        response['ok'] = True
        response['content'] = data
        return HttpResponse(json.dumps(response), content_type="application/json")    
    else:
        response = {}
        response['ok'] = 0
        response['message'] = 'Get Method Not Supported!!!'
        return HttpResponse(json.dumps(response), content_type="application/json")    

def rest_get_news_by_actor(request):
    context = RequestContext(request)
    if request.method == 'GET':
        if 'type' in request.GET and 'name' in request.GET and request.GET['type'] != None and request.GET['name'] != None:
            type = request.GET['type']
            name = request.GET['name']

            page_number = 0
            page_size = 10        
            if 'page_number' in request.GET :
                page_number = int(request.GET['page_number'])
            if 'page_size' in request.GET:
                page_size = int(request.GET['page_size'])

            
            data = get_news_by_actor(type,name,page_number = page_number, page_size = page_size)
            response = {}
            response['ok'] = True
            response['content'] = data
            return HttpResponse(json.dumps(response), content_type="application/json")    
        else:
            response = {}
            response['ok'] = 0
            response['message'] = 'Some Field Not Found (Type/Name) !!!'
            return HttpResponse(json.dumps(response), content_type="application/json")    
    else:
        response = {}
        response['ok'] = 0
        response['message'] = 'Get Method Not Supported!!!'
        return HttpResponse(json.dumps(response), content_type="application/json")    

def rest_get_news_by_location(request):
    context = RequestContext(request)
    if request.method == 'GET':
        if 'name' in request.GET and request.GET['name'] != None:
            name = request.GET['name']
            
            page_number = 0
            page_size = 10        
            if 'page_number' in request.GET :
                page_number = int(request.GET['page_number'])
            if 'page_size' in request.GET:
                page_size = int(request.GET['page_size'])
            
            data = get_news_by_location(name,page_number = page_number, page_size = page_size)
            response = {}
            response['ok'] = True
            response['content'] = data
            return HttpResponse(json.dumps(response), content_type="application/json")    
        else:
            response = {}
            response['ok'] = 0
            response['message'] = 'Name Field Not Found !!!'
            return HttpResponse(json.dumps(response), content_type="application/json")    
    else:
        response = {}
        response['ok'] = 0
        response['message'] = 'Get Method Not Supported!!!'
        return HttpResponse(json.dumps(response), content_type="application/json")    

def rest_get_news_by_source(request):
    context = RequestContext(request)
    if request.method == 'GET':
        if 'name' in request.GET and request.GET['name'] != None:
            name = request.GET['name']

            page_number = 0
            page_size = 10        
            if 'page_number' in request.GET :
                page_number = int(request.GET['page_number'])
            if 'page_size' in request.GET:
                page_size = int(request.GET['page_size'])

            data = get_news_by_source(name,page_number = page_number, page_size = page_size)
            response = {}
            response['ok'] = True
            response['content'] = data
            return HttpResponse(json.dumps(response), content_type="application/json")    
        else:
            response = {}
            response['ok'] = 0
            response['message'] = 'Name Field Not Found !!!'
            return HttpResponse(json.dumps(response), content_type="application/json")    
    else:
        response = {}
        response['ok'] = 0
        response['message'] = 'Get Method Not Supported!!!'
        return HttpResponse(json.dumps(response), content_type="application/json")    

def index(request):
    data = {}
    data['sentiments'] = {}
    data['sentiments']['positive'] = get_sentiment_frecuencies('positive')
    data['sentiments']['neutral'] = get_sentiment_frecuencies('neutral')
    data['sentiments']['negative'] = get_sentiment_frecuencies('negative')

    data.update(get_general_statistics())

    return render_to_response('index.html', data, context_instance=RequestContext(request))

def view_actor(request):
    context = RequestContext(request)
    if request.method == 'GET':
        if 'type' in request.GET and 'name' in request.GET and request.GET['type'] != None and request.GET['name'] != None:
            type = request.GET['type']
            name = request.GET['name']
            data = {'type' : type, 'name' : name}
            return render_to_response('actor.html', data, context_instance=RequestContext(request))
        else:
            data = {}
            data['ok'] = 0
            data['message'] = 'Some Field Not Found (Type/Name) !!!'
            return render_to_response('error.html', data, context_instance=RequestContext(request))
    else:
        data = {}
        data['ok'] = 0
        data['message'] = 'Get Method Not Supported!!!'
        return render_to_response('error.html', data, context_instance=RequestContext(request))

def view_location(request):
    context = RequestContext(request)
    if request.method == 'GET':
        if 'name' in request.GET and request.GET['name'] != None:
            name = request.GET['name']
            data = {'name' : name}
            return render_to_response('location.html', data, context_instance=RequestContext(request))
        else:
            data = {}
            data['ok'] = 0
            data['message'] = 'Field Name Not Found !!!'
            return render_to_response('error.html', data, context_instance=RequestContext(request))
    else:
        data = {}
        data['ok'] = 0
        data['message'] = 'Get Method Not Supported!!!'
        return render_to_response('error.html', data, context_instance=RequestContext(request))

def view_source(request):
    context = RequestContext(request)
    if request.method == 'GET':
        if 'name' in request.GET and request.GET['name'] != None:
            name = request.GET['name']
            data = {'name' : name}
            return render_to_response('source.html', data, context_instance=RequestContext(request))
        else:
            data = {}
            data['ok'] = 0
            data['message'] = 'Field Name Not Found !!!'
            return render_to_response('error.html', data, context_instance=RequestContext(request))
    else:
        data = {}
        data['ok'] = 0
        data['message'] = 'Get Method Not Supported!!!'
        return render_to_response('error.html', data, context_instance=RequestContext(request))
