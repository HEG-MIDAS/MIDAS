// Author : David Nogueiras Blanco
// Last edition : 29.03.2023
// Project : MIDAS (HEG)

//////////////////////////////////////////////////////////////////////////////////////
// Arrays of data selected
//////////////////////////////////////////////////////////////////////////////////////

sourcesMap = ["climacity", "sabra", "vhg"];
stationsMap4Search = [];
stationsMap = [];
parametersMap = [];

markersArray = [];

//////////////////////////////////////////////////////////////////////////////////////
// Handles the offcanvas display
//////////////////////////////////////////////////////////////////////////////////////

const bsCollapse = new bootstrap.Collapse('#collapseWidthExample', {
    toggle: false
})

const dropupBootstrap = new bootstrap.Dropdown('#dropdownMenuButtonLegend', {
    toggle: false
})

//////////////////////////////////////////////////////////////////////////////////////
// Manage the map
//////////////////////////////////////////////////////////////////////////////////////

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);

//////////////////////////////////////////////////////////////////////////////////////
// Defining Icon colors
//////////////////////////////////////////////////////////////////////////////////////

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

//////////////////////////////////////////////////////////////////////////////////////
// Functions
//////////////////////////////////////////////////////////////////////////////////////

// Check if the request is possible by checking if there is at least 1 station
// and 1 parameter selected
// Return a boolean
function checkIfRequestIsPossible(){
    if (stationsMap.length > 0 && parametersMap.length > 0) {
        return true;
    }
    return false;
}


// Update the value of the variables containing the last date selected
function updateDateMap(val, isStartingDateMap){
    if(isStartingDateMap == 1){
        lastStartingDateMap = val
    }
    else{
        lastEndingDateMap = val
    }
}


function triggerParameterButton(){
    const stationsNode = document.getElementById("burger-map-stations");
    const parametersNode = document.getElementById("burger-map-parameters");

    if (stationsMap.some(e => e.slug === stationsNode.children[0].id)){
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
        bsCollapse.show();
    }
    else {
        bsCollapse.hide();
        chevronNode.classList.remove("extension-chevron-on");
        chevronNode.classList.add("extension-chevron");
    }
}


function manageMarkerColor(currentStationSlug=""){
    markersArray.forEach(marker => {
        if (stationsMap.some(e => e.slug === marker.options.stationSlug)){
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

        if (marker.options.stationSlug == currentStationSlug){
            if (marker instanceof customMarker) {
                marker.setIcon(yellowIcon);
            }
            else {
                marker.setStyle({color: 'yellow'})
            }
        }
    });
}


function openMapMenu(){
    manageMarkerColor();
    manageMapMenu();
}


function synchronizeButtonCollapseAndMarkers(){
    const chevronNode = document.getElementById("extension-chevron");
    const stationsNode = document.getElementById("burger-map-stations");
    var collapse = false;
    let station_slug = stationsNode.childNodes[0].id;

    // Check if the button is collapsing or not
    if (chevronNode.classList.contains("extension-chevron-on")) {
        collapse = true;
        // redefine station_slug if we close, since we don't need to highlight station
        station_slug = "";
    }

    handleButtonCollapse(collapse);
    manageMarkerColor(station_slug);
}


// Manage the display of the badges for the stations and the parameters
function manageBadges(){
    badgesElement = document.getElementById("badges-recap");
    badgesElement.innerHTML = '';

    // let badgeSearch = document.createElement("span");
    // badgeSearch.innerHTML = "Visualiser";
    // badgeSearch.classList.add('badge', 'bg-danger');
    // badgesElement.appendChild(badgeSearch);

    // Managing badges for the stations
    for (let i = 0; i < stationsMap.length; i++) {
        let badgeStation = document.createElement("span");
        badgeStation.innerHTML = stationsMap[i].name;
        badgeStation.classList.add('badge', 'bg-primary');
        badgeStation.setAttribute("onclick", "".concat("openSelectionMenuBadge(`", stationsMap[i].slug,"`,`", stationsMap[i].name,"`)"));
        badgesElement.appendChild(badgeStation);
    }

    // Managing badges for the parameters
    for (let i = 0; i < parametersMap.length; i++) {
        let badgeParameter = document.createElement("span");
        badgeParameter.innerHTML = parametersMap[i].name;
        badgeParameter.classList.add('badge', 'bg-secondary');
        badgesElement.appendChild(badgeParameter);
    }
}


// Manage the parameters selected or unselected
function manageParameter(parameterSlug, parameterName){
    btn = document.getElementById(parameterSlug);
    if (btn.classList.contains("btn-outline-secondary")){
        btn.classList.remove("btn-outline-secondary");
        btn.classList.add("btn-secondary");
        parametersMap.push({
            slug: parameterSlug,
            name: parameterName
        });
    }
    else {
        btn.classList.remove("btn-secondary");
        btn.classList.add("btn-outline-secondary");
        var index = parametersMap.findIndex(e => e.slug === parameterSlug);
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
            'stations': stationsMap.map(e => e.slug)
        }
        try {
            const parametersData = await requestParametersSimplified(options);
            // console.log(parametersData)
            var array_params_stations = []
            parametersData.forEach(e => {
                array_params_stations.push(e.slug);
            });
            for (let i = parametersMap.length-1; i >= 0; i--) {
                if (!array_params_stations.includes(parametersMap[i].slug)){
                    manageParameter(parametersMap[i].slug, parametersMap[i].name);
                }
                
            }
        }
        catch(err){
            console.log(err);
        }
    }
    else {
        for (let i = parametersMap.length-1; i >= 0; i--) {
            manageParameter(parametersMap[i].slug, parametersMap[i].name);
        }
    }
}


// Manage the station selected or unselected
function manageStation(stationSlug, stationName){
    btn = document.getElementById(stationSlug);
    if (!stationsMap.some(e => e.slug === stationSlug)){
        stationsMap.push({
            slug: stationSlug,
            name: stationName
        });
        btn.children[0].classList.remove("anim-delete-2-plus")
        btn.children[0].classList.add("anim-plus-2-delete")
    }
    else {
        var index = stationsMap.findIndex(e => e.slug === stationSlug);
        if (index !== -1) {
            stationsMap.splice(index, 1);
        }
        btn.children[0].classList.remove("anim-plus-2-delete")
        btn.children[0].classList.add("anim-delete-2-plus")
    }

    manageParametersOnStationDeletion();
    triggerParameterButton();
    manageBadges();
}


// Handles format the json body to send via the POST method to get the data requested
function requestMapData(lastStartingDate, lastEndingDate, sources, stations, parameters){
    // Hide the error message if it's not already hidden
    document.getElementById("error-dashboard-message").hidden = true;
    // Create loader icon
    loader = document.getElementById('loaderMap');
    if (myChart == null){
        loader.classList.add("loader");
    }
    else {
        loader.classList.add("loader-with-main");
        document.getElementById('mainMap').classList.add("opacity-low");
    }


    // Check the dates of start and end are filled and that there is at least one element selected for source, station, and parameter
    // to be able to send the request
    if (lastStartingDate != '' && lastEndingDate != '' && sources.length > 0 && stations.length > 0 && parameters.length > 0) {
        
        // Formatting dates for request
        var startingDate = new Date(lastStartingDate);
        var startingDateString = startingDate.getFullYear() +"-"+ (startingDate.getMonth()+1) +"-"+ startingDate.getDate() + " " + startingDate.getHours() + ":" + startingDate.getMinutes() + ":" + startingDate.getSeconds();
        var endingDate = new Date(lastEndingDate);
        var endingDateString = endingDate.getFullYear() +"-"+ (endingDate.getMonth()+1) +"-"+ endingDate.getDate() + " " + endingDate.getHours() + ":" + endingDate.getMinutes() + ":" + endingDate.getSeconds();

        // Construct the json body of the POST method
        options = {'sources': sources, 'stations': stations, 'parameters': parameters, 'starting_date': startingDateString, 'ending_date': endingDateString}
        return requestDataFetch(options);

    }

    // Promise.all([array_promises]).then((data) => {
    //     // Remove loader icon
    //     loader.className = '';
    //     document.getElementById("main").className = '';
    //     document.getElementById('main').classList.remove("opacity-low");
    //     // If there is an error in the promises, display an error message in the dashboard, if not draw the chart
    //     if (data.some((value) => {return (value[0]==undefined)})){
    //         document.getElementById("error-dashboard-message").hidden = false;
    //     } else {
    //         if (displayData){
    //             drawChart(data[0]);
    //         }
    //         else{
    //             downloadData(data[0]);
    //         }
    //     }
    // }).catch(e => {console.log(e); document.getElementById("error-dashboard-message").hidden = false;});
}

function waitForElement(elementId, callBack){
    window.setTimeout(function(){
        var element = document.getElementById(elementId);
        // console.log(element.classList.contains('show'))
        if(element.classList.contains('show')){
            callBack(elementId, element);
        }
        else{
            waitForElement(elementId, callBack);
        }
    }, 500)
}

async function displayDataMap(){
    // let jsonData = await requestMapData(lastStartingDateMap, lastEndingDateMap, sourcesMap, stationsMap.map(e => e.slug), parametersMap.map(e => e.slug));
    // drawChart([jsonData], "mainMap");
}


function manageLegendText(isOpen=false, parametersData=null){
    const divLegend = document.getElementById("divLegend");
    if (isOpen){
        let ulDivLegend = divLegend.getElementsByTagName("ul")[0];
        ulDivLegend.innerHTML = ""
        parametersData.forEach((e, idx, array) => {
            let elementListLegendHeader = document.createElement("li");
            let elementListLegendHeaderTitle = document.createElement("h6");
            elementListLegendHeaderTitle.classList.add("dropdown-header");
            elementListLegendHeaderTitle.innerHTML = e.name;

            elementListLegendHeader.appendChild(elementListLegendHeaderTitle);
            ulDivLegend.appendChild(elementListLegendHeader)

            let elementListLegendText = document.createElement("li");
            let elementListLegendTextInfo = document.createElement("p");
            elementListLegendTextInfo.classList.add("dropdown-item-text");
            if (e.infos != ""){
                elementListLegendTextInfo.innerHTML = e.infos;
            }
            else {
                elementListLegendTextInfo.innerHTML = "Aucune info disponible...";
            }

            elementListLegendText.appendChild(elementListLegendTextInfo);
            ulDivLegend.appendChild(elementListLegendText)


            if( idx < array.length-1){   
                let elementListLegendli = document.createElement("li");
                let elementListLegendlihr = document.createElement("hr");
                elementListLegendlihr.classList.add("dropdown-divider");
                
                elementListLegendli.appendChild(elementListLegendlihr);
                ulDivLegend.appendChild(elementListLegendli)
            }
        });
        divLegend.hidden = false;
        dropupBootstrap.show();
    }
    else {
        divLegend.hidden = true;
    }
}


// Manage the menu of the map, that means, that the generation of the content of the offcanvas is done here
function manageMapMenu(stationSlug=null, stationName=null, parametersData=null){
    const stationsNode = document.getElementById("burger-map-stations");
    const parametersNode = document.getElementById("burger-map-parameters");
    const temporalityNode = document.getElementById("card-map-temporality");
    const displayBtnNode = document.getElementById("display-btn-data-map");

    stationsNode.innerHTML = '';
    parametersNode.innerHTML = '';
    temporalityNode.innerHTML = '';
    displayBtnNode.innerHTML = '';

    // If the function was called by clicking on the open offcanvas button, displays the current information
    if (stationSlug == null){
        let noStations = true;
        let noParameters = true;

        // Manage the creation of the stations buttons
        if (stationsMap.length > 0){
            noStations = false;
            for (let i = 0; i < stationsMap.length; i++) {
                let btnStation = document.createElement("span");
                btnStation.innerHTML = stationsMap[i].name;
                btnStation.classList.add('btn', 'btn-primary');
                btnStation.style = "pointer-events: none; margin-right: 0.5em; margin-bottom: 0.5em; padding-bottom: 7px;";
                stationsNode.appendChild(btnStation);
            }

            // Manage the creation of the parameters buttons
            if (parametersMap.length > 0){
                noParameters = false;
                for (let i = 0; i < parametersMap.length; i++) {
                    let btnParameter = document.createElement("span");
                    btnParameter.innerHTML = parametersMap[i].name;
                    btnParameter.classList.add('btn', 'btn-secondary');
                    btnParameter.style = "pointer-events: none; margin-right: 0.5em; margin-bottom: 0.5em;";
                    parametersNode.appendChild(btnParameter);
                }
            }
        }

        // Deals the display of text when no station nor parameter is selected
        if(noStations){
            stationsNode.innerHTML = 'Aucune station sélectionnée...';
        }
        if(noParameters){
            parametersNode.innerHTML = 'Aucun paramètre sélectionné...';
        }

        // Creating temporality form
        let titleTemp = document.createElement("h2");
        titleTemp.innerHTML = "Temporalité :";

        let labelStart = document.createElement("label");
        labelStart.setAttribute("for", "startingDateMap");
        labelStart.innerHTML = "Date de début :";

        let inputStart = document.createElement("input");
        inputStart.setAttribute("type", "datetime-local");
        inputStart.id = "startingDateMap";
        inputStart.name = "starting_date_map";
        inputStart.classList.add("form-control");
        inputStart.required = true;
        inputStart.value = lastStartingDateMap;
        inputStart.setAttribute("oninput", "updateDateMap(this.value, 1)");

        let labelEnd = document.createElement("label");
        labelEnd.setAttribute("for", "endingDateMap");
        labelEnd.innerHTML = "Date de fin :";
        labelEnd.style = "margin-top: 1em;";

        let inputEnd = document.createElement("input");
        inputEnd.setAttribute("type", "datetime-local");
        inputEnd.id = "endingDateMap";
        inputEnd.name = "ending_date_map";
        inputEnd.classList.add("form-control");
        inputEnd.required = true;
        inputEnd.value = lastEndingDateMap;
        inputEnd.setAttribute("oninput", "updateDateMap(this.value, 0)");

        temporalityNode.appendChild(titleTemp);
        temporalityNode.appendChild(labelStart);
        temporalityNode.appendChild(inputStart);
        temporalityNode.appendChild(labelEnd);
        temporalityNode.appendChild(inputEnd);

        // Create button for displaying the data selected

        let btnDisplay = document.createElement("button");
        btnDisplay.setAttribute("type", "button");
        btnDisplay.classList.add("btn", "btn-primary");
        btnDisplay.setAttribute("onclick", "displayDataMap()");
        btnDisplay.innerHTML = "Visualiser";
        btnDisplay.disabled = !checkIfRequestIsPossible();
        btnDisplay.id = "displayButton";
        btnDisplay.dataset.bsToggle = "modal";
        btnDisplay.dataset.bsTarget = "#displayModal";

        displayBtnNode.appendChild(btnDisplay);

        manageLegendText()

    }
    else{
        // Creates a button like containing the name of the current station
        let btnStation = document.createElement("span");
        btnStation.innerHTML = stationName;
        btnStation.classList.add('btn', 'btn-primary');
        btnStation.id = stationSlug;
        btnStation.style = "pointer-events: none; margin-bottom: 0.5em;";

        // Creates a button to add or delete the current station
        let btnAddStation = document.createElement("span");
        btnAddStation.classList.add('btn', 'btn-primary');
        btnAddStation.innerHTML = '<i class="fas fa-plus-circle"></i>';
        btnAddStation.style = "padding: 0; border: 0; margin-left: 10px; pointer-events: auto;";
        // Check if the station was already added, if it is the case add the class for the delete button
        if (stationsMap.some(e => e.slug === btnStation.id)){
            btnAddStation.classList.add("anim-plus-2-delete");
        }
        btnAddStation.setAttribute("onclick", "".concat("manageStation(`",stationSlug,"`,`",stationName,"`)"));

        btnStation.appendChild(btnAddStation);
        stationsNode.appendChild(btnStation);

        for (let i = 0; i < parametersData.length; i++) {
            let btnParameter = document.createElement("button");
            btnParameter.innerHTML = parametersData[i].name;
            if (parametersMap.some(e => e.slug === parametersData[i].slug)){
                btnParameter.classList.add('btn', 'btn-secondary', 'list-burger');
            }
            else{
                btnParameter.classList.add('btn', 'btn-outline-secondary', 'list-burger');
            }
            if (!stationsMap.some(e => e.slug === parametersData[i].station)){
                btnParameter.classList.add('disabled')
            }
            btnParameter.id = parametersData[i].slug;
            btnParameter.name = parametersData[i].name;
            btnParameter.setAttribute("onclick", "".concat("manageParameter('", parametersData[i].slug,"','",parametersData[i].name,"')"));
            parametersNode.appendChild(btnParameter);
        }

        let btnDisplay = document.createElement("button");
        btnDisplay.setAttribute("type", "button");
        btnDisplay.classList.add("btn", "btn-primary");
        btnDisplay.setAttribute("onclick", "openMapMenu()");
        btnDisplay.innerHTML = "Récap";
        btnDisplay.id = "displayButton";

        displayBtnNode.appendChild(btnDisplay);

        manageLegendText(true, parametersData)
    }
    // Open menu
    bsCollapse.show();
    handleButtonCollapse();
}

async function openSelectionMenuMarker() {
    options = {
        'sources': sourcesMap,
        'stations': [this.options.stationSlug]
    }
    try {
        const parametersData = await requestParametersSimplified(options);
        manageMarkerColor(this.options.stationSlug);
        manageMapMenu(this.options.stationSlug, this.options.station, parametersData)
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
    marker.addTo(map).on("click", openSelectionMenuMarker);
    markersArray.push(marker);
}

function addingCircle2Map(latitude, longitude, stationName, slug) {
    var marker = new customCircle([parseFloat(latitude), parseFloat(longitude)], 600, options = {
        station: stationName,
        stationSlug: slug
    });
    marker.addTo(map).on("click", openSelectionMenuMarker);
    markersArray.push(marker);
}

// Handles the Map Menu opening when clicking a badge
async function openSelectionMenuBadge(stationSlug, stationName) {
    options = {
        'sources': sourcesMap,
        'stations': [stationSlug]
    }
    try {
        const parametersData = await requestParametersSimplified(options);

        // console.log(parametersData)
        
        manageMarkerColor(stationSlug);
        manageMapMenu(stationSlug, stationName, parametersData)
    }
    catch(err){
        console.log(err);
    }
}

// Add markers on the map thanks to their coordinates
// Depending on the precision of the coordinates, will display a point or a zone to select
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
            stationsMap4Search.push({
                name: stations_data[i]['name'],
                slug: stations_data[i]['slug']
            })
        }
    }
    catch(err){
        console.log(err);
    }
}


const levenshteinDistance = (s, t) => {
    if (!s.length) return t.length;
    if (!t.length) return s.length;
    const arr = [];
    for (let i = 0; i <= t.length; i++) {
        arr[i] = [i];
        for (let j = 1; j <= s.length; j++) {
            arr[i][j] =
            i === 0
                ? j
                : Math.min(
                    arr[i - 1][j] + 1,
                    arr[i][j - 1] + 1,
                    arr[i - 1][j - 1] + (s[j - 1] === t[i - 1] ? 0 : 1)
                );
        }
    }
    return arr[t.length][s.length];
};


function searchBarStations(valueOfSearchBar){
    cardResultsList = document.getElementById("cardResultsList");
    cardResultsList.innerHTML = "";

    if (valueOfSearchBar.length >= 3 && valueOfSearchBar.trim().length >= 3){
        valueOfSearchBar = valueOfSearchBar.trim().toLowerCase();
        let resultsFilter = stationsMap4Search.filter(station => {
            return station.name.toLowerCase().includes(valueOfSearchBar) || station.slug.toLowerCase().includes(valueOfSearchBar) || levenshteinDistance(station.name.toLowerCase(), valueOfSearchBar) <= 2 || levenshteinDistance(station.slug.toLowerCase(), valueOfSearchBar) <= 2;
        });

        if (resultsFilter.length > 0){

            resultsFilter.forEach(result => {
                listElement = document.createElement("li");
                listElement.classList.add("list-group-item", "listElementSelection");
                listElement.innerHTML = result.name.concat(" - ", result.slug);
                listElement.setAttribute("onclick", "".concat("openSelectionMenuBadge(`", result.slug,"`,`", result.name,"`)"))
                cardResultsList.appendChild(listElement);
            });
        }
    }
    else {
        listElement = document.createElement("li");
        listElement.classList.add("list-group-item", "clueListElementSelection");
        listElement.innerHTML = "Entrer au moins 3 caractères";
        cardResultsList.appendChild(listElement);
    }
}


function keyIputSearch(){
    let cardResultsList = document.getElementById("cardResultsList");
    let searchBar = document.getElementById("searchBar");
    let valOfSearchBar = searchBar.value

    if (valOfSearchBar.length >= 3 && valOfSearchBar.trim().length >= 3) {
        valOfSearchBar = valOfSearchBar.trim().toLowerCase();
        let resultsFilter = stationsMap4Search.filter(station => {
            return station.name.toLowerCase().includes(valOfSearchBar) || station.slug.toLowerCase().includes(valOfSearchBar) || levenshteinDistance(station.name.toLowerCase(), valOfSearchBar) <= 2 || levenshteinDistance(station.slug.toLowerCase(), valOfSearchBar) <= 2;
        });
        openSelectionMenuBadge(resultsFilter[0].slug, resultsFilter[0].name);
    }
    else {
        searchBar.focus();
    }
}


const searchInput = document.querySelector('#searchBar');
searchInput.addEventListener("input", (e) => {
    // Clean the content of the results
    searchBarStations(e.target.value);
});


document.addEventListener('click', function(event){
    let searchClick = document.getElementById("searchBar").contains(event.target);
    let searchBar = document.getElementById("searchBar");
    let valOfSearchBar = searchBar.value
    let isMagnifyingGlass = document.getElementById("magnifyingButtonId").contains(event.target) ||  document.getElementById("magnifyingId").contains(event.target);

    let cardResultsList = document.getElementById("cardResultsList");
    if (searchClick || isMagnifyingGlass) {
        valOfSearchBar = document.getElementById("searchBar").value
        searchBarStations(valOfSearchBar)

        if (isMagnifyingGlass && valOfSearchBar.trim().length >= 3){
            cardResultsList.parentNode.hidden = true;
        }
        else {
            cardResultsList.parentNode.hidden = false;
        }
    }
    else {
        cardResultsList.parentNode.hidden = true;
    }
});


searchInput.addEventListener('keydown', function(event){
    if (event.key === "Enter") {

        let searchBar = document.getElementById("searchBar");
        let valOfSearchBar = searchBar.value
        if (valOfSearchBar.length >= 3) {
            keyIputSearch();
            cardResultsList.parentNode.hidden = true;
        }
    }
});

//////////////////////////////////////////////////////////////////////////////////////
// Start of code
//////////////////////////////////////////////////////////////////////////////////////

// Creates request to request all the stations available on the API
options = {'sources': sourcesMap};
const stations_results = requestStationsSimplified(options);

const myModalEl = document.getElementById('displayModal');
const myInput = document.getElementById('displayButton')

myModalEl.addEventListener('shown.bs.modal', async event => {
    myInput.focus()
    let jsonData = await requestMapData(lastStartingDateMap, lastEndingDateMap, sourcesMap, stationsMap.map(e => e.slug), parametersMap.map(e => e.slug));
    jsonDataFormatted = formatDataJSON(lastStartingDateMap.toString().replace("T", " ") + ":00", lastEndingDateMap.toString().replace("T", " ") + ":00", [jsonData])
    drawChart(jsonDataFormatted, "mainMap");
    // Remove loader icon
    loader.className = '';
    document.getElementById('mainMap').classList.remove("opacity-low");
})

// Display all the stations on the map
setUpStationsOnMap();
