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
datePH.setHours(0);
datePH.setMinutes(0);
startingDate.value = datePH.toISOString().slice(0, -8);

//////////////////////////////////////////////////////////////////////////////////////
// Map
//////////////////////////////////////////////////////////////////////////////////////

var map = L.map('map').setView([46.2026, 6.1235], 12);
map.zoomControl.setPosition('topright');
        map.addLayer(new L.TileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
            {attribution:'Map data © <a href="http://openstreetmap.org">OpenStreetMap</a> contributors'}
        ));

L.DomEvent.disableClickPropagation(document.getElementById("map-menu"));
L.DomEvent.disableScrollPropagation(document.getElementById("map-menu"));