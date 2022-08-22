// CONSTANTS
const NBMAXPARAMETERSSELECTED = 6;
const NBMAXPARALLELSEARCHS = 2;
const TYPESPLOTGRAPH = ['line', 'bar', 'scatter']

// Global variables

// Arrays that will contain the elements selected by the user
// each dimension correspond to a research div used
var sources = [];
var stations = [];
var parameters = [];

// Will contain all the current indexes of the research interfaces
var arrayCurrentIdx = [];

// Data requests JSON object
var options = {};
// Data of echarts JSON object
var option = {};

// state of the accordeon, is it always open ?
var fixed = true;

// index to give to the next research interface created
var idxResearch = 1;

// echarts display
var myChart;

//////////////////////////////////////////////////////////////////////////////////////
// Define default dates of data research
//////////////////////////////////////////////////////////////////////////////////////

// get todays date
var datePH = new Date();
// var date = datePH.getFullYear()+'-'+(datePH.getMonth() + 1)+'-'+datePH.getDate();
// var time = datePH.getHours() + ":" + datePH.getMinutes();
// var dateTime = date+' '+time;

const endingDate = document.getElementById("endingDate0");
endingDate.value = datePH.toISOString().slice(0, -8);

// Get 30 days ago date
const startingDate = document.getElementById("startingDate0");
datePH.setDate(datePH.getDate() - 30);
datePH.setHours(2);
datePH.setMinutes(0);
startingDate.value = datePH.toISOString().slice(0, -8);

//////////////////////////////////////////////////////////////////////////////////////
// Handle parameters selection
//////////////////////////////////////////////////////////////////////////////////////

function disableOrNotParametersThatCanBeSelected(){

}

//////////////////////////////////////////////////////////////////////////////////////
// Handle research and parallel research
//////////////////////////////////////////////////////////////////////////////////////

function addResearch(){
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

        const titleOfFilter = clone.querySelector("#title"+idxResearch.toString())
        titleOfFilter.innerHTML = titleOfFilter.innerHTML.replace("0", idxResearch.toString());

        // Add new index inside the array that will contain the current indexes
        arrayCurrentIdx.push(idxResearch);
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
    console.log("HERE :")
    handleSubmitButton();

    // Check if addResearchButton is already disable and if the number of simultaneous researchs are below the max
    if (document.getElementById("addResearchButton").getAttribute("disabled")!=null && document.querySelectorAll("[id^='accordionDashboard']").length < NBMAXPARALLELSEARCHS+1) {
        document.getElementById("addResearchButton").removeAttribute("disabled");
    }
}

window.addEventListener("load", addResearch);

//////////////////////////////////////////////////////////////////////////////////////
// Elements Dashboard Selection
//////////////////////////////////////////////////////////////////////////////////////

// Handles format the json body to send via the POST method to get the data requested
async function requestData(){
    array_promises = [];
    for (var cnt=0; cnt < arrayCurrentIdx.length; cnt++) {
        var startingDateValue = document.getElementById('startingDate'+arrayCurrentIdx[cnt].toString()).value;
        var endingDateValue = document.getElementById('endingDate'+arrayCurrentIdx[cnt].toString()).value;
        // Check the dates of start and end are filled and that there is at least one element selected for source, station, and parameter
        // to be able to send the request
        if (startingDateValue != '' && endingDateValue != '' && sources[cnt].length > 0 && stations[cnt].length > 0 && parameters[cnt].length > 0) {
            // Format dates
            var startingDate = new Date(startingDateValue);
            var startingDateString = startingDate.getUTCFullYear() +"-"+ (startingDate.getUTCMonth()+1) +"-"+ startingDate.getUTCDate() + " " + startingDate.getUTCHours() + ":" + startingDate.getUTCMinutes() + ":" + startingDate.getUTCSeconds();
            var endingDate = new Date(endingDateValue);
            var endingDateString = endingDate.getUTCFullYear() +"-"+ (endingDate.getUTCMonth()+1) +"-"+ endingDate.getUTCDate() + " " + endingDate.getUTCHours() + ":" + endingDate.getUTCMinutes() + ":" + endingDate.getUTCSeconds();

            // Construct the json body of the POST method
            options = {'sources': sources[cnt], 'stations': stations[cnt], 'parameters': parameters[cnt], 'starting_date': startingDateString, 'ending_date': endingDateString}

            let test = await requestDataFetch(options);
            array_promises.push(test);
        }
    };

    Promise.all([array_promises]).then((data) => {
        document.getElementById("main").className = '';
        drawChart(data[0]);
    });
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
function select_source(e, idx){
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
            requestStations(options, idx);
            if (!fixed) {
                // Open accordeon of stations
                var cs = document.getElementById('buttonStations'+idx.toString());
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
// Fetch requests to get data
//////////////////////////////////////////////////////////////////////////////////////

// Add CSRF into a constant to be used by the fetch requests
const csrf = document.querySelector('input[name="csrfmiddlewaretoken"]').value ;
// Request all the stations available for the selected sources
function requestStations(options, idx){
    // Request station-dashboard view
    var index = arrayCurrentIdx.indexOf(idx);
    fetch('/stations-dashboard/',{
        method: 'POST',
        headers: {
            'X-CSRFToken': csrf,
        },
        body: JSON.stringify(
            options
        )
    })
    .then(function(response) {
        // Handle json response
        return response.json();
    })
    .then(function(responseJSONData) {
        // Parse JSON
        jsonData = JSON.parse(responseJSONData);
        // Array that will contain all the slugs of the stations of the request
        var stationsSlug = [];
        var accordionStations = document.getElementById("accordionStations"+idx.toString());
        // Remove all the checkboxes of the stations in the element accordionStations
        while (accordionStations.firstChild) {
            accordionStations.removeChild(accordionStations.firstChild);
        }
        // Create checkboxes for the stations in the request
        for (var i = 0; i < jsonData.length; i++) {
            // Create div
            const accDiv = document.createElement("div");
            accDiv.className = "form-check form-check-inline";
            // Create input
            const accInp = document.createElement("input");
            accInp.className = "form-check-input";
            accInp.type = "checkbox";
            // Define the value of the input with the slug of the source concatenate with the station's slug
            accInp.value = jsonData[i]['source']['slug'].concat(" ", jsonData[i]['slug']);
            accInp.id = "flexCheck" + jsonData[i]['slug']+idx.toString();
            accInp.setAttribute('onclick', 'select_station(this, ' + idx.toString() + ')');
            // Create label
            const accLab = document.createElement("label");
            accLab.className = "form-check-label";
            accLab.setAttribute("for", "flexCheck" + jsonData[i]['slug']+idx.toString());
            accLab.innerText = jsonData[i]['name'];
            // Add childs
            accDiv.appendChild(accInp);
            accDiv.appendChild(accLab);
            accordionStations.appendChild(accDiv);

            // Add slug of the station to our array that retrace all the station out of the request
            stationsSlug.push(jsonData[i]['slug'])
        }
        
        // This part check the boxes that were previously selected and can still be
        // Check if there is stations selected
        if (stations[index].length > 0){
            for (var i = stations[index].length-1; i >= 0; --i) {
                // Check if the station is still available to be selected
                /*console.log(stations)
                console.log(stationsSlug)
                console.log(stations[i])
                console.log(stationsSlug.includes(stations[i]))
                */
                if (stationsSlug.includes(stations[index][i])){
                    //console.log(stations[i])
                    // Select the station box
                    document.getElementById("flexCheck"+stations[index][i]+idx.toString()).checked = true;
                    // Request for the parameters of the box selected and will do the same stuff
                    requestParameters({'sources': sources[index], 'stations': stations[index][i]})
                }
                else {
                    // If the code enter here, it means that the station was not in the request so it is deleted from our stations' array 
                    stations[index].splice(i, 1);
                }
                //console.log(stations)
                //console.log(stationsSlug)
            }
        }
        // If there is no stations selected
        if (stations[index].length == 0) {
            var cs = document.getElementById('buttonParameters'+idx.toString());
            // Check if the parameters div is expanded
            if (cs.getAttribute('aria-expanded') === 'true') {
                // Closes it
                cs.click();
            }
            // Remove all parameters of the array
            parameters[index] = [];
            parametersAccordeon = document.getElementById('headingParameters'+idx.toString()).getElementsByTagName('button')[0];
            // Disabled the accordeon of parameters as there is no stations selected
            parametersAccordeon.disabled = true;
        }
    });
}

// Request all the paremeters available for the selected stations and sources
function requestParameters(options, idx){
    var index = arrayCurrentIdx.indexOf(idx);
    // Request parameters to view parameters-dashboard
    fetch('/parameters-dashboard/',{
        method: 'POST',
        headers: {
            'X-CSRFToken': csrf,
        },
        body: JSON.stringify(
            options
        )
    })
    .then(function(response) {
        // Get a response on JSON format
        return response.json();
    })
    .then(function(responseJSONData) {
        // Parse the JSON response
        jsonData = JSON.parse(responseJSONData);
        // Array that will serve to know which parameters where in the request (we will use the slug)
        var parametersSlug = [];
        var accordionParameters = document.getElementById("accordionParameters"+idx.toString());
        // Delete all the checkboxes inside the parameter accordion
        while (accordionParameters.firstChild) {
            accordionParameters.removeChild(accordionParameters.firstChild);
        }
        // Create checkboxes for each parameter in the request
        for (var i = 0; i < jsonData.length; i++) {
            // Create div
            const accDiv = document.createElement("div");
            accDiv.className = "form-check form-check-inline";
            accDiv.title = jsonData[i]['infos'];
            // Create input
            const accInp = document.createElement("input");
            accInp.className = "form-check-input";
            accInp.type = "checkbox";
            // Add value to parameter that contain the slugs of the source, station and parameter
            accInp.value = jsonData[i]['source'].concat(" ", jsonData[i]['station']).concat(" ", jsonData[i]['slug']);
            accInp.id = "flexCheck" + jsonData[i]['slug']+idx.toString();
            accInp.setAttribute('onclick', 'select_parameter(this, ' + idx.toString() + ')');
            // Create label
            const accLab = document.createElement("label");
            accLab.className = "form-check-label";
            accLab.setAttribute("for", "flexCheck" + jsonData[i]['slug']+idx.toString());
            accLab.innerText = jsonData[i]['name'];
            // Happen children
            accDiv.appendChild(accInp);
            accDiv.appendChild(accLab);
            accordionParameters.appendChild(accDiv);

            // Add slug of the current paramter to our current parameter array
            parametersSlug.push(jsonData[i]['slug'])
        }

        // Check if there was paremeters selected
        if (parameters[index].length > 0){
            for (var i = parameters[index].length-1; i >= 0; --i) {
                // If the selected parameter is still in the request
                if (parametersSlug.includes(parameters[index][i])){
                    // Select it
                    document.getElementById("flexCheck"+parameters[index][i]+idx.toString()).checked = true;
                }
                else {
                    // If the selected parameter is not in the request, delete it from our list of selected parameters
                    parameters[index].splice(i, 1);
                }
            }
        }
        // After checking if there is still selected parameters, we check if there is none
        if (parameters[index].length == 0) {
            parameters[index] = [];
            var cs = document.getElementById('buttonDates'+idx.toString());
            // If the accordion containing the selection of dates is expanded
            if (cs.getAttribute('aria-expanded') === 'true') {
                // Closes it
                cs.click();
            }
        }

    });
}

// Request data from the sources, stations, parameters, and date selected
function requestDataFetch(options){
    return fetch('/request-data-dashboard/',{
        method: 'POST',
        headers: {
            'X-CSRFToken': csrf,
        },
        body: JSON.stringify(
            options
        )
    })
    .then(function(response) {
        // Get a JSON response
        return response.json();
    })
    .then(function(responseJSONData) {
        // Parse JSON response
        // console.log(responseJSONData);
        jsonData = JSON.parse(responseJSONData);
        return jsonData;
    });
}


function handleSubmitButton(){
    var domDates = document.querySelectorAll('*[id^="buttonDates"]');
    console.log(domDates);
    var wait4submit = false;
    domDates.forEach(function(element, currentIndex, listObj){
        if (element.disabled && currentIndex > 0){
            wait4submit = true;
        }
    })
    if (wait4submit || domDates.length == 1){
        document.getElementById('submitButton').disabled = true;
    }
    else {
        document.getElementById('submitButton').disabled = false;
    }
}


//////////////////////////////////////////////////////////////////////////////////////
// Change the dimension display
//////////////////////////////////////////////////////////////////////////////////////


function flipDimensionDisplay(){
    console.log("Switch");
}


//////////////////////////////////////////////////////////////////////////////////////
// Echarts
//////////////////////////////////////////////////////////////////////////////////////


// Handles the responsiveness of the echarts plot
function resetEchartsPlot() {
    if (myChart != null && myChart != '' && myChart != undefined) {
        myChart.dispose() //Solve the error reported by echarts dom already loaded
    }

    // Initialize the echarts instance based on the prepared dom
    myChart = echarts.init(document.getElementById('main'));

    // Display the chart using the configuration items and data just specified.
    myChart.setOption(option, true);
}

window.addEventListener('resize', resetEchartsPlot);


function addMarkLineToEchartsPlot(e, typeString, nameString){
    if (e.checked) {
        for (var i=0; i < option.series.length; i++) {
            if (!option.series[i].markLine.data.some(e => e.type === typeString)){
                option.series[i].markLine.data.push({ type: typeString, name: nameString });//), { type: 'median', name: 'Median line' }];
            }
        }
    }
    else {
        for (var i=option.series.length-1; i >= 0; i--) {
            option.series[i].markLine.data.forEach((element, index) => {
                if (element.type === typeString){
                    option.series[i].markLine.data.splice(index, 1);
                }
            });
        }
    }
    resetEchartsPlot();
}


function changeLinePlotDisplay(name, displayType){
    console.log(displayType)
    option.series.forEach(function(element, currentIndex) {
        if (element.name == name){
            element.type = displayType;
        }
    });

    resetEchartsPlot();
}


function addRuleOfEChartsParameters(echartSeriesNames){
    var baseDiv = document.getElementById("EchartsParameters");
    
    while (baseDiv.firstChild) {
        baseDiv.removeChild(baseDiv.firstChild);
    }

    const div = document.createElement("div");
    div.id = "EchartsViewParameters";

    const title = document.createElement("h4");
    title.innerHTML = "Paramètres d'affichage";
    div.appendChild(title);

    // Creates some buttons that allow to show statistical values on the echarts graph

    const divStats = document.createElement("div");
    divStats.id = "EchartsViewParametersStatistics";

    const averageInp = document.createElement("input");
    averageInp.className = "form-check-input ";
    averageInp.type = "checkbox";
    averageInp.id = "CheckAverage";
    averageInp.setAttribute("onclick", "addMarkLineToEchartsPlot(this, 'average', 'Avg')");
    const averageLab = document.createElement("label");
    averageLab.className = "form-check-label lab-param-echarts";
    averageLab.setAttribute("for", "CheckAverage");
    averageLab.innerText = "Afficher la moyenne";

    divStats.appendChild(averageInp);
    divStats.appendChild(averageLab);

    // Median button
    const medianInp = document.createElement("input");
    medianInp.className = "form-check-input";
    medianInp.type = "checkbox";
    medianInp.id = "CheckMedian";
    medianInp.setAttribute("onclick", "addMarkLineToEchartsPlot(this, 'median', 'Median')");
    const medianLab = document.createElement("label");
    medianLab.className = "form-check-label lab-param-echarts";
    medianLab.setAttribute("for", "CheckMedian");
    medianLab.innerText = "Afficher la medianne";

    divStats.appendChild(medianInp);
    divStats.appendChild(medianLab);

    // Min button
    const minInp = document.createElement("input");
    minInp.className = "form-check-input";
    minInp.type = "checkbox";
    minInp.id = "CheckMin";
    minInp.setAttribute("onclick", "addMarkLineToEchartsPlot(this, 'min', 'Min')");
    const minLab = document.createElement("label");
    minLab.className = "form-check-label lab-param-echarts";
    minLab.setAttribute("for", "CheckMin");
    minLab.innerText = "Afficher le minimum";

    divStats.appendChild(minInp);
    divStats.appendChild(minLab);

    // Max button
    const maxInp = document.createElement("input");
    maxInp.className = "form-check-input";
    maxInp.type = "checkbox";
    maxInp.id = "CheckMax";
    maxInp.setAttribute("onclick", "addMarkLineToEchartsPlot(this, 'max', 'Max')");
    const maxLab = document.createElement("label");
    maxLab.className = "form-check-label lab-param-echarts";
    maxLab.setAttribute("for", "CheckMax");
    maxLab.innerText = "Afficher le maximum";

    divStats.appendChild(maxInp);
    divStats.appendChild(maxLab);
    
    div.appendChild(divStats);

    // Create a select for each element displayed that allow to change the line to bar or bar to line

    const divPlot = document.createElement("div");
    divPlot.id = "EchartsViewParametersPlot";

    for (var i=0; i<echartSeriesNames.length; i++){

        const labelSelect = document.createElement("label");
        labelSelect.classList.add("label-select-type-display");
        labelSelect.innerHTML = echartSeriesNames[i]+" :";

        const select = document.createElement("select");
        select.classList.add("form-select");
        select.classList.add("select-type-display");
        select.setAttribute("onchange", "changeLinePlotDisplay('"+echartSeriesNames[i]+"', this.value)")

        TYPESPLOTGRAPH.forEach(function(element){
            const optionSelectLine = document.createElement("option")
            optionSelectLine.value = element;
            optionSelectLine.innerHTML = element;

            select.appendChild(optionSelectLine);
        });

        labelSelect.appendChild(select);

        divPlot.appendChild(labelSelect);
    }

    div.appendChild(divPlot);

    baseDiv.appendChild(div);
}


function generateData(JSONdata, currentIndex, nbOffset){
    var jsonSeriesData = [];
    var jsonLegendData = [];
    var jsonxAxisData = [];
    var jsonyAxisData = [];
    var cnt = 0;
    for (var source in JSONdata) {
        if (JSONdata.hasOwnProperty(source)) {
            for (var station in JSONdata[source]) {
                if (JSONdata[source].hasOwnProperty(station)) {
                    for (var parameter in JSONdata[source][station]) {
                        if (JSONdata[source].hasOwnProperty(station)) {
                            arrayData = []
                            JSONdata[source][station][parameter].forEach(element => arrayData.push(element[1]))
                            arrayTemp = []
                            JSONdata[source][station][parameter].forEach(element => arrayTemp.push(element[0]))
                            //console.log(arrayData);
                            nameOfParam = String(parameter)+" ("+String(station)+" - "+String(source)+") Filtre " + String(arrayCurrentIdx[currentIndex]);
                            jsonSeriesData.push({
                                "name": nameOfParam,
                                "xAxisIndex": currentIndex,
                                "yAxisIndex": nbOffset.offset+currentIndex+cnt,
                                "data": arrayData,
                                "type": "line",
                                "markLine": {
                                    data: []
                                }
                            });
                            if (!jsonxAxisData.length > 0) {
                                jsonxAxisData.push({
                                        "type": 'category',
                                        "axisTick": {
                                            "alignWithLabel": true
                                        },
                                        "axisLine": {
                                            "onZero": true,
                                        },
                                        "data": arrayTemp,
                                        axisLabel: {
                                            rotate: '45',
                                            interval: 50
                                        },
                                });
                            }
                            jsonyAxisData.push({
                                "type": 'value',
                                "name": String(parameter),
                                "position": currentIndex>0 ? 'right' : cnt>0 ? 'right' : 'left',
                                "alignTicks": true,
                                "offset": currentIndex>0 ? (nbOffset.offset+cnt)*80 : cnt>0 ? (cnt-1)*80 : 0,
                                "axisLine": {
                                    show: true,
                                },
                                "nameTextStyle": {
                                    "padding": currentIndex>0 ? [0, 0, 0, 70] : cnt>0 ? [0, 0, 0, 70] : [0, 70, 0, 0],
                                }
                            });
                            jsonLegendData.push(nameOfParam);
                            
                            cnt++;
                        }
                    }
                }
            }
        }
    }
    nbOffset.offset = cnt-1;
    jsonDataParsed = {"legend" : jsonLegendData, "series": jsonSeriesData, "xaxis": jsonxAxisData, "yaxis": jsonyAxisData};
    return jsonDataParsed
}

function drawChart(JSONdata) {

    if (myChart != null && myChart != '' && myChart != undefined) {
        myChart.dispose() //Solve the error reported by echarts dom already loaded
    }

    // Initialize the echarts instance based on the prepared dom
    myChart = echarts.init(document.getElementById('main'));
    myChart.showLoading();

    const colors = ['#5470C6', '#EE6666'];

    JSONgenerateData = [];
    nbOffset = {"offset": 0}
    JSONdata.forEach(function(element, currentIndex) {
        JSONgenerateData.push(generateData(element, currentIndex, nbOffset));
    });
    var legendData = []
    JSONgenerateData.forEach(element => element['legend'].forEach(e => legendData.push(e)));
    var seriesData = []
    JSONgenerateData.forEach(element =>element['series'].forEach(e => seriesData.push(e)));
    var xaxisData = []
    JSONgenerateData.forEach(element => element['xaxis'].forEach(e => xaxisData.push(e)));
    var yaxisData = []
    JSONgenerateData.forEach(element =>element['yaxis'].forEach(e => yaxisData.push(e)));

    // Specify the configuration items and data for the chart
    option = {
        tooltip: {
            trigger: 'axis'
        },
        toolbox: {
            feature: {
                dataView: { show: true, readOnly: false },
                dataZoom: { yAxisIndex: 'none'},
                magicType: { show: true, type: ['line', 'bar'] },
                restore: { show: true },
                saveAsImage: { show: true, restore: true }
            },
            padding: [0, 0, 0, 0]
        },
        legend: {
            type: 'scroll',
            data: legendData,
            padding: [0, 400, 400, 0]
        },
        grid: {
            containLabel: true,
            width: "auto",
            heigth: "800px"
        },
        xAxis: xaxisData,
        yAxis: yaxisData,
        dataZoom: [
            {
              type: 'inside',
              start: 0,
              end: 100
            },
            {
              start: 0,
              end: 100
            }
        ],
        series: seriesData,
    };

    myChart.hideLoading();
    // Display the chart using the configuration items and data just specified.
    myChart.setOption(option, true);

    echartSeriesNames = [];
    option.series.forEach(element => echartSeriesNames.push(element.name));

    addRuleOfEChartsParameters(echartSeriesNames);
}


