
var Labeler = {
    sessionIdList: {},
    currentSessionStep: 0,
    maxSessionSteps: 0,
    currentEntry: 0,
    currentSelectedSession: [],

    loadProgramCount: function(){
        console.log("Get the maximum number of programs to label");
        $.ajax({
            type: "GET",
            url: "http://localhost:20042/get_labeler_data_count",
            datatype: "json"},
        ).done(function(data){
            Labeler.maxSessionSteps = JSON.parse(data);
        }).fail(function(response, status)  {
            console.warn('Failed to fetch sessionIdList:', status);
        });
    },
    loadProgram: function(programIndex){
        $.ajax({
            type: "GET",
            url: "http://localhost:20042/get_labeler_data_element?prog_number=" + programIndex,
            datatype: "json"},
        ).done(function(data){
            var element = JSON.parse(data);
            console.log(element);
            Labeler.currentEntry = element;
            DwenguinoBlockly.workspace.clear();
            var xml = Blockly.Xml.textToDom(Labeler.currentEntry["xml_blocks"]);
            Blockly.Xml.domToWorkspace(xml, DwenguinoBlockly.workspace);
        }).fail(function(response, status)  {
            console.warn('Failed to fetch sessionIdList:', status);
        });
    },

    labelProgram: function(label){
        var entry = Labeler.currentEntry;
        entry["label"] = label;
        $.ajax({
            type: "POST",
            crossDomain : true,
            url: "http://localhost:20042/update_functional_vector",
            data: JSON.stringify(entry),
        }).done(function(data){
            console.debug('Recording submitted', data);
        }).fail(function(response, status)  {
            console.warn('Failed to submit recording:', status);
        });
    }


}

$(document).ready(function(){
    Labeler.loadProgramCount();
    $('#db_current_item').val(Labeler.currentSessionStep);
    Labeler.loadProgram(Labeler.currentSessionStep);
    $(".labelbutton").click(function(){
        var label = $(this).attr("data-nr");
        console.log(label);
        Labeler.labelProgram(label);
    });
    $('#prev_session_step').click(function(){
        if (Labeler.currentSessionStep > 0){
            Labeler.currentSessionStep -= 1;
        }
        $('#db_current_item').val(Labeler.currentSessionStep);
        Labeler.loadProgram(Labeler.currentSessionStep);
    });
    $('#next_session_step').click(function(){
        if (Labeler.currentSessionStep < Labeler.maxSessionSteps){
            Labeler.currentSessionStep += 1;
        }
        $('#db_current_item').val(Labeler.currentSessionStep);
        Labeler.loadProgram(Labeler.currentSessionStep);
    });
    $("#set_current_program").click(function(){
        var value = parseInt($("#db_current_item").val());
        if (value > 0 && value < Labeler.maxSessionSteps){
            Labeler.currentSessionStep = value;
        }
        $('#db_current_item').val(Labeler.currentSessionStep);
        Labeler.loadProgram(value);
    });
})
