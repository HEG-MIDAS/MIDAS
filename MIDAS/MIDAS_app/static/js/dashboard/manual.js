function handleSubmitButton(){
    var domDates = document.querySelectorAll('*[id^="buttonDates"]');
    var wait4submit = false;
    domDates.forEach(function(element, currentIndex, listObj){
        if (element.disabled && currentIndex > 0){
            wait4submit = true;
        }
    })
    if (wait4submit || domDates.length == 1){
        document.getElementById('submitButton').disabled = true;
        document.getElementById('downloadButton').disabled = true;
    }
    else {
        document.getElementById('submitButton').disabled = false;
        document.getElementById('downloadButton').disabled = false;
    }
}

//////////////////////////////////////////////////////////////////////////////////////
// Handle research and parallel research
//////////////////////////////////////////////////////////////////////////////////////

function addResearch(pageLoaded=true){
    // Check if it is possible to add a new research interface
    if (document.querySelectorAll("[id^='accordionDashboard']").length < NBMAXPARALLELSEARCHS+1) {

        // Clone accordionDashboard0 that is used as reference and display the it
        var clone = document.getElementById("accordionDashboard0").cloneNode(true);
        clone.removeAttribute("hidden");

        // Modify the index of the element of the new accordion
        Array.from(clone.querySelectorAll("[id*='0']")).map(element => element.id = element.id.replace("0", idxResearch.toString()));
        clone.id = clone.id.replace("0", idxResearch.toString());
        Array.from(clone.querySelectorAll("[data-bs-target*='0']")).map(element => element.setAttribute("data-bs-target", element.getAttribute("data-bs-target").replace("0", idxResearch.toString())));
        Array.from(clone.querySelectorAll("[for*='0']")).map(element => element.setAttribute("for", element.getAttribute("for").replace("0", idxResearch.toString())));
        Array.from(clone.querySelectorAll("[onclick*='0']")).map(element => element.setAttribute("onclick", element.getAttribute("onclick").replace("0", idxResearch.toString())));

        // Create a const containing the title of the new research created
        const titleOfFilter = clone.querySelector("#title"+idxResearch.toString())

        // Add new index inside the array that will contain the current indexes
        arrayCurrentIdx.push(idxResearch);

        // Edit the title of the new research by using the position in the array as displayed element
        if (pageLoaded){
            titleOfFilter.innerHTML = "Données : <span class='change-animation'>filtre " + (arrayCurrentIdx.indexOf(idxResearch)+1).toString()+"</span>";
        }
        else {
            titleOfFilter.innerHTML = "Données : <span>filtre " + (arrayCurrentIdx.indexOf(idxResearch)+1).toString()+"</span>";
        }

        idxResearch++;

        // Create new arrays that will contain the data of the new research inside of the elements array
        sources.push([]);
        stations.push([]);
        parameters.push([]);

        target = document.querySelector("#addResearchDiv");
        target.parentNode.insertBefore(clone, target);

        handleSubmitButton();
    }
    // Check if the addResearchButton was not already disabled and if we exceed the size max accepted for the research interfaces
    if (document.getElementById("addResearchButton").getAttribute("disabled")==null && document.querySelectorAll("[id^='accordionDashboard']").length >= NBMAXPARALLELSEARCHS+1) {
        document.getElementById("addResearchButton").setAttribute("disabled", true);
    }
    document.getElementById("addResearchButton").innerHTML = "Ajouter une recherche ("+(document.querySelectorAll("[id^='accordionDashboard']").length-1)+"/"+NBMAXPARALLELSEARCHS+`) <i class="fa-solid fa-circle-plus"></i>`;
}

function removeResearch(e, idx){
    e.parentElement.remove()

    // Remove arrays with the data from the differents arrays of elements
    var index = arrayCurrentIdx.indexOf(idx);
    if (index !== -1) {
        arrayCurrentIdx.splice(index, 1);
        sources.splice(index, 1);
        stations.splice(index, 1);
        parameters.splice(index, 1);
    }
    handleSubmitButton();

    for (let i = 0; i < arrayCurrentIdx.length; i++) {
        const titleOfFilter = document.querySelector("#title"+arrayCurrentIdx[i].toString());
        titleOfFilter.innerHTML = "Données : <span class='change-animation'>filtre " + (arrayCurrentIdx.indexOf(arrayCurrentIdx[i])+1).toString()+"</span>";
    }

    // Check if addResearchButton is already disable and if the number of simultaneous researchs are below the max
    if (document.getElementById("addResearchButton").getAttribute("disabled")!=null && document.querySelectorAll("[id^='accordionDashboard']").length < NBMAXPARALLELSEARCHS+1) {
        document.getElementById("addResearchButton").removeAttribute("disabled");
    }
    document.getElementById("addResearchButton").innerHTML = "Ajouter une recherche ("+(document.querySelectorAll("[id^='accordionDashboard']").length-1)+"/"+NBMAXPARALLELSEARCHS+`) <i class="fa-solid fa-circle-plus"></i>`;
}

window.addEventListener("load", addResearch(false));

//////////////////////////////////////////////////////////////////////////////////////
// Elements Dashboard Selection
//////////////////////////////////////////////////////////////////////////////////////

// Handles format the json body to send via the POST method to get the data requested
async function requestData(displayData = true){
    // Hide the error message if it's not already hidden
    document.getElementById("error-dashboard-message").hidden = true;
    // Create loader icon
    loader = document.getElementById('loader');
    if (myChart == null){
        loader.classList.add("loader");
    }
    else {
        loader.classList.add("loader-with-main");
        document.getElementById('main').classList.add("opacity-low");
    }
    

    array_promises = [];
    for (var cnt=0; cnt < arrayCurrentIdx.length; cnt++) {
        var startingDateValue = document.getElementById('startingDate'+arrayCurrentIdx[cnt].toString()).value;
        var endingDateValue = document.getElementById('endingDate'+arrayCurrentIdx[cnt].toString()).value;
        // Check the dates of start and end are filled and that there is at least one element selected for source, station, and parameter
        // to be able to send the request
        if (startingDateValue != '' && endingDateValue != '' && sources[cnt].length > 0 && stations[cnt].length > 0 && parameters[cnt].length > 0) {
            // Format dates
            var startingDate = new Date(startingDateValue);
            // console.log(startingDate)
            var startingDateString = startingDate.getFullYear() +"-"+ (startingDate.getMonth()+1) +"-"+ startingDate.getDate() + " " + startingDate.getHours() + ":" + startingDate.getMinutes() + ":" + startingDate.getSeconds();
            var endingDate = new Date(endingDateValue);
            var endingDateString = endingDate.getFullYear() +"-"+ (endingDate.getMonth()+1) +"-"+ endingDate.getDate() + " " + endingDate.getHours() + ":" + endingDate.getMinutes() + ":" + endingDate.getSeconds();

            // Construct the json body of the POST method
            options = {'sources': sources[cnt], 'stations': stations[cnt], 'parameters': parameters[cnt], 'starting_date': startingDateString, 'ending_date': endingDateString}
            let promise = await requestDataFetch(options);
            array_promises.push(promise);
        }
    };

    Promise.all([array_promises]).then((data) => {
        // Remove loader icon
        loader.className = '';
        document.getElementById("main").className = '';
        document.getElementById('main').classList.remove("opacity-low");
        // If there is an error in the promises, display an error message in the dashboard, if not draw the chart
        if (data.some((value) => {return (value[0]==undefined)})){
            document.getElementById("error-dashboard-message").hidden = false;
        } else {
            if (displayData){
                drawChart(data[0]);
            }
            else{
                downloadData(data[0]);
            }
        }
    }).catch(e => {console.log(e); document.getElementById("error-dashboard-message").hidden = false;});
}

// Modify the properties of the accordeon component to be always open or not in function of the dedicated box
function fixedAccordeon(e){
    var data_to_pass = null;
    fixed = true;
    if (!e.checked) {
        data_to_pass = document.getElementById('accordionDashboard');
        fixed = false;
    }

    // Iterate over each accordion component to remove or not the property that closes it
    for (var i = 0; i < document.getElementsByClassName('accordion-collapse').length; i++) {
        document.getElementsByClassName('accordion-collapse')[i].dataset.bsParent = false;
        if (!fixed) {
            // Redifine bsParent if not fixed
            document.getElementsByClassName('accordion-collapse')[i].dataset.bsParent = '#accordionDashboard';
        }
        // Catch exemption launched the first time that config parent is setted and do redifine it always after
        try {
            bootstrap.Collapse.getInstance(document.getElementsByClassName('accordion-collapse')[i])._config.parent = data_to_pass;
        }
        catch {}
    }
}

// Function lauched when a source is selected or deselected by the user
// Adds or deletes the sources from the global array dedicated and enable the selection of stations
// if there is at least one source selected
async function select_source(e, idx){
    var index = arrayCurrentIdx.indexOf(idx);
    var stationsAccordeon = document.getElementById('headingStations'+idx.toString()).getElementsByTagName('button')[0];
    // Check if the user selected or deselected a source
    if (e.checked) {
        // If the user selects a source
        // Enable accordeon component for stations
        stationsAccordeon.disabled = false;
        // Add source to source array
        sources[index].push(e.value);
        // Prepare json body to POST request
        options = {'sources': sources[index]};
        requestStations(options, idx);
        var cs = document.getElementById('buttonStations'+idx.toString());
        // Open next accordeon if it is closed
        if (cs.getAttribute('aria-expanded') === 'false') {
            cs.click();
        }
    }
    else {
        // Deletes source from source array
        var idx_sources = sources[index].indexOf(e.value);
        if (idx_sources !== -1) {
            sources[index].splice(idx_sources, 1);
        }
        // If there is no sources selected
        if (sources[index].length == 0) {
            // Closes all open accordeons below
            var cs = document.getElementById('buttonStations'+idx.toString());
            if (cs.getAttribute('aria-expanded') === 'true') {
                cs.click();
            }
            var cs = document.getElementById('buttonParameters'+idx.toString());
            if (cs.getAttribute('aria-expanded') === 'true') {
                cs.click();
            }
            var cs = document.getElementById('buttonDates'+idx.toString());
            if (cs.getAttribute('aria-expanded') === 'true') {
                cs.click();
            }
            // Clear stations and parameters arrays
            stations[index] = [];
            parameters[index] = [];
            // Disable the possibility to expand accordeon of stations and parameters
            stationsAccordeon.disabled = true;
            parametersAccordeon = document.getElementById('headingParameters'+idx.toString()).getElementsByTagName('button')[0];
            parametersAccordeon.disabled = true;
            parametersAccordeon = document.getElementById('headingDates'+idx.toString()).getElementsByTagName('button')[0];
            parametersAccordeon.disabled = true;

            handleSubmitButton();
        }
        else{
            // Prepare json body to POST request for the sources left
            options = {'sources': sources[index]};
            await requestStations(options, idx);
            if (!fixed) {
                // Open accordeon of stations
                var cs = document.getElementById('buttonStations'+idx.toString());
                cs.click();
            }
        }
        if (parameters[index].length == 0) {
            var cs = document.getElementById('buttonDates'+idx.toString());
            if (cs.getAttribute('aria-expanded') === 'true') {
                cs.click();
            }
        }
    }
}

// Function lauched when a station is selected or deselected by the user
// Adds or deletes the stations from the global array dedicated and enable the selection of parameters
// if there is at least one station selected
function select_station(e, idx){
    var index = arrayCurrentIdx.indexOf(idx);
    var parametersAccordeon = document.getElementById('headingParameters'+idx.toString()).getElementsByTagName('button')[0];
    // Split the value to an array of elements (value of e is formed as => value="source station")
    var array_e_values = e.value.split(' ');
    // Check if the user selected or deselected a station
    if (e.checked) {
        // Add station value to its dedicated array
        stations[index].push(array_e_values.at(-1));
        // Prerare json body for POST request
        options = {'sources': sources[index], 'stations': stations[index]};
        // If the user selects a stations
        // Enable accordeon component for parmeters
        parametersAccordeon.disabled = false;
        requestParameters(options, idx)
        // Open parameters accordion if it's closed
        var cs = document.getElementById('buttonParameters'+idx.toString());
        if (cs.getAttribute('aria-expanded') === 'false') {
            cs.click();
        }
    }
    else {
        // Deletes station from its array
        var idx_stations = stations[index].indexOf(array_e_values.at(-1));
        if (idx_stations !== -1) {
            stations[index].splice(idx_stations, 1);
        }
        if (stations[index].length == 0) {
            // If there is no more stations in the array, closes all accordeons below
            var cs = document.getElementById('buttonParameters'+idx.toString());
            if (cs.getAttribute('aria-expanded') === 'true') {
                cs.click();
            }
            var cs = document.getElementById('buttonDates'+idx.toString());
            if (cs.getAttribute('aria-expanded') === 'true') {
                cs.click();
            }
            // Set parameters array to empty
            parameters[index] = [];
            // Disabled accordeons below
            parametersAccordeon.disabled = true;
            var datesAccordeon = document.getElementById('headingDates'+idx.toString()).getElementsByTagName('button')[0];
            datesAccordeon.disabled = true;

            handleSubmitButton();
        }
        else{
            // Prepare json body to POST request for the stations left
            options = {'sources': sources[index], 'stations': stations[index]};
            requestParameters(options, idx)
            // Open next accordeon if the accordeons are not fixed
            if (!fixed) {
                var cs = document.getElementById('buttonParameters'+idx.toString());
                cs.click();
            }
        }
    }
    handleElementsSelection()
}

// Function lauched when a parameter is selected or deselected by the user
// Adds or deletes the parameters from the global array dedicated and enable the selection of dates
// if there is at least one parameter selected
function select_parameter(e, idx){
    var index = arrayCurrentIdx.indexOf(idx);
    var datesAccordeon = document.getElementById('headingDates'+idx.toString()).getElementsByTagName('button')[0];
    // Split the value to an array of elements (value of e is formed as => value="source station1,station2 parameter")
    var array_e_values = e.value.split(' ');
    // Check if the user selected or deselected a parameter
    if (e.checked) {
        parameters[index].push(array_e_values.at(-1));
        // If the user selects a parameter
        // Enable accordeon component for dates
        datesAccordeon.disabled = false;
        // Open dates accordeon if it is closed
        var cs = document.getElementById('buttonDates'+idx.toString());
        if (cs.getAttribute('aria-expanded') === 'false') {
            cs.click();
        }
        handleSubmitButton();
    }
    else {
        // Delete parameter from its array
        var idx_param = parameters[index].indexOf(array_e_values.at(-1));
        if (idx_param !== -1) {
            parameters[index].splice(idx_param, 1);
        }
        if (parameters[index].length == 0) {
            // If there are no paremeters left in the dedicated array
            // Closes and disable date accordeon
            var cs = document.getElementById('buttonDates'+idx.toString());
            if (cs.getAttribute('aria-expanded') === 'true') {
                cs.click();
            }
            datesAccordeon.disabled = true;
            handleSubmitButton();
        }
        else{
            // Open next accordeon if the accordeons are not fixed
            if (!fixed) {
                var cs = document.getElementById('buttonDates'+idx.toString());
                cs.click();
            }
        }
    }
    handleElementsSelection()
}

function handleElementsSelection() {
    var allParameters = document.querySelectorAll('[id^="accordionParameters"]');
    //console.log(allParameters);
}


//////////////////////////////////////////////////////////////////////////////////////
// Change the dimension display
//////////////////////////////////////////////////////////////////////////////////////


function flipDimensionDisplay(){
    console.log("Switch");
}
