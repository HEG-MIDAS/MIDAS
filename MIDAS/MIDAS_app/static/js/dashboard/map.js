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
        icon: blueIcon,
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

function triggerParameterButton(){
    
}

function toggleButtonCollapse(){
    bsCollapse.toggle();
}

options = {'sources': sourcesMap};
const stations_results = requestStationsSimplified(options);

function manageMapMenu(form=false, currentMarker=null, parameters_data=null){
    const stationsNode = document.getElementById("burger-map-stations");
    const parametersNode = document.getElementById("burger-map-parameters");
    const burgerExpanded = document.getElementById("buttonBurger");

    stationsNode.innerHTML = '';

    // If the function was called by clicking on the burger, displays the current information
    if (!form){
        
        // if (burgerExpanded.ariaExpanded == "true"){
        //     bsCollapse.hide();
        // }
        // If there is stations selected will work on display
        if (stationsMap.length > 0){
            stationsNode.innerHTML = 'test'
        }
        else{
            stationsNode.innerHTML = 'Aucune station sélectionnée'
            parametersNode.innerHTML = 'Aucun paramètre sélectionné'
        }
        bsCollapse.show();
    }
    else{
        let btnStation = document.createElement("span");
        btnStation.innerHTML = currentMarker.options.station;
        btnStation.classList.add('badge', 'bg-primary');
        stationsNode.appendChild(btnStation);

        for (let i = 0; i < parameters_data.length; i++) {
            let btnParameter = document.createElement("button");
            btnParameter.innerHTML = parameters_data[i].name;
            btnParameter.classList.add('btn', 'btn-secondary', 'list-burger');
            btnParameter.name = parameters_data[i].name;
            parametersNode.appendChild(btnParameter);
            
        }
        currentMarker.setIcon(greenIcon);

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
        manageMapMenu(true, this, parameters_data)
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





