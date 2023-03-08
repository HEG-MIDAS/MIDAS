sourcesMap = ["climacity", "sabra", "vhg"];
stationsMap = [];
parametersMap = [];

const bsCollapse = new bootstrap.Collapse('#collapseWidthExample', {
    toggle: false
})

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);

var greenIcon = new L.Icon({
    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
});

var blueIcon = new L.Icon({
    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
});


//////////////////////////////////////////////////////////////////////////////////////
// Customising classes
//////////////////////////////////////////////////////////////////////////////////////

const customMarker = L.Marker.extend({
    options: { 
        station: '',
        stationSlug: '',
        source: '',
        sourceSlug: '',
        parameters_list: '',
    }
});

const customCircle = L.Circle.extend({
    options: { 
        station: '',
        stationSlug: '',
        source: '',
        sourceSlug: '',
        parameters_list: '',
    }
});

function toggleButtonCollapse(){
    bsCollapse.toggle();
}

options = {'sources': sourcesMap};
const stations_results = requestStationsSimplified(options);

function manageMapMenu(form=false, options=null, parameters_data=null){
    const stationsNode = document.getElementById("burger-map-stations");
    const burgerExpanded = document.getElementById("buttonBurger");
    // If the function was called by clicking on the burger, displays the current information
    if (!form){
        
        // if (burgerExpanded.ariaExpanded == "true"){
        //     bsCollapse.hide();
        // }
        // If there is stations selected will work on display
        if (stationsMap.length > 0){
            stationsNode.innerHTML = 'test'
        }
        stationsNode.innerHTML = 'test'
        bsCollapse.show();
    }
    else{
        stationsNode.innerHTML = 'BWAAAAAH'

        // Open menu
        
        bsCollapse.show();
    }
}

async function openSelectionMenu() {
    options = {
        'sources': sourcesMap,
        'stations': [this.options.stationSlug]
    }
    try {
        const parameters_data = await requestParametersSimplified(options);
        manageMapMenu(true, options, parameters_data)
    }
    catch(err){
        console.log(err);
    }
}

function addingMarker2Map(latitude, longitude, stationName, slug) {
    var marker = new customMarker([parseFloat(latitude), parseFloat(longitude)], { 
        station: stationName,
        stationSlug: slug
        });
    marker.addTo(map).on("click", openSelectionMenu);
}

function addingCircle2Map(latitude, longitude, stationName, slug) {
    new customCircle([parseFloat(latitude), parseFloat(longitude)], 600, options = {
        station: stationName,
        stationSlug: slug
    }).addTo(map).on("click", openSelectionMenu);
}

async function setUpStationsOnMap(){
    try {
        const stations_data = await stations_results;
        console.log(stations_data);
        for (let i = 0; i < stations_data.length; i++) {
            if (stations_data[i]['coordinates_exact']){
                addingMarker2Map(stations_data[i]['latitude'], stations_data[i]['longitude'], stations_data[i]['name'], stations_data[i]['slug'])
            }
            else {
                addingCircle2Map(stations_data[i]['latitude'], stations_data[i]['longitude'], stations_data[i]['name'], stations_data[i]['slug'])
            }
        }
    }
    catch(err){
        console.log(err);
    }
}

setUpStationsOnMap();





