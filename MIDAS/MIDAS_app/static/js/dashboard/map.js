sourcesMap = ["climacity", "sabra", "vhg"];
stationsMap = [];
parametersMap = [];

markersArray = [];

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

var yellowIcon = new L.Icon({
    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-yellow.png',
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


options = {'sources': sourcesMap};
const stations_results = requestStationsSimplified(options);


function triggerParameterButton(){
    const stationsNode = document.getElementById("burger-map-stations");
    const parametersNode = document.getElementById("burger-map-parameters");

    if (stationsMap.includes(stationsNode.children[0].id)){
        for (const child of parametersNode.children) {
            child.classList.remove("disabled");
        }
    }
    else {
        for (const child of parametersNode.children) {
            child.classList.add("disabled");
        }
    }
}


function handleButtonCollapse(collapse=false){
    const chevronNode = document.getElementById("extension-chevron");
    if (chevronNode.classList.contains("extension-chevron") || !collapse) {
        chevronNode.classList.remove("extension-chevron");
        chevronNode.classList.add("extension-chevron-on");
    }
    else {
        bsCollapse.hide();
        chevronNode.classList.remove("extension-chevron-on");
        chevronNode.classList.add("extension-chevron");
    }
}


function synchronizeButtonCollapseAndMarkers(){
    const chevronNode = document.getElementById("extension-chevron");
    var collapse = false;
    if (chevronNode.classList.contains("extension-chevron-on")) {
        collapse = true;
    }
    manageMapMenu();
    handleButtonCollapse(collapse);
}


function manageMarkerColor(){
    markersArray.forEach(marker => {
        if (stationsMap.includes(marker.options.stationSlug)){
            if (marker instanceof customMarker) {
                marker.setIcon(greenIcon);
            }
            else {
                marker.setStyle({color: 'green'})
            }
        }
        else if (marker instanceof customMarker) {
            marker.setIcon(blueIcon);
        }
        else {
            marker.setStyle({color: '#3487FD'})
        }
    });
}


// Manage the display of the badges for the stations and the parameters
function manageBadges(){
    badgesElement = document.getElementById("badges-recap");
    badgesElement.innerHTML = '';
    for (let station = 0; station < stationsMap.length; station++) {
        let badgeStation = document.createElement("span");
        badgeStation.innerHTML = stationsMap[station];;
        badgeStation.classList.add('badge', 'bg-primary');
        badgesElement.appendChild(badgeStation);
    }

    for (let parameter = 0; parameter < parametersMap.length; parameter++) {
        let badgeParameter = document.createElement("span");
        badgeParameter.innerHTML = parametersMap[parameter];;
        badgeParameter.classList.add('badge', 'bg-secondary');
        badgesElement.appendChild(badgeParameter);
    }
}


// Manage the parameters selected or unselected
function manageParameter(parameterSlug){
    btn = document.getElementById(parameterSlug);
    if (btn.classList.contains("btn-outline-secondary")){
        btn.classList.remove("btn-outline-secondary");
        btn.classList.add("btn-secondary");
        parametersMap.push(parameterSlug);
    }
    else {
        btn.classList.remove("btn-secondary");
        btn.classList.add("btn-outline-secondary");
        var index = parametersMap.indexOf(parameterSlug);
        if (index !== -1) {
            parametersMap.splice(index, 1);
        }
    }

    manageBadges();
}


// Manage the parameters selected and the badges when a station is deleted
// Check if there is a station that use the parameters selected
// if not, change class of the parameters button and remove them from parametersMap array
async function manageParametersOnStationDeletion(){
    if (stationsMap.length > 0){
        options = {
            'sources': sourcesMap,
            'stations': stationsMap
        }
        try {
            const parametersData = await requestParametersSimplified(options);
            var array_params_stations = []
            parametersData.forEach(e => {
                array_params_stations.push(e.slug);
            });
            var cnt = parametersMap.length-1;
            while (cnt >= 0){
                if (!array_params_stations.includes(parametersMap[cnt])){
                    manageParameter(parametersMap[cnt]);
                }
                cnt--;
            }
        }
        catch(err){
            console.log(err);
        }
    }
    else {
        parametersMap.forEach(param =>{
            manageParameter(param);
        });
        while (parametersMap.length > 0) {
            manageParameter(parametersMap[0]);
        }
    }
}


// Manage the station selected or unselected
async function manageStation(stationSlug){
    btn = document.getElementById(stationSlug);
    if (!stationsMap.includes(stationSlug)){
        stationsMap.push(stationSlug);
        btn.children[0].classList.remove("anim-delete-2-plus")
        btn.children[0].classList.add("anim-plus-2-delete")
    }
    else {
        var index = stationsMap.indexOf(stationSlug);
        if (index !== -1) {
            stationsMap.splice(index, 1);
        }
        btn.children[0].classList.remove("anim-plus-2-delete")
        btn.children[0].classList.add("anim-delete-2-plus")
    }

    await manageParametersOnStationDeletion();
    triggerParameterButton();
    manageBadges();
}


// Manage the menu of the map, that means, that the generation of the content of the offcanvas is done here
function manageMapMenu(form=false, currentMarker=null, parametersData=null, collapse=false){
    const stationsNode = document.getElementById("burger-map-stations");
    const parametersNode = document.getElementById("burger-map-parameters");
    const burgerExpanded = document.getElementById("buttonBurger");

    stationsNode.innerHTML = '';
    parametersNode.innerHTML = '';

    manageMarkerColor();

    // If the function was called by clicking on the burger, displays the current information
    if (!form){
        if (stationsMap.length > 0){
            stationsNode.innerHTML = 'test'
        }
        else{
            stationsNode.innerHTML = 'Aucune station sélectionnée'
            parametersNode.innerHTML = 'Aucun paramètre sélectionné'
        }
    }
    else{
        let btnStation = document.createElement("span");
        btnStation.innerHTML = currentMarker.options.station;
        btnStation.classList.add('btn', 'btn-primary');
        btnStation.id = currentMarker.options.stationSlug;
        btnStation.style = "pointer-events: none;";

        let btnAddStation = document.createElement("span");
        btnAddStation.classList.add('btn', 'btn-primary');
        btnAddStation.innerHTML = '<i class="fas fa-plus-circle"></i>';
        btnAddStation.style = "padding: 0; margin-left: 10px; pointer-events: auto;";
        btnAddStation.setAttribute("onclick", "".concat("manageStation('",currentMarker.options.stationSlug,"')"));

        btnStation.appendChild(btnAddStation);
        stationsNode.appendChild(btnStation);

        for (let i = 0; i < parametersData.length; i++) {
            let btnParameter = document.createElement("button");
            btnParameter.innerHTML = parametersData[i].name;
            if (parametersMap.includes(parametersData[i].slug)){
                btnParameter.classList.add('btn', 'btn-secondary', 'list-burger');
            }
            else{
                btnParameter.classList.add('btn', 'btn-outline-secondary', 'list-burger');
            }
            if (!stationsMap.includes(parametersData[i].station)){
                btnParameter.classList.add('disabled')
            }
            btnParameter.id = parametersData[i].slug;
            btnParameter.name = parametersData[i].name;
            btnParameter.setAttribute("onclick", "".concat("manageParameter('", parametersData[i].slug,"')"));
            parametersNode.appendChild(btnParameter);
        }
        if (currentMarker instanceof customMarker) {
            currentMarker.setIcon(yellowIcon);
        }
        else {
            currentMarker.setStyle({color: 'yellow'})
        }
    }
    // Open menu
    bsCollapse.show();
    handleButtonCollapse();
}

async function openSelectionMenu() {
    options = {
        'sources': sourcesMap,
        'stations': [this.options.stationSlug]
    }
    try {
        const parametersData = await requestParametersSimplified(options);
        manageMapMenu(true, this, parametersData)
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
    markersArray.push(marker);
}

function addingCircle2Map(latitude, longitude, stationName, slug) {
    var marker = new customCircle([parseFloat(latitude), parseFloat(longitude)], 600, options = {
        station: stationName,
        stationSlug: slug
    });
    marker.addTo(map).on("click", openSelectionMenu);
    markersArray.push(marker);
}

async function setUpStationsOnMap(){
    try {
        const stations_data = await stations_results;
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





