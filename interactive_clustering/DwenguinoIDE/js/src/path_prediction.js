var path_prediction = {
    workspace: undefined,
    init: function(){
        this.workspace = DwenguinoBlockly.workspace;
        console.log("Workspace: " + this.workspace);
        this.workspace.addChangeListener(path_prediction.changeLogger);
    },
    changeLogger: function(event){
        var blocks = path_prediction.workspace.getAllBlocks();

        var delayTimeBlock = path_prediction.workspace.newBlock('char_type');
        delayTimeBlock.setFieldValue(1000, 'BITMASK');
        delayTimeBlock.initSvg();
        delayTimeBlock.render();

        var delayBlock = path_prediction.workspace.newBlock('dwenguino_delay');
        delayBlock.initSvg();
        delayBlock.render();


        console.log(delayTimeBlock.toString());
    }

}





$(document).ready(function(){
    console.log("Loaded path prediction");
    path_prediction.init();
})