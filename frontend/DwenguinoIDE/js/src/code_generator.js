
var CodeGenerator = {
    onresize: function(){
        var blocklyArea = document.getElementById('db_blockly');
        var blocklyDiv = document.getElementById('blocklyDiv');
        // Compute the absolute coordinates and dimensions of blocklyArea.
        var element = blocklyArea;
        var x = 0;
        var y = 0;
        do {
            x += element.offsetLeft;
            y += element.offsetTop;
            element = element.offsetParent;
        } while (element);
        // Position blocklyDiv over blocklyArea.
        blocklyDiv.style.left = x + 'px';
        blocklyDiv.style.top = y + 'px';
        blocklyDiv.style.width = blocklyArea.offsetWidth + 'px';
        blocklyDiv.style.height = blocklyArea.offsetHeight + 'px';
    },

    injectBlockly: function(){
        var blocklyArea = document.getElementById('db_blockly');
        var blocklyDiv = document.getElementById('blocklyDiv');
        CodeGenerator.workspace = Blockly.inject(blocklyDiv,
            {
                toolbox: document.getElementById('toolbox'),
                media: "DwenguinoIDE/img/",
                zoom: {controls: true, wheel: true}
            });
        window.addEventListener('resize', CodeGenerator.onresize, false);
        CodeGenerator.onresize();
        Blockly.svgResize(CodeGenerator.workspace);
        CodeGenerator.workspace.addChangeListener(CodeGenerator.renderCode);
    },

    changeLanguage: function() {
        // Store the blocks for the duration of the reload.
        // This should be skipped for the index page, which has no blocks and does
        // not load Blockly.
        // Also store the recoring up till now.
        // MSIE 11 does not support sessionStorage on file:// URLs.
        if (typeof Blockly !== 'undefined' && window.sessionStorage) {
            var xml = Blockly.Xml.workspaceToDom(CodeGenerator.workspace);
            var text = Blockly.Xml.domToText(xml);
            window.sessionStorage.loadOnceBlocks = text;
        }

        var languageMenu = document.getElementById('db_menu_item_language_selection');
        var newLang = encodeURIComponent(languageMenu.options[languageMenu.selectedIndex].value);
        var search = window.location.search;
        if (search.length <= 1) {
            search = '?lang=' + newLang;
        } else if (search.match(/[?&]lang=[^&]*/)) {
            search = search.replace(/([?&]lang=)[^&]*/, '$1' + newLang);
        } else {
            search = search.replace(/\?/, '?lang=' + newLang + '&');
        }

        window.location = window.location.protocol + '//' +
        window.location.host + window.location.pathname + search;
    },

    /**
     * User's language (e.g. "en").
     * @type {string}
     */
    LANG: DwenguinoBlocklyLanguageSettings.getLang(),

    isRtl: function(){
        return false;
    },

    /**
     * Initialize the page language.
     */
    initLanguage: function() {
      // Set the HTML's language and direction.
      var rtl = CodeGenerator.isRtl();
      document.dir = rtl ? 'rtl' : 'ltr';
      document.head.parentElement.setAttribute('lang', CodeGenerator.LANG);

      // Sort languages alphabetically.
      var languages = [];
      for (var lang in DwenguinoBlocklyLanguageSettings.LANGUAGE_NAME) {
        languages.push([DwenguinoBlocklyLanguageSettings.LANGUAGE_NAME[lang], lang]);
      }
      var comp = function(a, b) {
        // Sort based on first argument ('English', 'Русский', '简体字', etc).
        if (a[0] > b[0]) return 1;
        if (a[0] < b[0]) return -1;
        return 0;
      };
      languages.sort(comp);

  },

    doTranslation: function() {
        // Inject language strings.
        document.title += ' ' + MSG['title'];
        //document.getElementById('title').textContent = MSG['title'];
        //document.getElementById('tab_blocks').textContent = MSG['blocks'];

        //document.getElementById('linkButton').title = MSG['linkTooltip'];
        //document.getElementById('db_menu_item_run').title = MSG['runTooltip'];
        document.getElementById('db_menu_item_upload').title = MSG['loadBlocksFileTooltip'];
        document.getElementById('db_menu_item_download').title = MSG['saveBlocksFileTooltip'];
        document.getElementById('db_menu_item_simulator').title = MSG['toggleSimulator'];
        //document.getElementById('t

        var tutorials = []; /*['tutsIntroduction', 'tutsHelloDwenguino', 'tutsBlink', 'tutsHelloRobot',
        'tutsNameOnLcd', 'tutsBlinkLED', 'tutsLedOnButtonPress', 'tutsBitPatternOnLeds',
      'tutsAllButtons', 'tutsDriveForward', 'tutsRideInSquare', 'tutsRideToWall', 'tutsAvoidWall'];*/
      /*  for (var i = 0; i < tutorials.length ; i++){
            var element = document.getElementById(tutorials[i]);
            if (element){
                element.innerHTML = MSG[tutorials[i]];
            }
        }*/

        var categories = ['catLogic', 'catLoops', 'catMath', 'catText', 'catLists',
            'catColour', 'catVariables', 'catFunctions', 'catBoardIO', 'catDwenguino', 'catArduino'];
        for (var i = 0, cat; cat = categories[i]; i++) {
            var element = document.getElementById(cat);
            if (element) {
                element.setAttribute('name', MSG[cat]);
            }

        }
        var textVars = document.getElementsByClassName('textVar');
        for (var i = 0, textVar; textVar = textVars[i]; i++) {
            textVar.textContent = MSG['textVariable'];
        }
        var listVars = document.getElementsByClassName('listVar');
        for (var i = 0, listVar; listVar = listVars[i]; i++) {
            listVar.textContent = MSG['listVariable'];
        }
    },

    /**
     * Load blocks saved on App Engine Storage or in session/local storage.
     * @param {string} defaultXml Text representation of default blocks.
     */
    loadBlocks: function(defaultXml) {
      try {
        var loadOnce = window.sessionStorage.loadOnceBlocks;
      } catch(e) {
        // Firefox sometimes throws a SecurityError when accessing sessionStorage.
        // Restarting Firefox fixes this, so it looks like a bug.
        var loadOnce = null;
      }
      if ('BlocklyStorage' in window && window.location.hash.length > 1) {
        // An href with #key trigers an AJAX call to retrieve saved blocks.
        BlocklyStorage.retrieveXml(window.location.hash.substring(1));
      } else if (loadOnce) {
        // Language switching stores the blocks during the reload.
        delete window.sessionStorage.loadOnceBlocks;
        var xml = Blockly.Xml.textToDom(loadOnce);
        Blockly.Xml.domToWorkspace(xml, CodeGenerator.workspace);
      } else if (defaultXml) {
        // Load the editor with default starting blocks.
        var xml = Blockly.Xml.textToDom(defaultXml);
        Blockly.Xml.domToWorkspace(xml, CodeGenerator.workspace);
      } else if ('BlocklyStorage' in window) {
        // Restore saved blocks in a separate thread so that subsequent
        // initialization is not affected from a failed load.
        window.setTimeout(BlocklyStorage.restoreBlocks, 0);
      }
  },
  generateRandomCorrectCodeTree: function(sessionId){
        var parentBlock = CodeGenerator.workspace.newBlock('setup_loop_structure');
        parentBlock.initSvg();
        parentBlock.render();

        // DONE: log code here (created setup loop block)
        CodeGenerator.takeSnapshotOfWorkspace(sessionId);
        // Generate a first motor block with random speed and channel
        var speed1 = -100 + 200 * Math.round(Math.random());
        var channel1 = Math.floor(Math.random() * 2 + 1);
        var speed2 = -100 + 200 * Math.round(Math.random());
        var channel2 = Math.floor(Math.random() * 2 + 1);
        var delay1 = 1750 + Math.floor(Math.random() * 10) * 50;
        var delay2 = Math.floor(Math.random() * 20) + 165;
        var isSetup = false;
        var globalParentConnection = null;
        // Randomly select the part of the setup loop block to put our blocks into.
        if (Math.random() < 0.5){
            isSetup = true;
            globalParentConnection = parentBlock.getInput('SETUP').connection;
        }else{
            globalParentConnection = parentBlock.getInput('LOOP').connection;
        }

        var codeConnections = CodeGenerator.generateBaseDriveInSquareSolution(globalParentConnection, speed1, channel1, speed2, channel2, delay1, delay2, sessionId);
        // DONE: log code here! (added second delay block)*/
        CodeGenerator.takeSnapshotOfWorkspace(sessionId);
        if (isSetup){
            if (Math.random() < 0.4){
                // Generate a loop which iterates 4 times
                var forLoop = CodeGenerator.generateForLoop(0, 4, 1);
                forLoop.previousConnection.connect(globalParentConnection);
                forLoop.getInput('DO').connection.connect(codeConnections[0]);
                // DONE: log code here (added for loop )
                CodeGenerator.takeSnapshotOfWorkspace(sessionId);
            }else{
                for (var i = 0 ; i < 3 ; i++){
                    var newCodeConnections = CodeGenerator.generateBaseDriveInSquareSolution(codeConnections[1], speed1, channel1, speed2, channel2, delay1, delay2, sessionId);
                    codeConnections[1] = newCodeConnections[1];
                }
            }
        }else{
            if (Math.random() < 0.4){
                // Do nothing this code works
            }else{
                // Make the incorrect assumption that the code has to be repeated
                for (var i = 0 ; i < 3 ; i++){
                    var newCodeConnections = CodeGenerator.generateBaseDriveInSquareSolution(codeConnections[1], speed1, channel1, speed2, channel2, delay1, delay2, sessionId);
                    codeConnections[1] = newCodeConnections[1];
                }
            }
        }

        CodeGenerator.workspace.clear();

  },
  generateBaseDriveInSquareSolution: function(globalParentConnection, speed1, channel1, speed2, channel2, delayTime1, delayTime2, sessionId){
        var motor1 = CodeGenerator.generateMotorBlock(speed1, channel1);
        var motor2 = CodeGenerator.generateMotorBlock(speed1, 1 + (channel1)%2);
        globalParentConnection.connect(motor1.previousConnection);
        //DONE: log code here (added first motor block)
        CodeGenerator.takeSnapshotOfWorkspace(sessionId);
        motor1.nextConnection.connect(motor2.previousConnection);
        // DONE: log code here (added second motor block)
        CodeGenerator.takeSnapshotOfWorkspace(sessionId);

        // Generate random time wait block for going straight
        var delay1 = CodeGenerator.generateWaitBlock(delayTime1);
        motor2.nextConnection.connect(delay1.previousConnection);
        // DONE: log code here (added first dela block)
        CodeGenerator.takeSnapshotOfWorkspace(sessionId);

        // Now add two motor blocks after the wait block for turning
        var motor3 = CodeGenerator.generateMotorBlock(speed2, channel2);
        var motor4 = CodeGenerator.generateMotorBlock(speed2 * -1, 1 + (channel2)%2);
        delay1.nextConnection.connect(motor3.previousConnection);
        // DONE: log code here! (added third motor block)
        CodeGenerator.takeSnapshotOfWorkspace(sessionId);
        motor3.nextConnection.connect(motor4.previousConnection);
        // DONE: log code her (added fourth motor block)
        CodeGenerator.takeSnapshotOfWorkspace(sessionId);

        // Add a final delay block for making the turn
        var delay2 = CodeGenerator.generateWaitBlock(delayTime2);
        motor4.nextConnection.connect(delay2.previousConnection);
        // DONE: log code here! (added second delay block)
        CodeGenerator.takeSnapshotOfWorkspace(sessionId);
        return [motor1.previousConnection, delay2.nextConnection];
  },
  generateWaitBlock: function(waittime){
        var delayTimeBlock = CodeGenerator.workspace.newBlock('char_type');
        delayTimeBlock.setFieldValue(waittime, 'BITMASK');
        delayTimeBlock.initSvg();
        delayTimeBlock.render();
        var delayBlock = CodeGenerator.workspace.newBlock('dwenguino_delay');
        delayBlock.initSvg();
        delayBlock.render();
        var delayBlockTimeConnection = delayBlock.getInput('DELAY_TIME').connection;
        delayBlockTimeConnection.connect(delayTimeBlock.outputConnection);
        return delayBlock;
  },
  generateMotorBlock: function(speed, number){
        var motorBlock = CodeGenerator.workspace.newBlock('dc_motor');
        motorBlock.initSvg();
        motorBlock.render();

        var speedBlock = CodeGenerator.workspace.newBlock('math_number');
        speedBlock.setFieldValue(speed, 'NUM');
        speedBlock.initSvg();
        speedBlock.render();

        var numberBlock = CodeGenerator.workspace.newBlock('math_number');
        numberBlock.setFieldValue(number, 'NUM')
        numberBlock.initSvg();
        numberBlock.render();

        var speedMotorConnection = motorBlock.getInput('speed').connection;
        var speedSpeedConnection = speedBlock.outputConnection;
        speedMotorConnection.connect(speedSpeedConnection);

        var numberMotorConnection = motorBlock.getInput('channel').connection;
        var numberNumberConnection = numberBlock.outputConnection;
        numberMotorConnection.connect(numberNumberConnection);

        return motorBlock;

  },
  generateForLoop: function(start, end, inc){
        var forBlock = CodeGenerator.workspace.newBlock('controls_for');
        forBlock.initSvg();
        forBlock.render();
        forBlock.setFieldValue('i', 'VAR');
        var startBlock = CodeGenerator.workspace.newBlock('char_type');
        startBlock.initSvg();
        startBlock.render();
        startBlock.setFieldValue(start, 'BITMASK');
        var endBlock = CodeGenerator.workspace.newBlock('char_type');
        endBlock.initSvg();
        endBlock.render();
        endBlock.setFieldValue(end, 'BITMASK');
        var incBlock = CodeGenerator.workspace.newBlock('char_type');
        incBlock.initSvg();
        incBlock.render();
        incBlock.setFieldValue(inc, 'BITMASK');

        forBlock.getInput('FROM').connection.connect(startBlock.outputConnection);
        forBlock.getInput('TO').connection.connect(endBlock.outputConnection);
        forBlock.getInput('BY').connection.connect(incBlock.outputConnection);

        return forBlock;

  },
  /*
    * This function submits an event to the python logging server.
    */
    recordEvent: function(eventToRecord, sessionId){
      var serverSubmission = {
        "sessionId": sessionId,
        "agegroup": 0,
        "gender": 0,
        "activityId": 0,
        "timestamp": $.now(),
        "event": eventToRecord
      };
      console.log(serverSubmission);
      /*if (DwenguinoBlockly.sessionId !== undefined){
        $.ajax({
            type: "POST",
            url: this.serverUrl + "/sessions/update",
            data: {"logEntry": JSON.stringify(serverSubmission)},
        }).done(function(data){
            console.debug('Recording submitted', data);
        }).fail(function(response, status)  {
            console.warn('Failed to submit recording:', status);
        });
      }*/
    },
    createEvent: function(eventName, data){
      var event = {
        "name": eventName,
        "timestamp": $.now(),
        "simulatorState": "off",
        "selectedDifficulty": "Advanced",
        "activeTutorial": null,
        "groupId": 0,
        "computerId": 0,
        "workshopId": 0,
        "data": data
      };
      return event;
    },
    prevWorkspaceXml: "",
    /**
    *   Take a snapshot of the current timestamp, simulatorstate, selectedDifficulty, activeTutorial and blocks in the workspace.
    */
    takeSnapshotOfWorkspace: function(sessionId){
        console.log("taking snapshot");
        var xml = Blockly.Xml.workspaceToDom(CodeGenerator.workspace);
        var text = Blockly.Xml.domToText(xml);
        if (text != CodeGenerator.prevWorkspaceXml){
            CodeGenerator.prevWorkspaceXml = text;
            CodeGenerator.recordEvent(CodeGenerator.createEvent("changedWorkspace", text), sessionId);
        }
    },
}

$(document).ready(function(){

    CodeGenerator.initLanguage();
    CodeGenerator.injectBlockly();
    for (var i = 0 ; i < 10 ; i++){
        CodeGenerator.generateRandomCorrectCodeTree(i);
    }
})


