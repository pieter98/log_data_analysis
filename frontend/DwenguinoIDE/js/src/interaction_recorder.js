var InteractionRecorder = {
    recording: false,
    init: function(){
        $("#record_interactions_button").click(function(){
            InteractionRecorder.recording = !InteractionRecorder.recording;
            $(this).text("" + InteractionRecorder.recording)
        })
    },
    recordEvent: function(event){
        if (InteractionRecorder.recording == true){
            var label = $("#label").val();
            event.structureLabelString = label;
            $.ajax({
                type: "POST",
                url: "http://localhost:20042/record_event",
                dataType: "string",
                data: JSON.stringify(event)
                },
            ).done(function(data){

            }).fail(function(response, status)  {
                console.warn('Failed to fetch sessionIdList:', status);
            });
        }
    },

}

$(document).ready(function(){
    InteractionRecorder.init();

})