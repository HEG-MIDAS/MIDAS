//////////////////////////////////////////////////////////////////////////////////////
// Manage the download of the data
//////////////////////////////////////////////////////////////////////////////////////

function downloadData(JSONDataToCSV) {
   
    for (var elementNumber in JSONDataToCSV) {
        CSVHeader = []
        data = []
        if (JSONDataToCSV.hasOwnProperty(elementNumber)) {
            for (var source in JSONDataToCSV[elementNumber]) {
                if (JSONDataToCSV[elementNumber].hasOwnProperty(source)) {
                    for (var station in JSONDataToCSV[elementNumber][source]) {
                        if (JSONDataToCSV[elementNumber][source].hasOwnProperty(station)) {
                            for (var parameter in JSONDataToCSV[elementNumber][source][station]) {
                                if (JSONDataToCSV[elementNumber][source][station].hasOwnProperty(parameter)) {
                                    // If the header is empty
                                    if (CSVHeader.length == 0){
                                        // Create header with date and combination of source-station-parameter as name for the data
                                        CSVHeader = ["date", source+"-"+station+"-"+parameter];
                                        // Copy the 2d array
                                        data = JSONDataToCSV[elementNumber][source][station][parameter]
                                    }
                                    else {
                                        CSVHeader.push(source+"-"+station+"-"+parameter)
                                        // Extract only the value of the parameter from the 2d array and create a new array
                                        dataParameter = JSONDataToCSV[elementNumber][source][station][parameter].map(a => a[1]).flat(1)
                                        // Add new value to already existing data
                                        for (let i = 0; i < data.length; i++) {
                                            data[i].push(dataParameter[i]);
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
            let csv = CSVHeader.map(val => `'${val}'`).join(",")+"\n";
            for (let i = 0; i < data.length; i++) {
                csv += (data[i].map(val => `'${val}'`).join(",")+"\n");
            }
            let csvContent = "data:text/csv;charset=utf-8," + csv
            var encodedUri = encodeURI(csvContent);
            var link = document.createElement("a");
            link.setAttribute("href", encodedUri);
            link.setAttribute("download", "DataDashboard_Filter"+(parseInt(elementNumber)+1)+"_"+new Date()+".csv");
            document.body.appendChild(link); // Required for FF

            link.click();
        }
    }
}

//////////////////////////////////////////////////////////////////////////////////////
// Manage the display between Advanced or Map mode
//////////////////////////////////////////////////////////////////////////////////////

function handleAdvancedOrMap(element) {
    var advanced_disp = document.getElementById("midas-container-advanced");
    var map_disp = document.getElementById("midas-container-map");

    if (window.getComputedStyle(map_disp).visibility === "hidden") {
        advanced_disp.style.visibility = 'hidden';
        advanced_disp.style.display = 'none';
        map_disp.style.visibility = 'visible';
        map_disp.style.display = 'block';
        map.invalidateSize();
        element.innerHTML = 'Avancé';
    }
    else {
        map_disp.style.visibility = 'hidden';
        map_disp.style.display = 'none';
        advanced_disp.style.visibility = 'visible';
        advanced_disp.style.display = 'inline';
        element.innerHTML = 'Map';
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

window.addEventListener("load", addResearch(false));


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