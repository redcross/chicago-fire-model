/* Copyright © 2017 American Red Cross
 * 
 * Permission is hereby granted, free of charge, to any person
 * obtaining a copy of this software and associated documentation
 * files (the “Software”), to deal in the Software without
 * restriction, including without limitation the rights to use,
 * copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the
 * Software is furnished to do so, subject to the following
 * conditions:
 * 
 * The above copyright notice and this permission notice shall be
 * included in all copies or substantial portions of the Software.
 * 
 * THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND,
 * EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
 * OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 * NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
 * HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
 * WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 * FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
 * OTHER DEALINGS IN THE SOFTWARE.
 */

// Configure map settings and set initial lat, lng, and zoom levels.
var map = L.map('map', {
  doubleClickZoom: false,
  minZoom: 11,
  maxZoom: 17
});
var mapinit = {
  lat: 41.84,
  lng: -87.66,
  zoom: 11
};

// Creating new panes and setting the z-index allow neighborhood polygons to
// sit below census tracts and labels to be visible over other layers.
map.createPane('labelPane');
map.getPane('labelPane').style.zIndex = 550;
map.createPane('neighborhoods');
map.getPane('neighborhoods').style.zIndex = 500;


// Map layer variables
var risk_breaks = [.0125, .0250, .0375, .0500, 1]; // Risk level buckets
var risk_levels = ["Very Low", "Low", "Moderate", "High", "Very High"]; // Risk level labels
var response_breaks = [1, 2, 3, 4, 5]; // Red Cross response buckets
var palResponse = ['#f2f0f7','#dadaeb','#bcbddc','#9e9ac8','#756bb1','#54278f']; // Red Cross response hues
var pal = ['#2c7bb6','#abd9e9','#ffffbf','#fdae61','#d7191c']; // Risk level hues
var palResponseText = ['#82AFC9', '#B8DBE5', '#FCFCC0', '#F8D1AB', '#E49490']; // Risk level label hues


// Other variables
var marker;
var layerRisk;
var layerResponse;
var currentLayer;

// Render the map tiles
function drawMap(lat, lng, zm) {
  var tilesURL = 'https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_nolabels/{z}/{x}/{y}.png';
  var labelsURL = 'https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_only_labels/{z}/{x}/{y}.png';
  var tilesAttrib = '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> | &copy; <a href="http://cartodb.com/attributions">CartoDB</a>';

  var tiles = new L.TileLayer(tilesURL, {
    attribution: tilesAttrib
  }).addTo(map);
  var labels = new L.TileLayer(labelsURL, {
    pane: 'labelPane'
  }).addTo(map);
  map.setView(new L.LatLng(lat, lng), zm);
};

// Default census tract polygon style
function styleRisk(feature) {
  return {
    weight: .3,
    color: getColor(feature.properties.fire_score, risk_breaks),
    fillColor: getColor(feature.properties.fire_score, risk_breaks),
    opacity: 0.5,
    fillOpacity: 0.5
  }
};

// Style for Red Cross response polygons
function styleResponse(feature) {
  return {
    weight: .3,
    color: getColorResponse(feature.properties.responses_per_tract, response_breaks),
    fillColor: getColorResponse(feature.properties.responses_per_tract, response_breaks),
    opacity: 0.5,
    fillOpacity: 0.5
  }
};

// Style for neighborhood boundary polygons
function styleNeighborhood(feature) {
  return {
    weight: 1.5,
    color: 'gray',
    opacity: .5,
    fillOpacity: 0
  }
};


// Mapping risk score to fill color
function getColor(d, breaks) {
  return d < breaks[0] ? pal[0] :
         d < breaks[1] ? pal[1] :
         d < breaks[2] ? pal[2] :
         d < breaks[3] ? pal[3] :
                         pal[4];
}

// Mapping number of responses to fill color
function getColorResponse(d, breaks) {
  return d < breaks[0] ? palResponse[0] :
         d < breaks[1] ? palResponse[1] :
         d < breaks[2] ? palResponse[2] :
         d < breaks[3] ? palResponse[3] :
                         palResponse[4];
}

// Mapping risk level to risk label background color
function getColorText(d, breaks) {
  return d < breaks[0] ? palResponseText[0] :
         d < breaks[1] ? palResponseText[1] :
         d < breaks[2] ? palResponseText[2] :
         d < breaks[3] ? palResponseText[3] :
                         palResponseText[4];
}

// Converts risk score to risk level
function getRiskLevel(d) {
  return d < risk_breaks[0] ? risk_levels[0] :
         d < risk_breaks[1] ? risk_levels[1] :
         d < risk_breaks[2] ? risk_levels[2] :
         d < risk_breaks[3] ? risk_levels[3] :
                              risk_levels[4];
}

// Add geojson, risk score, and response data to the map
// The layerControl allows users to toggle between risk levels and Red Cross
// responses.
function addDataToMap(data, map) {
  layerRisk = L.geoJson(data, {
    style: styleRisk
  });
  layerResponse = L.geoJson(data, {
    style: styleResponse
  });
  currentLayer = layerRisk;
  layerRisk.addTo(map);
  legendRisk.addTo(map);
  var baselayers = {
    "Risk Level": layerRisk,
    "Red Cross Responses": layerResponse
  };

  layerControl = L.control.layers(baselayers).setPosition('topleft');
  layerControl.addTo(map);
}


// Draw the map with the initial location settings
drawMap(mapinit.lat, mapinit.lng, mapinit.zoom);

// Load cesnsus tract geojson data and add to map
$.getJSON("resources/data/tract_fire_scores_responses.geojson", function(data) { addDataToMap(data, map); });

// Load neighborhood boundary geojson files and add to map
$.getJSON("resources/data/Neighborhoods_2012b.geojson", function(data) {
  function resetHighlight(e) {
    layerNeighborhoods.resetStyle(e.target);
  }
  // Set hover effects for neighborhood boundaries
  function highlightFeature(e) {
    var layer = e.target;
    layer.setStyle({
      weight: 2,
      opacity: 1,
      color: 'black'
    });
    if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
      layer.bringToFront();
    }
  }

  function onEachFeature(feature, layer) {
    layer.on({
      mouseover: highlightFeature,
      mouseout: resetHighlight,
    });
  }
  layerNeighborhoods = L.geoJson(data, {
    pane: 'neighborhoods',
    style: styleNeighborhood,
    onEachFeature: onEachFeature
  });
  layerNeighborhoods.addTo(map);
});




// The info box: This is where risk levels for a census track will be displayed
var infoRisk = L.control();
infoRisk.onAdd = function (map) {
  this._div = L.DomUtil.create('div', 'info'); // create a div with a class "info"
  L.DomEvent.disableClickPropagation(this._div);
  return this._div;
};
infoRisk.update = function (props, nprops) {  // updates the info box
  var neighborhood;
  if (nprops) {
    neighborhood = nprops.PRI_NEIGH;
  } else {
    neighborhood = "Chicago"
  }

  this._div.innerHTML = (props ?
      '<h3>' + neighborhood + '</h3>' +
      'The risk level for this area of ' + neighborhood + ' is<br/><br/>' +
      '<div class="score" style="background-color:' + getColorText(props.fire_score, risk_breaks) + '">' +
      getRiskLevel(props.fire_score).toUpperCase() + '</div><br/>' +
      'Fire risk levels are based the number of the vacant housing units, median housing value, and a number of other factors.</br></br>' +
      'A working smoke alarm is the first step in keeping your home safe.</br></br>' +
      '<b><a href=https://getasmokealarm.org/ target="_blank">Contact the Red Cross about installing new smoke alarms in your home.</a></b>' +
      '<br/><br/>'
      : 'Sorry, we couldn\'t find this address.<br/><br/>Please try a different address, or click on the map to get your risk score.'
    );
};



// Title card: This is where the app title, intro text, and address search bar are found.
var searchbar = L.control();
searchbar.onAdd = function(map) {
  this._div = L.DomUtil.create('div', 'info');
  L.DomEvent.disableClickPropagation(this._div);
  this.update();
  return this._div;
};
searchbar.update = function() {
  this._div.innerHTML = '<h2>Red Cross Fire Risk Finder</h2>' +
      'From 2013-2017 there were over 26,000 reported fires across Cook County. ' +
      'Some areas of Chicago remain more susceptible to fires than others.<br/><br/>' +
      '<span class="instructions">Click on the map or search for an address to see your neighborhood\'s fire risk score.</span><br/><br/>' +
      '<input id="post" type="text" placeholder="600 W Chicago Ave";"/><br/><br/>'
      ;
};
searchbar.addTo(map);


// Listener for the address search bar
$("#post").focus(function() {
  $(this).data("hasfocus", true);
});
$("#post").blur(function() {
  $(this).data("hasfocus", false);
});
$(document.body).keyup(function(ev) {
  if (ev.which === 13 && $("#post").data("hasfocus")) {
    setAddress(document.getElementById("post").value);
  }
});



// Set the risk level legend
var legendRisk = L.control({position: 'bottomright'});
legendRisk.onAdd = function (map) {
    var div = L.DomUtil.create('div', 'info legend');
    div.innerHTML += '<b>Risk Level</b><br/>';
    // loop through intervals and generate a label with a colored square for each interval
    for (var i = 0; i < risk_breaks.length; i++) {
        div.innerHTML +=
            '<i style="background:' + getColor(risk_breaks[i] - .01, risk_breaks) + '"></i> ' +
            risk_levels[i] + (risk_breaks[i + 1] ? '<br>' : ' ');
    }
    return div;
};

// Set the Red Cross response legend
var legendResponse = L.control({position: 'bottomright'});
legendResponse.onAdd = function (map) {
    var div = L.DomUtil.create('div', 'info legend');
    div.innerHTML += '<b>Red Cross Responses</b><br/>';
    // loop through intervals and generate a label with a colored square for each interval
    for (var i = 0; i < response_breaks.length; i++) {
        div.innerHTML +=
            '<i style="background:' + getColorResponse(response_breaks[i] - .01, response_breaks) + '"></i> ' +
            response_breaks[i] + (response_breaks[i + 1] ? '<br>' : '+');
    }
    return div;
};



// API call for the US Census Geocoder
// Returns geographic data for a given address, including the lat/lng coordinates.
httpRequestGeocoder = function(url){
  return new Promise(function(resolve, reject) {
    var xhttp = new XMLHttpRequest();
    xhttp.open("GET", url, true);
    xhttp.onreadystatechange = function() {
      address_check = JSON.parse(this.response)["result"]["addressMatches"].length > 0;
      if (this.status === 200 & address_check) {
        resolve(this.response);
      } else {
        if (marker) {
          map.removeLayer(marker);
        }
        infoRisk.addTo(map);
        infoRisk.update();
        reject(new Error("geocoding failed"));
      }
    };
    xhttp.send();
  });
}

// Redraw the map to focus on the searched address
// Parse the response from the Geocoder API, recenter the map, and update the
// info box.
setAddress = function(a){
  var geocodeUrl = "https://geocoding.geo.census.gov/geocoder/geographies/address?street=";
  var geoq = "&city=Chicago&state=IL&benchmark=Public_AR_Census2010&vintage=Census2010_Census2010&layers=14&format=json";
  var proxyurl = "https://cors-anywhere.herokuapp.com/"; // allows for cross-origin requests
  var geourl = proxyurl + geocodeUrl + a.replace("#", "").replace(/ /g, "+") + geoq;

  httpRequestGeocoder(geourl).then(function(data){
    try {
      slat = JSON.parse(data)["result"]["addressMatches"][0]["coordinates"]["y"];
      slng = JSON.parse(data)["result"]["addressMatches"][0]["coordinates"]["x"];
    } catch(e) {
    }

    drawMap(slat, slng, 14);

    if (marker) {
      map.removeLayer(marker);
    }
    marker = L.marker([slat, slng]).addTo(map);

    // Find which polygon the marker falls in,
    // and change the style and update the info box.
    var lidc = leafletPip.pointInLayer([slng, slat], layerRisk)[0]._leaflet_id;
    var lidn = leafletPip.pointInLayer([slng, slat], layerNeighborhoods)[0]._leaflet_id;

    var layer_tract = layerRisk._layers[lidc];
    var layer_neigh = layerNeighborhoods._layers[lidn];

    infoRisk.addTo(map);
    infoRisk.update(layer_tract.feature.properties, layer_neigh.feature.properties);

  }).catch(function(err){
    console.log("error", err);
  });
}

// Update the marker and info box in response to user clicks
function clickHandler(e) {
  var lidc, lidn, layer_tract, layer_neigh;

  if (marker) {
    map.removeLayer(marker);
  }
  if (infoRisk._map) {
    infoRisk.remove();
  }

  try {
    lidc = leafletPip.pointInLayer([e.latlng.lng, e.latlng.lat], layerRisk)[0]._leaflet_id;
    props_tract = layerRisk._layers[lidc].feature.properties;
  } catch (e) {
    props_tract = undefined;
  }

  try {
    lidn = leafletPip.pointInLayer([e.latlng.lng, e.latlng.lat], layerNeighborhoods)[0]._leaflet_id;
    props_neigh = layerNeighborhoods._layers[lidn].feature.properties;
  } catch (e) {
    props_neigh = undefined;
  }

  if(lidc){
    marker = L.marker([e.latlng.lat, e.latlng.lng]).addTo(map);
    infoRisk.addTo(map);
    infoRisk.update(props_tract, props_neigh);
  }

  document.getElementById("post").value = ""

}

map.on("click", clickHandler);

// Toggle legend and polygon colors between risk levels and Red Cross responses.
map.on('baselayerchange', function(eventLayer){
  if (eventLayer.name === 'Risk Level') {
    this.removeControl(legendResponse);
    this.removeLayer(layerResponse);
    layerRisk.addTo(this);
    legendRisk.addTo(this);
    currentLayer = layerRisk;
  } else {
    this.removeControl(legendRisk);
    this.removeControl(infoRisk);
    this.removeLayer(layerRisk);
    layerResponse.addTo(this);
    legendResponse.addTo(this);
    currentLayer = layerResponse;
  }
});

// Add Uptake watermark
L.Control.Watermark = L.Control.extend({
  onAdd: function(map) {
    var img = L.DomUtil.create('img');
		img.src = 'resources/images/Powered-by_Uptake-org.png';
		img.style.width = '150px';
		return img;
  },

	onRemove: function(map) {
		// Nothing to do here
	}
});

L.control.watermark = function(opts) {
  return new L.Control.Watermark(opts);
}

L.control.watermark({ position: 'bottomleft' }).addTo(map);
