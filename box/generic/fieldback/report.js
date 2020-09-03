var moment = require('moment');
////    Startup Initialization
var sql = 'select connected_time/60 as value1, tx_bytes/1000000 as value2,hour as xaxis,hour from connections';
var label1 = "Time Min";
var label2 = "Bytes MB"
$( '#hour' ).addClass('chosen');
$( '#usage' ).addClass('chosen');


///////////   Button click action routines //////////////
var xAxisUnit = "day"
var pdEnd = document.getElementById('pdEnd');
var pdStart = document.getElementById('pdStart');

function xAxis(elem){
  var clickedId = elem.id;
  $( ".chooseAxis" ).removeClass('chosen');
  $( '#'+ clickedId ).addClass('chosen');
  xAxisUnit = clickedId;
  switch( clickedId ){
    case "hour":
        sql = 'select host_num, hour,sum(connected_time),sum(tx_bytes) from connections group by year,doy,hour'; 
       pdEnd.innerHTML - moment().format('l');
       pdStartinnerHTML - moment().format('l');
       break;
     case "day":
       break;
     case "week":
       break;
     case "month":
       break;
     default:
       break;
  }
}
$(document).ready(function () {
   showGraph();
});


//////////////// Graph.js ///////////////////////////
function showGraph(){
    $.post("select.php?sql=" + sql,function (data){
        dataDict = JSON.parse(data);
        console.log(dataDict);
        var name = [];
        var bar1 = [];
        var bar2 = [];
        var bar2Max = 0;

        for (var i=0;i<dataDict.length;i++) {
            name.push(dataDict[i].xaxis);
            bar1.push(dataDict[i].value1);
            var bar2Val = dataDict[i].value2
            if ( bar2Val < bar2Max) bar2Max = bar2Val;
            bar2.push(bar2Val);
        }
        // scale value2
        var trial = bar2Max;
        scaleFactor = 1; 
        while (trial > 1000){
            trial = trial / 1000;
            var scaleFactor = scaleFactor * 1000;
        }
        var chartdata = {
            labels: name,
            datasets: [
                {
                    label: label1,
                    backgroundColor: 'Blue',
                    yAxisID: 'A',
                    data: bar1
                },
                {
                    label: label2,
                    backgroundColor: 'Green',
                    yAxisID: 'B',
                    data: bar2
                }
            ]
        };

        var graphTarget = $("#graphCanvas");

        var barGraph = new Chart(graphTarget, {
            type: 'bar',
            data: chartdata,
            options: {
                scales: {
                  yAxes: [{
                    id: 'A',
                    type: 'linear',
                    position: 'left'
                  }, {
                    id: 'B',
                    type: 'linear',
                    position: 'right'
                  }]
                }
              }
        });
  });
}
