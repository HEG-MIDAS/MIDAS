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
// Manage the display between Manual or Map mode
//////////////////////////////////////////////////////////////////////////////////////

function handleManualOrMap(element) {
    var manual_disp = document.getElementById("midas-container-manual");
    var map_disp = document.getElementById("midas-container-map");

    if (window.getComputedStyle(manual_disp).visibility === "hidden") {
        map_disp.style.visibility = 'hidden';
        map_disp.style.display = 'none';
        manual_disp.style.visibility = 'visible';
        manual_disp.style.display = 'inline';
        element.innerHTML = 'Map';
    }
    else {
        manual_disp.style.visibility = 'hidden';
        manual_disp.style.display = 'none';
        map_disp.style.visibility = 'visible';
        map_disp.style.display = 'block';
        map.invalidateSize();
        element.innerHTML = 'Manual';
    }
}