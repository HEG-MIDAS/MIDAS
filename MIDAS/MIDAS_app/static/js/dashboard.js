// Global variables
// Arrays that will contain the elements selected by the user
var sources = [];
var stations = [];
var parameters = [];
// JSON object
var options = {};
var option = {};
// state of the accordeon, is it always open ?
var fixed = true;

var result = []
var myChart;

// get todays date
var datePH = new Date();
// var date = datePH.getFullYear()+'-'+(datePH.getMonth() + 1)+'-'+datePH.getDate();
// var time = datePH.getHours() + ":" + datePH.getMinutes();
// var dateTime = date+' '+time;

const endingDate = document.getElementById("endingDate");
endingDate.value = datePH.toISOString().slice(0, -8);

// Get 30 days ago date
const startingDate = document.getElementById("startingDate");
datePH.setDate(datePH.getDate() - 30);
datePH.setHours(2);
datePH.setMinutes(0);
startingDate.value = datePH.toISOString().slice(0, -8);

//////////////////////////////////////////////////////////////////////////////////////
// Elements Dashboard Selection
//////////////////////////////////////////////////////////////////////////////////////

// Handles format the json body to send via the POST method to get the data requested
function requestData(e){
    var startingDateValue = document.getElementById('startingDate').value;
    var endingDateValue = document.getElementById('endingDate').value;
    // Check the dates of start and end are filled and that there is at least one element selected for source, station, and parameter
    // to be able to send the request
    if (startingDateValue != '' && endingDateValue != '' && sources.length > 0 && stations.length > 0 && parameters.length > 0) {
        // Format dates
        var startingDate = new Date(startingDateValue);
        var startingDateString = startingDate.getUTCFullYear() +"-"+ (startingDate.getUTCMonth()+1) +"-"+ startingDate.getUTCDate() + " " + startingDate.getUTCHours() + ":" + startingDate.getUTCMinutes() + ":" + startingDate.getUTCSeconds();
        var endingDate = new Date(endingDateValue);
        var endingDateString = endingDate.getUTCFullYear() +"-"+ (endingDate.getUTCMonth()+1) +"-"+ endingDate.getUTCDate() + " " + endingDate.getUTCHours() + ":" + endingDate.getUTCMinutes() + ":" + endingDate.getUTCSeconds();

        // Construct the json body of the POST method
        options = {'sources': sources, 'stations': stations, 'parameters': parameters, 'starting_date': startingDateString, 'ending_date': endingDateString}
        requestDataFetch(options)
    }
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
function select_source(e){
    var stationsAccordeon = document.getElementById('headingStations').getElementsByTagName('button')[0];
    // Check if the user selected or deselected a source
    if (e.checked) {
        // If the user selects a source
        // Enable accordeon component for stations
        stationsAccordeon.disabled = false;
        // Add source to source array
        sources.push(e.value);
        // Prepare json body to POST request
        options = {'sources': sources};
        requestStations(options);
        var cs = document.getElementById('buttonStations');
        // Open next accordeon if it is closed
        if (cs.getAttribute('aria-expanded') === 'false') {
            cs.click();
        }
    }
    else {
        // Deletes source from source array
        var index = sources.indexOf(e.value);
        if (index !== -1) {
            sources.splice(index, 1);
        }
        // If there is no sources selected
        if (sources.length == 0) {
            // Closes all open accordeons below
            var cs = document.getElementById('buttonStations');
            if (cs.getAttribute('aria-expanded') === 'true') {
                cs.click();
            }
            var cs = document.getElementById('buttonParameters');
            if (cs.getAttribute('aria-expanded') === 'true') {
                cs.click();
            }
            var cs = document.getElementById('buttonDates');
            if (cs.getAttribute('aria-expanded') === 'true') {
                cs.click();
            }
            // Clear stations and parameters arrays
            stations = [];
            parameters = [];
            // Disable the possibility to expand accordeon of stations and parameters
            stationsAccordeon.disabled = true;
            parametersAccordeon = document.getElementById('headingParameters').getElementsByTagName('button')[0];
            parametersAccordeon.disabled = true;
        }
        else{
            // Prepare json body to POST request for the sources left
            options = {'sources': sources};
            requestStations(options);
            if (!fixed) {
                // Open accordeon of stations
                var cs = document.getElementById('buttonStations');
                cs.click();
            }
        }
    }
}

// Function lauched when a station is selected or deselected by the user
// Adds or deletes the stations from the global array dedicated and enable the selection of parameters
// if there is at least one station selected
function select_station(e){
    var parametersAccordeon = document.getElementById('headingParameters').getElementsByTagName('button')[0];
    // Split the value to an array of elements (value of e is formed as => value="source station")
    var array_e_values = e.value.split(' ');
    // Check if the user selected or deselected a station
    if (e.checked) {
        // Add station value to its dedicated array
        stations.push(array_e_values.at(-1));
        // Prerare json body for POST request
        options = {'sources': sources, 'stations': stations};
        // If the user selects a stations
        // Enable accordeon component for parmeters
        parametersAccordeon.disabled = false;
        requestParameters(options)
        // Open parameters accordion if it's closed
        var cs = document.getElementById('buttonParameters');
        if (cs.getAttribute('aria-expanded') === 'false') {
            cs.click();
        }
    }
    else {
        // Deletes station from its array
        var index = stations.indexOf(array_e_values.at(-1));
        if (index !== -1) {
            stations.splice(index, 1);
        }
        if (stations.length == 0) {
            // If there is no more stations in the array, closes all accordeons below
            var cs = document.getElementById('buttonParameters');
            if (cs.getAttribute('aria-expanded') === 'true') {
                cs.click();
            }
            var cs = document.getElementById('buttonDates');
            if (cs.getAttribute('aria-expanded') === 'true') {
                cs.click();
            }
            // Set parameters array to empty
            parameters = [];
            // Disabled accordeons below
            parametersAccordeon.disabled = true;
            var datesAccordeon = document.getElementById('headingDates').getElementsByTagName('button')[0];
            datesAccordeon.disabled = true;
        }
        else{
            // Prepare json body to POST request for the stations left
            options = {'sources': sources, 'stations': stations};
            requestParameters(options)
            // Open next accordeon if the accordeons are not fixed
            if (!fixed) {
                var cs = document.getElementById('buttonParameters');
                cs.click();
            }
        }
    }
}

// Function lauched when a parameter is selected or deselected by the user
// Adds or deletes the parameters from the global array dedicated and enable the selection of dates
// if there is at least one parameter selected
function select_parameter(e){
    var datesAccordeon = document.getElementById('headingDates').getElementsByTagName('button')[0];
    // Split the value to an array of elements (value of e is formed as => value="source station1,station2 parameter")
    var array_e_values = e.value.split(' ');
    // Check if the user selected or deselected a parameter
    if (e.checked) {
        parameters.push(array_e_values.at(-1));
        // If the user selects a parameter
        // Enable accordeon component for dates
        datesAccordeon.disabled = false;
        // Open dates accordeon if it is closed
        var cs = document.getElementById('buttonDates');
        if (cs.getAttribute('aria-expanded') === 'false') {
            cs.click();
        }
    }
    else {
        // Delete parameter from its array
        var index = parameters.indexOf(array_e_values.at(-1));
        if (index !== -1) {
            parameters.splice(index, 1);
        }
        if (parameters.length == 0) {
            // If there are no paremeters left in the dedicated array
            // Closes and disable date accordeon
            var cs = document.getElementById('buttonDates');
            if (cs.getAttribute('aria-expanded') === 'true') {
                cs.click();
            }
            datesAccordeon.disabled = true;
        }
        else{
            // Open next accordeon if the accordeons are not fixed
            if (!fixed) {
                var cs = document.getElementById('buttonDates');
                cs.click();
            }
        }
    }
}

// Add CSRF into a constant to be used by the fetch requests
const csrf = document.querySelector('input[name="csrfmiddlewaretoken"]').value ;
// Request all the stations available for the selected sources
function requestStations(options){
    // Request station-dashboard view
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
        var accordionStations = document.getElementById("accordionStations");
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
            accInp.id = "flexCheck" + jsonData[i]['slug'];
            accInp.setAttribute('onclick', 'select_station(this)');
            // Create label
            const accLab = document.createElement("label");
            accLab.className = "form-check-label";
            accLab.setAttribute("for", "flexCheck" + jsonData[i]['slug']);
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
        if (stations.length > 0){
            for (var i = stations.length-1; i >= 0; --i) {
                // Check if the station is still available to be selected
                /*console.log(stations)
                console.log(stationsSlug)
                console.log(stations[i])
                console.log(stationsSlug.includes(stations[i]))
                */
                if (stationsSlug.includes(stations[i])){
                    //console.log(stations[i])
                    // Select the station box
                    document.getElementById("flexCheck"+stations[i]).checked = true;
                    // Request for the parameters of the box selected and will do the same stuff
                    requestParameters({'sources': sources, 'stations': stations[i]})
                }
                else {
                    // If the code enter here, it means that the station was not in the request so it is deleted from our stations' array 
                    stations.splice(i, 1);
                }
                //console.log(stations)
                //console.log(stationsSlug)
            }
        }
        // If there is no stations selected
        if (stations.length == 0) {
            var cs = document.getElementById('buttonParameters');
            // Check if the parameters div is expanded
            if (cs.getAttribute('aria-expanded') === 'true') {
                // Closes it
                cs.click();
            }
            // Remove all parameters of the array
            parameters = [];
            parametersAccordeon = document.getElementById('headingParameters').getElementsByTagName('button')[0];
            // Disabled the accordeon of parameters as there is no stations selected
            parametersAccordeon.disabled = true;
        }
    });
}

// Request all the paremeters available for the selected stations and sources
function requestParameters(options){
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
        var accordionParameters = document.getElementById("accordionParameters");
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
            accInp.id = "flexCheck" + jsonData[i]['slug'];
            accInp.setAttribute('onclick', 'select_parameter(this)');
            // Create label
            const accLab = document.createElement("label");
            accLab.className = "form-check-label";
            accLab.setAttribute("for", "flexCheck" + jsonData[i]['slug']);
            accLab.innerText = jsonData[i]['name'];
            // Happen children
            accDiv.appendChild(accInp);
            accDiv.appendChild(accLab);
            accordionParameters.appendChild(accDiv);

            // Add slug of the current paramter to our current parameter array
            parametersSlug.push(jsonData[i]['slug'])
        }

        // Check if there was paremeters selected
        if (parameters.length > 0){
            for (var i = parameters.length-1; i >= 0; --i) {
                // If the selected parameter is still in the request
                if (parametersSlug.includes(parameters[i])){
                    // Select it
                    document.getElementById("flexCheck"+parameters[i]).checked = true;
                }
                else {
                    // If the selected parameter is not in the request, delete it from our list of selected parameters
                    parameters.splice(i, 1);
                }
            }
        }
        // After checking if there is still selected parameters, we check if there is none
        if (parameters.length == 0) {
            parameters = [];
            var cs = document.getElementById('buttonDates');
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
    fetch('/request-data-dashboard/',{
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
        jsonData = JSON.parse(responseJSONData);
        document.getElementById("main").className = '';
        drawChart(jsonData)
    });
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


function addRuleOfEChartsParameters(){
    var baseDiv = document.getElementById("EchartsParameters");
    
    while (baseDiv.firstChild) {
        baseDiv.removeChild(baseDiv.firstChild);
    }

    const div = document.createElement("div");

    div.id = "EchartsViewParameters";
    const averageInp = document.createElement("input");
    averageInp.className = "form-check-input ";
    averageInp.type = "checkbox";
    averageInp.id = "CheckAverage";
    averageInp.setAttribute("onclick", "addMarkLineToEchartsPlot(this, 'average', 'Avg')");
    const averageLab = document.createElement("label");
    averageLab.className = "form-check-label lab-param-echarts";
    averageLab.setAttribute("for", "CheckAverage");
    averageLab.innerText = "Afficher la moyenne";

    div.appendChild(averageInp);
    div.appendChild(averageLab);

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

    div.appendChild(medianInp);
    div.appendChild(medianLab);

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

    div.appendChild(minInp);
    div.appendChild(minLab);

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

    div.appendChild(maxInp);
    div.appendChild(maxLab);
    
    baseDiv.appendChild(div);
}

function generateData(JSONdata){
    var jsonSeriesData = []
    var jsonLegendData = []
    for (var source in JSONdata) {
        if (JSONdata.hasOwnProperty(source)) {
            for (var station in JSONdata[source]) {
                if (JSONdata[source].hasOwnProperty(station)) {
                    for (var parameter in JSONdata[source][station]) {
                        if (JSONdata[source].hasOwnProperty(station)) {
                            jsonSeriesData.push({
                                "name": String(parameter)+" ("+String(station)+" - "+String(source)+")",
                                "data": JSONdata[source][station][parameter],
                                "type": "line",
                                "markLine": {
                                    data: []
                                }
                            });
                            jsonLegendData.push(String(parameter)+" ("+String(station)+" - "+String(source)+")");
                        }
                    }
                }
            }
        }
    }
    jsonDataParsed = {"legend" : jsonLegendData, "series": jsonSeriesData};
    return jsonDataParsed
}

function drawChart(JSONdata) {

    if (myChart != null && myChart != '' && myChart != undefined) {
        myChart.dispose() //Solve the error reported by echarts dom already loaded
    }

    // Initialize the echarts instance based on the prepared dom
    myChart = echarts.init(document.getElementById('main'));

    const colors = ['#5470C6', '#EE6666'];

    JSONgenerateData = generateData(JSONdata);

    // Specify the configuration items and data for the chart
    option = {
        tooltip: {
            trigger: 'axis'
        },
        legend: {
            type: 'scroll',
            data: JSONgenerateData['legend']
        },
        grid: {
            containLabel: true
        },
        xAxis: {type: "time"},
        yAxis: {type: 'value'},
        series: JSONgenerateData['series'],
    };

    // Display the chart using the configuration items and data just specified.
    myChart.setOption(option, true);

    addRuleOfEChartsParameters();
}


