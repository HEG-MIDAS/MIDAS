// Author : David Nogueiras Blanco
// Last edition : 21.03.2024
// Project : MIDAS (HEG)

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
var myChartMainID = '';

//////////////////////////////////////////////////////////////////////////////////////
// Define default dates of data research
//////////////////////////////////////////////////////////////////////////////////////

// get todays date
var dateEnd = new Date();
var dateStart = new Date();
// var date = datePH.getFullYear()+'-'+(datePH.getMonth() + 1)+'-'+datePH.getDate();
// var time = datePH.getHours() + ":" + datePH.getMinutes();
// var dateTime = date+' '+time;

// Get 30 days ago date
dateStart.setDate(dateEnd.getDate() - 30);
dateStart.setHours(0);
dateStart.setMinutes(0);

// ADVANCED
const startingDate = document.getElementById("startingDate0");
startingDate.value = dateStart.toISOString().slice(0, -8);

const endingDate = document.getElementById("endingDate0");
endingDate.value = dateEnd.toISOString().slice(0, -8);

// MAP
let lastStartingDateMap = dateStart.toISOString().slice(0, -8);
let lastEndingDateMap = dateEnd.toISOString().slice(0, -8);

const startingDateMap = document.getElementById("startingDateMap");
startingDateMap.value = lastStartingDateMap

const endingDateMap = document.getElementById("endingDateMap");
endingDateMap.value = lastEndingDateMap

//////////////////////////////////////////////////////////////////////////////////////
// Map
//////////////////////////////////////////////////////////////////////////////////////

var map = L.map('map').setView([46.2026, 6.1235], 12);
map.zoomControl.setPosition('topright');
        map.addLayer(new L.TileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
            // {attribution:'Map data © <a href="http://openstreetmap.org">OpenStreetMap</a> contributors'}
        ));

L.DomEvent.disableClickPropagation(document.getElementById("map-menu"));
L.DomEvent.disableScrollPropagation(document.getElementById("map-menu"));

/*Legend specific*/
var legend = L.control({ position: "bottomright" });

legend.onAdd = function(map) {
    let divLegend = L.DomUtil.create("div", "Légende");
    divLegend.classList.add("btn-group", "dropup", "legend");
    divLegend.id = "divLegend";
    divLegend.hidden = true;

    let dropupButton = document.createElement("button");
    dropupButton.type = "button";
    dropupButton.classList.add("btn", "btn-danger", "dropdown-toggle");
    dropupButton.dataset.bsToggle="dropdown";
    dropupButton.dataset.bsAutoClose = "outside";
    dropupButton.setAttribute("aria-expanded", "false");
    dropupButton.innerHTML = "Légende";
    dropupButton.id = "dropdownMenuButtonLegend";

    let listLegend = document.createElement("ul");
    listLegend.classList.add("dropdown-menu");
    listLegend.setAttribute("aria-labelledby", "dropdownMenuButtonLegend");

    let elementListLegend = document.createElement("li");
    elementListLegend.classList.add("dropdown-item-text");
    elementListLegend.innerHTML = "";

    listLegend.appendChild(elementListLegend);
    divLegend.appendChild(dropupButton);
    divLegend.appendChild(listLegend);

    return divLegend;
};
  
legend.addTo(map);

// Disable click and scroll on divLegend
L.DomEvent.disableClickPropagation(document.getElementById("divLegend"));
L.DomEvent.disableScrollPropagation(document.getElementById("divLegend"));