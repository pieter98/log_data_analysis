
var DataAnalysis = {
    sessionIdList: {},
    currentSessionStep: 0,
    currentSelectedSession: [],

    loadSessionIds: function(){
        console.log("loading session ids");
        $.ajax({
            type: "GET",
            url: "http://localhost:20042/sessionIdList",
            datatype: "json"},
        ).done(function(data){
            DataAnalysis.handleSessionIdList(JSON.parse(data));
        }).fail(function(response, status)  {
            console.warn('Failed to fetch sessionIdList:', status);
        });
    },

    handleSessionIdList: function(sessionIdList){
        var sessionIdDropdown = $("#session_ids");
        sessionIdDropdown.empty();
        sessionIdDropdown.append($("<option>").attr("disabled", true).attr("selected", true).attr("value", "").text("--Select a session--"));
        sessionIdDropdown.append($("<option>").attr("value", ".*").text("All"));
        for (key in sessionIdList){
            sessionIdDropdown.append($("<option>").attr("value", sessionIdList[key]).text(key));
            DataAnalysis.sessionIdList[sessionIdList[key]] = key;
        }
        //Attach event listeners to different filter inputs.
        console.log("test");
        console.log($("#start_date").val());
        sessionIdDropdown.off();
        sessionIdDropdown.on("change", function(){
            DataAnalysis.loadSessionSteps();
        });
        $("#start_date").off();
        $("#start_date").on("change", function(){
            DataAnalysis.loadSessionSteps();
        });
        $("#end_date").off();
        $("#end_date").on("change", function(){
            DataAnalysis.loadSessionSteps();
        });
    },
    loadSessionSteps: function(){
        //Reset the selected steps
        $("#session_steps").val(-1);
        //Collect the selected filter criteria.
        var session_id = $("#session_ids").val();
        var workshopType = $("#workshop_type").val();
        var start_date = Date.parse($("#start_date").val());
        var end_date = Date.parse($("#end_date").val());
        var query_string = "";
        if (!isNaN(start_date)){
            query_string += "&start_date=";
            query_string += start_date;
        }
        if (!isNaN(end_date)){
            query_string += "&end_date=";
            query_string += end_date;
        }
        console.log(start_date);
        console.log("Loading session steps");
        $.ajax({
            type: "GET",
            url: "http://localhost:20042/eventsfor?session_id=" + session_id + "&workshop_type=" + workshopType + query_string,
            datatype: "json"},
        ).done(function(data){
            DataAnalysis.processSessionData(data);
        }).fail(function(response, status)  {
            console.warn('Failed to fetch sessionIdList:', status);
        });
    },
    processSessionData: function(sessionData){
        var selected_sessions_dropdown = $("#selected_sessions");
        selected_sessions_dropdown.empty();
        selected_sessions_dropdown.append($("<option>").attr("disabled", true).attr("selected", true).attr("value", "").text("--Select a session--"));
        parsedData = JSON.parse(sessionData);
        for (elem in parsedData){
            var option = $("<option>").attr("value", elem).text(DataAnalysis.sessionIdList[parsedData[elem]["_id"]]);
            selected_sessions_dropdown.append(option);
        }
        selected_sessions_dropdown.off();
        selected_sessions_dropdown.on("change", function(){
            DataAnalysis.processSessionSteps(parsedData[this.value]);
        });
    },
    processSessionSteps: function(sessionData){
        console.log(sessionData);
        var session_steps_dropdown = $("#session_steps");
        session_steps_dropdown.empty();
        session_steps_dropdown.append($("<option>").attr("disabled", true).attr("selected", true).attr("value", -1).text("--Select a step--"));
        for (index in sessionData["eventsForSession"]){
            var option = $("<option>").attr("value", index).text(index);
            session_steps_dropdown.append(option);
        }
        DataAnalysis.currentSessionStep = 0;
        session_steps_dropdown.off();
        session_steps_dropdown.on("change", function(){
            DataAnalysis.currentSessionStep = parseInt(this.value);
            DataAnalysis.currentSelectedSession = sessionData["eventsForSession"];
            DataAnalysis.updateWorkspace();
        })
    },
    updateWorkspace: function(){
        console.log(DataAnalysis.currentSelectedSession[DataAnalysis.currentSessionStep].data);
        var xmlText = DataAnalysis.currentSelectedSession[DataAnalysis.currentSessionStep].data;
        var xml = Blockly.Xml.textToDom(xmlText);
        DwenguinoBlockly.restoreFromXml(xml);
    },
    nextCodeTreeInSessionSteps: function(delta){
        DataAnalysis.currentSessionStep += delta;
        if (DataAnalysis.currentSessionStep < 0){
            DataAnalysis.currentSessionStep = 0;
        }
        if (DataAnalysis.currentSessionStep > DataAnalysis.currentSelectedSession.length){
            DataAnalysis.currentSessionStep = DataAnalysis.currentSelectedSession.length - 1;
        }
        $("#session_steps").val(DataAnalysis.currentSessionStep);
        DataAnalysis.updateWorkspace();
    },
    handleSvgToImages: function(){
      var svgString = new XMLSerializer().serializeToString(document.querySelector('svg'));
      var canvas = document.getElementById("images_canvas");
      var ctx = canvas.getContext("2d");
      var DOMURL = self.URL || self.webkitURL || self;
      var img = new Image();
      var svg = new Blob([svgString], {type: "image/svg+xml;charset=utf-8"});
      var url = DOMURL.createObjectURL(svg);
      img.onload = function() {
          ctx.drawImage(img, 0, 0);
          var png = canvas.toDataURL("image/png");

          /// create an "off-screen" anchor tag
          var lnk = document.createElement('a'), e;

          /// the key here is to set the download attribute of the a tag
          lnk.download = "codeimage.png";

          /// convert canvas content to data-uri for link. When download
          /// attribute is set the content pointed to by link will be
          /// pushed as "download" in HTML5 capable browsers
          lnk.href = png;

          /// create a "fake" click-event to trigger the download
          if (document.createEvent) {
            e = document.createEvent("MouseEvents");
            e.initMouseEvent("click", true, true, window,
                             0, 0, 0, 0, 0, false, false, false,
                             false, 0, null);

            lnk.dispatchEvent(e);
          } else if (lnk.fireEvent) {
            lnk.fireEvent("onclick");
          }

          <!--document.querySelector('#png-container').innerHTML = '<img src="'+png+'"/>';-->
          //// Dispose of the png
          DOMURL.revokeObjectURL(png);
      };
      img.src = url
    },
    /* Canvas Donwload */
    download: function(canvas, filename) {
      /// create an "off-screen" anchor tag
      var lnk = document.createElement('a'), e;

      /// the key here is to set the download attribute of the a tag
      lnk.download = filename;

      /// convert canvas content to data-uri for link. When download
      /// attribute is set the content pointed to by link will be
      /// pushed as "download" in HTML5 capable browsers
      lnk.href = canvas.toDataURL("image/png;base64");

      /// create a "fake" click-event to trigger the download
      if (document.createEvent) {
        e = document.createEvent("MouseEvents");
        e.initMouseEvent("click", true, true, window,
                         0, 0, 0, 0, 0, false, false, false,
                         false, 0, null);

        lnk.dispatchEvent(e);
      } else if (lnk.fireEvent) {
        lnk.fireEvent("onclick");
      }
    }


}

$(document).ready(function(){
    DataAnalysis.loadSessionIds();
    $("#prev_session_step").click(function(){
        DataAnalysis.nextCodeTreeInSessionSteps(-1);
    });
    $("#next_session_step").click(function(){
        DataAnalysis.nextCodeTreeInSessionSteps(1);
    });
    $("#to_images_button").click(function(){
        DataAnalysis.handleSvgToImages();
    });
})
