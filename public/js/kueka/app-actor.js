var map;
var myCenter = new google.maps.LatLng(10.068248347064115, -69.34201776981354);
var markers = [];

function KuekaVM() {
	var self = this;

	self.top5_news = ko.observableArray();
	self.news = ko.observableArray();

	loadAll = function() {
		drawMap();
		loadNews();
	}
	
	loadNews = function() {

		$.ajax({
			//async : false,
			url : 'news-by-actor/',
			dataType : "json",
			data : {
				type : type,
				name : name,
				page_size : 20
			},
			beforeSend : function() {
			},
			success : function(data) {
				index = 0;
				data.content.content.forEach(function (element) {
					element.geolocation.forEach(function (location) {
						addMarker(location.latitude,location.longitude,element);
					});
					ko_element = ko.mapping.fromJS(element);
					self.news.push(ko_element);
					if (index  < 5) {
						self.top5_news.push(ko_element);
						index++;
					}
	                showMarkers();
				});	
			}
		});
		
	}
	
	/***** MAP HANDLE *****/
    drawMap = function() {
		
		if (map == null) {

			var mapProp = {
					center : myCenter,
					zoom : 3,
					zoomControl: true,
					mapTypeId : google.maps.MapTypeId.ROADMAP,
					zoomControlOptions: {
						style: google.maps.ZoomControlStyle.SMALL
					},
					streetViewControl: false
				};

				map = new google.maps.Map(document.getElementById("googleMap"), mapProp);

				google.maps.event.addDomListener(window, "resize", function() {
					 var center = map.getCenter();
					 google.maps.event.trigger(map, "resize");
					 map.setCenter(center); 
				});
				
				
			    showMarkers();
			    resizeMap();
			    setCenter();

		}
		
	}

     function resizeMap() {
     	google.maps.event.trigger(map, 'resize');
     }

     function addMarker(x,y,post) {

    	 html_text = '<div><h3 class="popover-title" style="padding-right: 0px; background-color: white; padding-left: 0px;">'+
			'<b>'+post.title+'</b></h3>'+
			'<p><small>'+post.description+'</small> <br/>' +
			'<a class="product-title" target="_blank" href="'+post.url+'"  >Go to ...</span></a>';    	 
    	 
     	var infowindow = new google.maps.InfoWindow({
     		content: html_text
     	});

     	var marker = new google.maps.Marker({
     		position : new google.maps.LatLng(x,y),
     		map : map,
     		animation : google.maps.Animation.DROP, 
     		cursor:"pointer",	
     	    title: post.title
     	});

     	marker.addListener('click', function() {
     		infowindow.open(map, marker);
     	});     	
     	
     	markers.push(marker);

     }

     // Sets the map on all markers in the array.
     function setAllMap(map) {
     	for (var i = 0; i < markers.length; i++) {
     		markers[i].setMap(map);
     	}
     }

     // Shows any markers currently in the array.
     function showMarkers() {
     	setAllMap(map);
     }

     function setCenter() {
     	if (navigator.geolocation) {
     		navigator.geolocation.getCurrentPosition(function(position) {
     			var pos = new google.maps.LatLng(position.coords.latitude,
     					position.coords.longitude);

     			var infowindow = new google.maps.InfoWindow({
     				map : map,
     				position : pos,
     				content : 'Your location.'
     			});

     			map.setCenter(pos);
     		}, function() {
     			handleNoGeolocation(true);
     		});
     	} else {
     		// Browser doesn't support Geolocation
     		handleNoGeolocation(false);
     	}
     }

     function handleNoGeolocation(errorFlag) {
     	if (errorFlag) {
     		var content = 'Error: The Geolocation service failed.';
     	} else {
     		var content = 'Error: Your browser doesn\'t support geolocation.';
     	}
     }

}

kuekaVM = KuekaVM()
ko.applyBindings(kuekaVM);