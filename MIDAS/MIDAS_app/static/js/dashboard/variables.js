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
    let div = L.DomUtil.create("div", "legend");
    let accordion = document.createElement("div");
    accordion.classList.add("accordion");
    accordion.id = "accordionExample";

    let accordionItem = document.createElement("div");
    accordionItem.classList.add("accordion-item");

    let accordionTitle1 = document.createElement("h2");
    accordionTitle1.classList.add("accordion-header");
    accordionTitle1.id = "headingOne";

    let accordionButton1 = document.createElement("button");
    accordionButton1.classList.add("accordion-button", "collapsed");
    accordionButton1.setAttribute("type", "button");
    accordionButton1.dataset.bsToggle = "collapse";
    accordionButton1.dataset.bsTarget = "#collapseLegend";
    accordionButton1.setAttribute("aria-expanded", "false");
    accordionButton1.setAttribute("aria-controls", "collapseLegend");

    accordionButton1.innerHTML = "Légende";

    let legendContent = document.createElement("div");
    legendContent.classList.add("accordion-collapse", "collapse");
    legendContent.id = "collapseLegend";
    legendContent.setAttribute("aria-labelledby", "headingOne");
    legendContent.dataset.bsParent = "accordionExample";

    let legendContentBody = document.createElement("div");
    legendContentBody.classList.add("accordion-body");
    legendContentBody.innerHTML = "TEST TEST TEST";

    legendContent.appendChild(legendContentBody);

    accordionTitle1.appendChild(accordionButton1);
    accordionItem.appendChild(accordionTitle1);
    accordionItem.appendChild(legendContent);
    accordion.appendChild(accordionItem);
    div.appendChild(accordion);

    
  
    return div;
  };
  
  legend.addTo(map);
