//////////////////////////////////////////////////////////////////////////////////////
// Fetch requests to get data Advanced part
//////////////////////////////////////////////////////////////////////////////////////

// Add CSRF into a constant to be used by the fetch requests
const csrf = document.querySelector('input[name="csrfmiddlewaretoken"]').value ;
// Request all the stations available for the selected sources
async function requestStations(options, idx){
    // Request station-dashboard view
    var index = arrayCurrentIdx.indexOf(idx);
    await fetch('/stations-dashboard/',{
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
        console.log(jsonData.length)
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
        if (index != -1 && stations[index].length > 0){
            for (var i = stations[index].length-1; i >= 0; --i) {
                // Check if the station is still available to be selected
                if (stationsSlug.includes(stations[index][i])){
                    // Select the station box
                    document.getElementById("flexCheck"+stations[index][i]+idx.toString()).checked = true;
                    // Request for the parameters of the box selected and will do the same stuff
                }
                else {
                    // If the code enter here, it means that the station was not in the request so it is deleted from our stations' array 
                    stations[index].splice(i, 1);
                }
            }
            requestParameters({'sources': sources[index], 'stations': stations[index]}, idx)
        }
        // If there is no stations selected
        if (index == -1 || stations[index].length == 0) {
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
        // Array that will serve to know which parameters were in the request (we will use the slug)
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
            // Create information bouton
            const accInf = document.createElement("button");
            accInf.type = "button";
            accInf.className = "btn popover-btn";
            accInf.setAttribute("data-bs-container", "body");
            accInf.setAttribute("data-bs-toggle", "popover");
            accInf.setAttribute("data-bs-trigger", "hover focus");
            accInf.setAttribute("data-bs-placement", "top");
            accInf.setAttribute("data-bs-html", "true");
            accInf.setAttribute("title", jsonData[i]['infos'])
            accInf.setAttribute("data-bs-content",
                
                "Source(s) : "+[...new Set(jsonData[i]['source'].split(","))].map(e => `<span class="badge bg-primary">`+e+`</span>`).join(' ')+"<br>"
                +"Station(s) : "+[...new Set(jsonData[i]['station'].split(","))].map(e => `<span class="badge bg-primary">`+e+`</span>`).join(' ')+"<br>"
                );
            accInf.innerHTML = `<i class="fas fa-info-circle"></i>`;

            // Happen children
            accDiv.appendChild(accInp);
            accDiv.appendChild(accLab);
            accDiv.appendChild(accInf);
            accordionParameters.appendChild(accDiv);

            // Activate the popovers created
            [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]')).map(function (tE) {
                return new bootstrap.Popover(tE, {trigger: 'hover focus'});
            });

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
async function requestDataFetch(options){
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
    }).catch(error => console.log(error));
}

//////////////////////////////////////////////////////////////////////////////////////
// Fetch requests to get data Map part
//////////////////////////////////////////////////////////////////////////////////////

async function requestStationsSimplified(options){
    // Request station-dashboard view
    return fetch('/stations-dashboard/',{
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
        return JSON.parse(responseJSONData);
    });
}

// Request all the paremeters available for the selected stations and sources
async function requestParametersSimplified(options){
    // Request parameters to view parameters-dashboard
    return fetch('/parameters-dashboard/',{
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
        return JSON.parse(responseJSONData);
    });
}
