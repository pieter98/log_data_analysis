var interactive_clustering = {
    experimentId: "_test_of_interactive_clustering",
    collectionLabel: "",
    embedding_dims: 2,
    dimension_names: ["scatter2d", "scatter3d"],
    viewing: 0,
    measuringState: 0,
    vector1: 0,
    vector2: 0,
    vector3: 0,
    init: function(){
        DwenguinoBlockly.recording_now = false;
        this.getInteractiveClusteringCollectionNames();
        DwenguinoSimulation.setupEnvironment("randomSimulatedEnvironment");
        $("#record_interactions_button").click(function(){
            var xml = Blockly.Xml.workspaceToDom(DwenguinoBlockly.workspace);
            var xmlString = Blockly.Xml.domToText(xml);
            interactive_clustering.handleFunctionalClustering(xmlString);
        });
        $("#visualize_interactions_button").click(function(){
            // Send request to server with empty code string. In this case the server doesn't record anything
            // It only visualizes the existing data in the selected collection.
            interactive_clustering.handleFunctionalClustering("");
        });
        $("#collection-label").on('input',function(e){
            interactive_clustering.collectionLabel = $(this).val();
        });
        $("#embedding_dims").on('change',function(e){
            interactive_clustering.embedding_dims = parseInt($(this).val());
        });
        $("#view_measure_distance_button").click(function(){
            interactive_clustering.measuringState = 0;
            if (interactive_clustering.viewing == 0){
                interactive_clustering.viewing = 1;
                $("#view_measure_distance_button").text("correlation");
            } else if (interactive_clustering.viewing == 1){
                interactive_clustering.viewing = 2;
                $("#view_measure_distance_button").text("distance");
            } else if (interactive_clustering.viewing == 2) {
                interactive_clustering.viewing = 0;
                $("#view_measure_distance_button").text("viewing");
            }
        });
        this.embedding_dims = parseInt($("#embedding_dims").val());

    },
    getInteractiveClusteringCollectionNames: function(){
        $.ajax({
                type: "GET",
                url: "http://localhost:20042/get_interactive_clustering_collection_names"
                },
            ).done(function(data){
                console.log(data);
                collection_names = JSON.parse(data);
                $.each(collection_names, function(i, element){
                    $("#collection_labels").append($("<option>").attr("value", element).text(element));
                })
            }).fail(function(response, status)  {
                console.warn('Failed to fetch sessionIdList:', status);
            });
    },

    handleFunctionalClustering: function(xmlString){
        try {
            var label = $("#label").val();
            var steplabel = $("#steplabel").val();
            var pathlabel = $("#pathlabel").val();
            if (xmlString != ""){
                var functionalDataVector = DwenguinoSimulation.generateSimulatedData(3900000, 1);
            }
            var collection = interactive_clustering.collectionLabel;
            var embedding_dims = this.embedding_dims;
            var data = {"collection": collection
                    , "experimentId": interactive_clustering.experimentId
                    , "vector": JSON.stringify(functionalDataVector)
                    , "xml_blocks": xmlString
                    , "label": label
                    , "steplabel": steplabel
                    , "pathlabel" : pathlabel
                    , "embedding_dims": embedding_dims};
            data = JSON.stringify(data);
            console.log(data);
            $.ajax({
                type: "POST",
                url: "http://localhost:20042/recluster",
                data: data
                },
            ).done(function(data){
                console.log("got response");
                json_data = JSON.parse(data);
                console.log(json_data);
                interactive_clustering.currentData = json_data;
                interactive_clustering.plotClusteringData(json_data[0], json_data[2]);
            }).fail(function(response, status)  {
                console.warn('Failed to fetch sessionIdList:', status);
            });
        }catch(err){
            console.log("error: skipping this tree");
        }
    },
    plotClusteringData: function(tsne_data, labels){
      var myPlot = document.getElementById("db_clustering_plot");
      var xCoords = [];
      var yCoords = [];
      var zCoords = [];
      var cCoords = [];
      for (var i = 0 ; i < tsne_data.length; i++){
            xCoords.push(tsne_data[i][0]);
            yCoords.push(tsne_data[i][1]);
            zCoords.push(tsne_data[i][2]);
            var rgb = hsluv.hsluvToRgb([(labels[i]+1)*50, 100, 50]);
            //cCoords.push(entry[3]*4)
            cCoords.push(Colors.rgb2hex(Math.round(rgb[0] * 255), Math.round(rgb[1] * 255), Math.round(rgb[2] * 255)));
      }
      var data = [];
      var scatterPoints = {x:xCoords,
                            y:yCoords,
                            z:zCoords,
                            type:interactive_clustering.dimension_names[interactive_clustering.embedding_dims - 2],
                            mode:"markers",
                            marker:{size:7, color: cCoords}};
      /*this.cluster_distance_pairs.forEach(function(entry){
        var trace = {x: [entry[0][0], entry[1][0]], y: [entry[0][1], entry[1][1]], z: [entry[0][2], entry[1][2]],
        mode: 'lines', type: 'scatter3d', line: {width: 5}};
        data.push(trace);
      });*/
      data.push(scatterPoints);
      layout = { hovermode:'closest', title:'Click on Points'};
      Plotly.newPlot('db_clustering_plot', data, layout);
      myPlot.on('plotly_click', function(eventdata){
        console.log(eventdata);
        var pointIndex = eventdata.points[0].pointNumber;
        console.log(pointIndex);
        interactive_clustering.loadCodeTreeToWorkspace(pointIndex);
        if (interactive_clustering.viewing == 0){
            interactive_clustering.loadCodeTreeToWorkspace(pointIndex);
        } else if (interactive_clustering.viewing == 1) {
            if (interactive_clustering.measuringState == 0){
                $("#vector1").val("");
                $("#vector2").val("");
                $("#vector3").val("");
                $("#v1_v2_v3_distance").val("");
                interactive_clustering.vector1 = interactive_clustering.currentData[3][pointIndex];
                $("#vector1").val(interactive_clustering.vector1);
                interactive_clustering.measuringState = 1;
            } else if (interactive_clustering.measuringState == 1){
                interactive_clustering.vector2 = interactive_clustering.currentData[3][pointIndex];
                $("#vector2").val(interactive_clustering.vector2);
                interactive_clustering.measuringState = 2;
            } else if (interactive_clustering.measuringState == 2){
                interactive_clustering.vector3 = interactive_clustering.currentData[3][pointIndex];
                $("#vector3").val(interactive_clustering.vector3);
                interactive_clustering.measuringState = 0;
                var distance = interactive_clustering.calculateVectorDistance(interactive_clustering.vector1,
                                                                              interactive_clustering.vector2,
                                                                              interactive_clustering.vector3);

                $("#v1_v2_v3_distance").val(distance);
            }
        } else if (interactive_clustering.viewing == 2){
            if (interactive_clustering.measuringState == 0){
                $("#vector1").val("");
                $("#vector2").val("");
                $("#vector3").val("");
                $("#v1_v2_v3_distance").val("");
                interactive_clustering.vector1 = interactive_clustering.currentData[3][pointIndex];
                $("#vector1").val(interactive_clustering.vector1);
                interactive_clustering.measuringState = 1;
            } else if (interactive_clustering.measuringState == 1){
                interactive_clustering.vector2 = interactive_clustering.currentData[3][pointIndex];
                $("#vector2").val(interactive_clustering.vector2);
                interactive_clustering.measuringState = 0;
                //distance = interactive_clustering.calculateCorrelation(interactive_clustering.vector1, interactive_clustering.vector2);
                distance = interactive_clustering.calculateCosineDistance(interactive_clustering.vector1, interactive_clustering.vector2);

                $("#v1_v2_v3_distance").val(distance);
            }
        }

      });
    },
    calculateVectorDistance: function(v1, v2, v3){
        var distance = 0;
        var combined = [];
        // Calculate combined vector, the mean of the combined vector and the mean of the target vector.
        for (var i = 0 ; i < v1.length ; i++){
            combined[i] = v1[i] + v2[i];
        }

        //var sim = this.calculateCorrelation(combined, v3);
        var sim = this.calculateCosineDistance(combined, v3);
        return sim;
    },
    calculateCosineDistance: function(v1, v2){
        var dot_prod = 0;
        for (var i = 0 ; i < v1.length ; i++){
            dot_prod += v1[i]*v2[i];
        }
        var v1Norm = 0;
        var v2Norm = 0;
        for (var i = 0 ; i < v1.length ; i++){
            v1Norm += v1[i] * v1[i];
            v2Norm += v2[i] * v2[i];
        }
        v1Norm = Math.sqrt(v1Norm);
        v2Norm = Math.sqrt(v2Norm);
        var cosine_dist = dot_prod/(v1Norm * v2Norm);
        return cosine_dist;
    },
    calculateCorrelation: function(v1, v2){
        var distance = 0;
        var meanV1 = 0;
        var meanV2 = 0;
        var stdV1 = 0;
        var stdV2 = 0;
        // Calculate combined vector, the mean of the combined vector and the mean of the target vector.
        for (var i = 0 ; i < v1.length ; i++){
            meanV1 += v1[i];
            meanV2 += v2[i];
        }
        meanV1 = meanV1/v1.length;
        meanV2 = meanV2/v1.length;
        // Calculate the standard deviation for the combined vector and the target vector.
        for (var i = 0 ; i < v1.length ; i++){
            stdV1 += (v1[i] - meanV1)*(v1[i] - meanV1);
            stdV2 += (v2[i] - meanV2)*(v2[i] - meanV2);
        }
        stdV1 = Math.sqrt(1/(v1.length - 1) * stdV1);
        stdV2 = Math.sqrt(1/(v1.length - 1) * stdV2);

        // Calculate the covariance between the combined vector and the target vector.
        cov = 0;
        for (var i = 0 ; i < v1.length ; i++){
            cov += (v1[i] - meanV1)*(v2[i] - meanV2);
        }
        cov = cov/v1.length;
        // Calculate the correlation between the combined and the target vector.
        corr = cov/(stdV1*stdV2);

        return corr;

    },
    loadCodeTreeToWorkspace: function(index){
        var codestring = interactive_clustering.currentData[1][index];
        DwenguinoBlockly.setWorkspaceBlockFromXml(codestring);
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