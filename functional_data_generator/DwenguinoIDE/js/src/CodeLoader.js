var CodeLoader = {
    /*latest recorded dataset: _01-07-2019_data_recorded*/
    nrOfCodeTrees: -1,
    experimentId: "_19-04-2019",
    currentTree: 1772,
    init: function(){
        DwenguinoSimulation.setupEnvironment("randomSimulatedEnvironment");
        $.ajax({
            type: "GET",
            url: "http://localhost:20042/get_nr_of_trees?experimentId=" + CodeLoader.experimentId,
            datatype: "json"},
        ).done(function(data){
            CodeLoader.nrOfCodeTrees = data;
            CodeLoader.convertCodeTrees();
        }).fail(function(response, status)  {
            console.warn('Failed to fetch sessionIdList:', status);
        });
    },
    convertCodeTrees: function(){
        this.loadCodeTree(CodeLoader.currentTree);
    },
    loadCodeTree: function(identifier){
         $.ajax({
            type: "GET",
            url: "http://localhost:20042/get_code_tree_for_index?experimentId=" + CodeLoader.experimentId + "&index=" + identifier,
            datatype: "json"},
        ).done(function(data){
            data = JSON.parse(data)
            CodeLoader.generateFunctionalIdForCodeTree(data[0], CodeLoader.currentTree, data[1]);
            CodeLoader.currentTree += 1;
            if (CodeLoader.currentTree < CodeLoader.nrOfCodeTrees){
                CodeLoader.loadCodeTree(CodeLoader.currentTree);
            }
        }).fail(function(response, status)  {
            console.warn('Failed to fetch sessionIdList:', status);
        });
    },
    generateFunctionalIdForCodeTree: function(codeTree, nr, label){
        DwenguinoBlockly.workspace.clear();
        Blockly.Xml.domToWorkspace(Blockly.Xml.textToDom(codeTree), DwenguinoBlockly.workspace);
        try {
            var functionalDataVector = DwenguinoSimulation.generateSimulatedData(30000, 1);
            console.log(functionalDataVector);
            var data = {"experimentId": CodeLoader.experimentId
                    , "vector": JSON.stringify(functionalDataVector)
                    , "xml_blocks": codeTree
                    , "label": label};
            data = JSON.stringify(data);
            $.ajax({
                type: "POST",
                url: "http://localhost:20042/save_functional_vector",
                dataType: "string",
                data: data
                },
            ).done(function(data){

            }).fail(function(response, status)  {
                console.warn('Failed to fetch sessionIdList:', status);
            });
        }catch(err){
            console.log("error: skipping this tree");
        }

    },
    saveFunctionalCodeId: function(functionalCodeId){

    }
}