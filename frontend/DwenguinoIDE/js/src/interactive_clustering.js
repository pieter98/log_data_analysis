var interactive_clustering = {
    init: function(){
        DwenguinoBlockly.recording_now = false;
        DwenguinoBackgroundSimulation.setupEnvironment("randomSimulatedEnvironment");
        $("#record_interactions_button").click(function(){
            var functionalDataVector = DwenguinoBackgroundSimulation.generateSimulatedData(30000, 1);
            console.log(functionalDataVector);
        })
    },


    plotClusteringData: function(){
      var myPlot = document.getElementById("db_clustering_plot");
      var xCoords = [];
      var yCoords = [];
      var zCoords = [];
      var cCoords = [];
      this.tsne_data.forEach(function(entry){
        //console.log(entry);
        xCoords.push(entry[0][0]);
        yCoords.push(entry[0][1]);
        zCoords.push(entry[0][2]);
        if (entry[1] != -1){
            console.log("recorede element with label");
        }
        var rgb = hsluv.hsluvToRgb([(entry[1]+1)*50, 100, 50]);
        //cCoords.push(entry[3]*4)
        cCoords.push(Colors.rgb2hex(Math.round(rgb[0] * 255), Math.round(rgb[1] * 255), Math.round(rgb[2] * 255)));
      });
      var data = [];
      var scatterPoints = {x:xCoords, y:yCoords, z:zCoords, type:"scatter3d", mode:"markers", marker:{size:7, color: cCoords}};
      this.cluster_distance_pairs.forEach(function(entry){
        var trace = {x: [entry[0][0], entry[1][0]], y: [entry[0][1], entry[1][1]], z: [entry[0][2], entry[1][2]],
        mode: 'lines', type: 'scatter3d', line: {width: 5}};
        data.push(trace);
      });
      data.push(scatterPoints);
      layout = { hovermode:'closest', title:'Click on Points'};
      Plotly.newPlot('db_clustering_plot', data, layout);
      myPlot.on('plotly_click', function(eventdata){
        console.log(eventdata);
        var pointIndex = eventdata.points[0].pointNumber;
        console.log(pointIndex);
        ClusteringAnalysis.getCodeTreeForIndex(pointIndex);
        if (ClusteringAnalysis.data_reduced == true){
            ClusteringAnalysis.getReducedVectorForIndex(pointIndex);
        }
      });

    },
    rainbow: function(value) {
        var h = (1.0 - value) * 240
        return "hsl(" + h + ", 100%, 50%)";
    },
    getCodeTreeForIndex: function(index){
      $.ajax({
          type: "GET",
          url: "http://localhost:20042/get_code_tree_for_index?experimentId=" + ClusteringAnalysis.experimentId + "&index=" + index,
          datatype: "json"},
      ).done(function(data){
          ClusteringAnalysis.code_tree = JSON.parse(data);
          console.log(ClusteringAnalysis.code_tree);
          ClusteringAnalysis.workspace.clear();
          var xml = Blockly.Xml.textToDom(ClusteringAnalysis.code_tree);
          Blockly.Xml.domToWorkspace(xml, ClusteringAnalysis.workspace);
      }).fail(function(response, status)  {
          console.warn('Failed to fetch sessionIdList:', status);
      });
    },
};

$(document).ready(function(){
    interactive_clustering.init();
})