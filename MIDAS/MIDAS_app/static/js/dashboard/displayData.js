// Author : David Nogueiras Blanco
// Last edition : 21.03.2024
// Project : MIDAS (HEG)

//////////////////////////////////////////////////////////////////////////////////////
// Echarts
//////////////////////////////////////////////////////////////////////////////////////

// Handles the responsiveness of the echarts plot
function resetEchartsPlot() {
    if (myChart != null && myChart != '' && myChart != undefined) {
        myChart.dispose() //Solve the error reported by echarts dom already loaded
    }

    // Initialize the echarts instance based on the prepared dom
    myChart = echarts.init(document.getElementById(myChartMainID));

    // Display the chart using the configuration items and data just specified.
    myChart.setOption(option, true);
}

window.addEventListener('resize', resetEchartsPlot);

// Draw lines on echarts plot following the requested parameter
function addMarkLineToEchartsPlot(e, typeString, nameString){
    if (e.checked) {
        for (var i=0; i < option.series.length; i++) {
            if (!option.series[i].markLine.data.some(e => e.type === typeString)){
                option.series[i].markLine.data.push({ type: typeString, name: nameString });
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

// 
function changeLinePlotDisplay(name, displayType){
    option.series.forEach(function(element, currentIndex) {
        if (element.name == name){
            element.type = displayType;
        }
    });

    resetEchartsPlot();
}

// Change the display of the extremes values on Y axis
function changeXtremeValuesDisplayYAxis(value, filterWorkingOn, changeMax=true){
    if (value.length == 0){
        value = undefined;
    }
    if (changeMax){
        option.yAxis[filterWorkingOn].max = value;
    }
    else {
        option.yAxis[filterWorkingOn].min = value;
    }

    resetEchartsPlot();
}

// Add the possibility to display mean, max, min on the plotted data
function addRuleOfEChartsParameters(idChart, echartSeriesNames){
    let baseDiv = document.getElementById("EchartsParameters");
    if (idChart == "mainMap"){
        baseDiv = document.getElementById("EchartsParametersMap");
    }
    
    while (baseDiv.firstChild) {
        baseDiv.removeChild(baseDiv.firstChild);
    }

    const div = document.createElement("div");
    div.classList.add("container");
    div.id = "EchartsViewParameters";

    const title = document.createElement("div");
    title.innerHTML = "Paramètres d'affichage <i class='fa-solid fa-chevron-down'></i>";

    // title.href = "#collapseEchartsParameters";
    title.classList.add("echartsParametersCollapse", "echartsParametersCollapseOff");
    title.id = "echartsParametersCollapse";
    title.dataset.bsToggle="collapse";
    title.dataset.bsTarget = "#collapseEchartsParameters"
    title.type="button";
    title.setAttribute("aria-expanded", "false");
    title.setAttribute("aria-controls", "collapseEchartsParameters");
    title.setAttribute("onclick", "animateChevron()");

    div.appendChild(title);

    const divCollapse = document.createElement("div");
    divCollapse.classList.add("collapse");
    divCollapse.id = "collapseEchartsParameters";

    // Creates some buttons that allow to show statistical values on the echarts graph

    const divStats = document.createElement("div");
    divStats.classList.add("row");
    divStats.id = "EchartsViewParametersStatistics";

    const averageDiv = document.createElement("div");
    averageDiv.classList.add("col");
    const averageInp = document.createElement("input");
    averageInp.className = "form-check-input ";
    averageInp.type = "checkbox";
    averageInp.id = "CheckAverage";
    averageInp.setAttribute("onclick", "addMarkLineToEchartsPlot(this, 'average', 'Avg')");
    const averageLab = document.createElement("label");
    averageLab.className = "form-check-label lab-param-echarts";
    averageLab.setAttribute("for", "CheckAverage");
    averageLab.innerText = "Afficher la moyenne";

    averageDiv.appendChild(averageInp);
    averageDiv.appendChild(averageLab);

    divStats.appendChild(averageDiv);

    // Median button
    const medianDiv = document.createElement("div");
    medianDiv.classList.add("col");
    const medianInp = document.createElement("input");
    medianInp.className = "form-check-input";
    medianInp.type = "checkbox";
    medianInp.id = "CheckMedian";
    medianInp.setAttribute("onclick", "addMarkLineToEchartsPlot(this, 'median', 'Median')");
    const medianLab = document.createElement("label");
    medianLab.className = "form-check-label lab-param-echarts";
    medianLab.setAttribute("for", "CheckMedian");
    medianLab.innerText = "Afficher la médiane";

    medianDiv.appendChild(medianInp);
    medianDiv.appendChild(medianLab);

    divStats.appendChild(medianDiv);

    // Max button
    const maxDiv = document.createElement("div");
    maxDiv.classList.add("col");
    const maxInp = document.createElement("input");
    maxInp.className = "form-check-input";
    maxInp.type = "checkbox";
    maxInp.id = "CheckMax";
    maxInp.setAttribute("onclick", "addMarkLineToEchartsPlot(this, 'max', 'Max')");
    const maxLab = document.createElement("label");
    maxLab.className = "form-check-label lab-param-echarts";
    maxLab.setAttribute("for", "CheckMax");
    maxLab.innerText = "Afficher le maximum";

    maxDiv.appendChild(maxInp);
    maxDiv.appendChild(maxLab);

    divStats.appendChild(maxDiv);

    // Min button
    const minDiv = document.createElement("div");
    minDiv.classList.add("col");
    const minInp = document.createElement("input");
    minInp.className = "form-check-input";
    minInp.type = "checkbox";
    minInp.id = "CheckMin";
    minInp.setAttribute("onclick", "addMarkLineToEchartsPlot(this, 'min', 'Min')");
    const minLab = document.createElement("label");
    minLab.className = "form-check-label lab-param-echarts";
    minLab.setAttribute("for", "CheckMin");
    minLab.innerText = "Afficher le minimum";

    minDiv.appendChild(minInp);
    minDiv.appendChild(minLab);

    divStats.appendChild(minDiv);
    
    divCollapse.appendChild(divStats);

    const separationStatsFilters = document.createElement("hr");
    separationStatsFilters.classList.add("solid");

    divCollapse.appendChild(separationStatsFilters);

    // Create a select for each element displayed that allow to change the line to bar or bar to line

    const divPlot = document.createElement("div");
    divPlot.id = "EchartsViewParametersPlot";

    for (var i=0; i<echartSeriesNames.length; i++){

        const divRow = document.createElement("div");
        divRow.classList.add("row");


        const divColLabel = document.createElement("div");
        divColLabel.classList.add("col-auto");
        divColLabel.classList.add("label-display-parameters");

        const labelElement = document.createElement("p");
        labelElement.innerHTML = echartSeriesNames[i]+" :";

        divColLabel.appendChild(labelElement);
        divRow.appendChild(divColLabel);


        const divColSelect = document.createElement("div");
        divColSelect.classList.add("col-auto");

        const labelSelect = document.createElement("label");
        labelSelect.classList.add("label-select-type-display");
        //labelSelect.innerHTML = echartSeriesNames[i]+" :";

        const select = document.createElement("select");
        select.classList.add("form-select");
        select.classList.add("select-type-display");
        select.setAttribute("onchange", "changeLinePlotDisplay('"+echartSeriesNames[i]+"', this.value)");

        TYPESPLOTGRAPH.forEach(function(element){
            const optionSelectLine = document.createElement("option")
            optionSelectLine.value = element;
            optionSelectLine.innerHTML = element;

            select.appendChild(optionSelectLine);
        });

        labelSelect.appendChild(select);
        divColSelect.appendChild(labelSelect);
        divRow.appendChild(divColSelect);

        // Handles creation of input group to modify max value

        const divMaxInput = document.createElement("div");
        divMaxInput.classList.add("input-group");
        divMaxInput.classList.add("mb-3");
        divMaxInput.classList.add("col");

        const spanMax = document.createElement("span");
        spanMax.classList.add("input-group-text");
        spanMax.innerHTML = "Max";

        divMaxInput.appendChild(spanMax);

        const maxInput = document.createElement("input");
        maxInput.classList.add("form-input");
        maxInput.classList.add("form-control");
        maxInput.setAttribute("type", "number");
        maxInput.setAttribute("oninput", "changeXtremeValuesDisplayYAxis(this.value, "+i+")");

        divMaxInput.appendChild(maxInput);

        divRow.appendChild(divMaxInput);

        // Handles creation of input group to modify min value

        const divMinInput = document.createElement("div");
        divMinInput.classList.add("input-group");
        divMinInput.classList.add("col");
        divMinInput.classList.add("mb-3");

        const spanMin = document.createElement("span");
        spanMin.classList.add("input-group-text");
        spanMin.innerHTML = "Min";

        divMinInput.appendChild(spanMin);

        const minInput = document.createElement("input");
        minInput.classList.add("form-input");
        minInput.classList.add("form-control");
        minInput.setAttribute("type", "number");
        minInput.setAttribute("oninput", "changeXtremeValuesDisplayYAxis(this.value, "+i+", false)");

        divMinInput.appendChild(minInput);

        divRow.appendChild(divMinInput);

        divPlot.appendChild(divRow);

        if (i+1 < echartSeriesNames.length){
            const separationFilterFilter = document.createElement("hr");
            separationFilterFilter.classList.add("dashed");

            divPlot.appendChild(separationFilterFilter);
        }
    }

    divCollapse.appendChild(divPlot);
    div.appendChild(divCollapse);

    baseDiv.appendChild(div);
}

// Format the JSON data to be rendered in an object that can be used for display by echarts
function generateData(JSONdata, currentIndex, nbOffset, hasFilters){
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
                            var arrayData = []
                            JSONdata[source][station][parameter].forEach(element => arrayData.push(element[1]))
                            var arrayTemp = []
                            JSONdata[source][station][parameter].forEach(element => arrayTemp.push(element[0]))
                            var nameOfParam = String(parameter)+" ("+String(station)+" - "+String(source)+")";
                            if (hasFilters){
                                nameOfParam.concat(" Filtre " + (arrayCurrentIdx.indexOf(arrayCurrentIdx[currentIndex])+1).toString());
                            }
                            jsonSeriesData.push({
                                "name": nameOfParam,
                                "xAxisIndex": currentIndex,
                                "yAxisIndex": nbOffset.offset+currentIndex+cnt,
                                "data": arrayData,
                                "type": "line",
                                "markLine": {
                                    data: []
                                },
                                "zlevel": nbOffset.offset+currentIndex+cnt,
                                "z": nbOffset.offset+currentIndex+cnt
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

                                            large: true
                                        },
                                });
                            }
                            jsonyAxisData.push({
                                "max": undefined,
                                "min": undefined,
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
    var jsonDataParsed = {"legend" : jsonLegendData, "series": jsonSeriesData, "xaxis": jsonxAxisData, "yaxis": jsonyAxisData};
    return jsonDataParsed
}

// Draw the chart in the page
function drawChart(JSONdata, mainID) {

    myChartMainID = mainID

    if (myChart != null && myChart != '' && myChart != undefined) {
        myChart.dispose() //Solve the error reported by echarts dom already loaded
    }

    // Initialize the echarts instance based on the prepared dom
    myChart = echarts.init(document.getElementById(myChartMainID));
    //myChart.showLoading();

    const colors = ['#5470C6', '#EE6666'];

    var JSONgenerateData = [];
    var nbOffset = {"offset": 0}
    JSONdata.forEach(function(element, currentIndex) {
        JSONgenerateData.push(generateData(element, currentIndex, nbOffset, mainID=="mainAdvanced"));
    });
    var legendData = []
    JSONgenerateData.forEach(element => element['legend'].forEach(e => legendData.push(e)));
    var seriesData = []
    JSONgenerateData.forEach(element =>element['series'].forEach(e => seriesData.push(e)));
    var xaxisData = []
    JSONgenerateData.forEach(element => element['xaxis'].forEach(e => xaxisData.push(e)));
    var yaxisData = []
    JSONgenerateData.forEach(element =>element['yaxis'].forEach(e => yaxisData.push(e)));

    const checkDivAlert =  document.getElementById("divAlert");
    if (checkDivAlert!=null) {
        checkDivAlert.remove();
    }

    for (let i = 0; i < JSONdata.length; i++) {
        for (var key in JSONdata[i]) {
            if (JSONdata[i].hasOwnProperty(key)) {
                for (var station in JSONdata[i][key]) {
                    if (JSONdata[i][key].hasOwnProperty(station)) {
                        if (Object.keys(JSONdata[i][key][station]).length === 0) {
                            let divAlert = document.createElement("div");
                            divAlert.classList.add("alert", "alert-warning", "alert-dismissible", "fade", "show", "divAlert");
                            divAlert.id = "divAlert".concat(station);
                            divAlert.role = "alert";

                            let textAlert = document.createElement("p");
                            textAlert.innerHTML = "Aucune donnée trouvée pour la station : <strong>".concat(station, "</strong>")

                            let buttonAlert = document.createElement("button");
                            buttonAlert.classList.add("btn-close");
                            buttonAlert.type = "button";
                            buttonAlert.dataset.bsDismiss = "alert";
                            buttonAlert.setAttribute("aria-label", "Close");

                            divAlert.appendChild(textAlert);
                            divAlert.appendChild(buttonAlert);
                            document.getElementsByTagName("body")[0].appendChild(divAlert);
                        }
                    }
                }
            }
        }
    }

    setTimeout(deleteSmoothlyAlertDiv, 2000);

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

    //myChart.hideLoading();
    // Display the chart using the configuration items and data just specified.
    myChart.setOption(option, true);

    var echartSeriesNames = [];
    option.series.forEach(element => echartSeriesNames.push(element.name));

    addRuleOfEChartsParameters(mainID, echartSeriesNames);
}
