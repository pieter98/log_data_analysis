
var CodeGenerator = {
    dbname: "GeneratedDataLog",
    setDBName: function(dbname){
        CodeGenerator.dbname = dbname;
    },
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
  structureLabelString: "",
  fullLabelString: "",
  generateRandomCorrectCodeTree: function(sessionId){
        CodeGenerator.structureLabelString = "";
            CodeGenerator.fullLabelString = "";
        var parentBlock = CodeGenerator.workspace.newBlock('setup_loop_structure');
        parentBlock.initSvg();
        parentBlock.render();

        ;
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
            CodeGenerator.structureLabelString += "setup";
            CodeGenerator.fullLabelString += "setup";
            // DONE: log code here (created setup loop block)
            CodeGenerator.takeSnapshotOfWorkspace(sessionId)
        }else{
            globalParentConnection = parentBlock.getInput('LOOP').connection;
            CodeGenerator.structureLabelString += "loop";
            CodeGenerator.fullLabelString += "loop";
            // DONE: log code here (created setup loop block)
            CodeGenerator.takeSnapshotOfWorkspace(sessionId)
        }

        var codeConnections = CodeGenerator.generateBaseDriveInSquareSolution(globalParentConnection, speed1, channel1, speed2, channel2, delay1, delay2, sessionId);
        if (isSetup){
            if (Math.random() < 0.5){
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
            if (Math.random() < 0.5){
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
        globalParentConnection.connect(motor1.previousConnection);
        //DONE: log code here (added first motor block)
        CodeGenerator.takeSnapshotOfWorkspace(sessionId);

        var motor2 = CodeGenerator.generateMotorBlock(speed1, 1 + (channel1)%2);
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
        delay1.nextConnection.connect(motor3.previousConnection);
        // DONE: log code here! (added third motor block)
        CodeGenerator.takeSnapshotOfWorkspace(sessionId);

        var motor4 = CodeGenerator.generateMotorBlock(speed2 * -1, 1 + (channel2)%2);
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
        CodeGenerator.structureLabelString += "waittime";
        CodeGenerator.fullLabelString += waittime;

        var delayBlock = CodeGenerator.workspace.newBlock('dwenguino_delay');
        delayBlock.initSvg();
        delayBlock.render();
        CodeGenerator.structureLabelString += "wait";
        CodeGenerator.fullLabelString += "wait";

        var delayBlockTimeConnection = delayBlock.getInput('DELAY_TIME').connection;
        delayBlockTimeConnection.connect(delayTimeBlock.outputConnection);
        return delayBlock;
  },
  generateMotorBlock: function(speed, number){
        var motorBlock = CodeGenerator.workspace.newBlock('dc_motor');
        motorBlock.initSvg();
        motorBlock.render();
        CodeGenerator.structureLabelString += "dc_motor";
        CodeGenerator.fullLabelString += "dc_motor";

        var speedBlock = CodeGenerator.workspace.newBlock('math_number');
        speedBlock.setFieldValue(speed, 'NUM');
        speedBlock.initSvg();
        speedBlock.render();
        CodeGenerator.structureLabelString += "speed";
        CodeGenerator.fullLabelString += speed;

        var numberBlock = CodeGenerator.workspace.newBlock('math_number');
        numberBlock.setFieldValue(number, 'NUM')
        numberBlock.initSvg();
        numberBlock.render();
        CodeGenerator.structureLabelString += "channel";
        CodeGenerator.fullLabelString += number;

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
        CodeGenerator.structureLabelString += "for";
        CodeGenerator.fullLabelString += "for";

        var startBlock = CodeGenerator.workspace.newBlock('char_type');
        startBlock.initSvg();
        startBlock.render();
        startBlock.setFieldValue(start, 'BITMASK');
        CodeGenerator.structureLabelString += "start";
        CodeGenerator.fullLabelString += start;

        var endBlock = CodeGenerator.workspace.newBlock('char_type');
        endBlock.initSvg();
        endBlock.render();
        endBlock.setFieldValue(end, 'BITMASK');
        CodeGenerator.structureLabelString += "end";
        CodeGenerator.fullLabelString += end;

        var incBlock = CodeGenerator.workspace.newBlock('char_type');
        incBlock.initSvg();
        incBlock.render();
        incBlock.setFieldValue(inc, 'BITMASK');
        CodeGenerator.structureLabelString += "inc";
        CodeGenerator.fullLabelString += inc;

        forBlock.getInput('FROM').connection.connect(startBlock.outputConnection);
        forBlock.getInput('TO').connection.connect(endBlock.outputConnection);
        forBlock.getInput('BY').connection.connect(incBlock.outputConnection);

        return forBlock;

  },
  generateStopAtWall: function(sessionId){

        CodeGenerator.structureLabelString = "";
        CodeGenerator.fullLabelString = "";
        var speed1 = 0;
        var speed2 = 0;
        var OP = "";

        if (Math.random() < 0.5){
            speed1 = 100;
            speed2 = 0;
            OP = "GT";
        }else{
            speed1 = 0;
            speed2 = 100;
            OP = "LT";
        }

        CodeGenerator.structureLabelString = "";
        CodeGenerator.fullLabelString = "";
        var parentBlock = CodeGenerator.workspace.newBlock('setup_loop_structure');
        parentBlock.initSvg();
        parentBlock.render();

        var setupConnection = parentBlock.getInput('SETUP').connection;
        var loopConnection = parentBlock.getInput('LOOP').connection;

        var conn1 = null;
        var conn2 = null;
        if (Math.random() < 0.7){
            conn1 = setupConnection;
            conn2 = loopConnection;
            CodeGenerator.structureLabelString += "setuploop";
            CodeGenerator.fullLabelString += "setuploop";
            CodeGenerator.takeSnapshotOfWorkspace(sessionId);
        } else {
            conn1 = loopConnection;
            conn2 = setupConnection;
            CodeGenerator.structureLabelString += "loopsetup";
            CodeGenerator.fullLabelString += "loopsetup";
            CodeGenerator.takeSnapshotOfWorkspace(sessionId);
        }

        var lcdBlock = CodeGenerator.generateLCDBlock();
        conn1.connect(lcdBlock.previousConnection);
        CodeGenerator.takeSnapshotOfWorkspace(sessionId);

        var ifBlock = null;
        var ifConnectedFirst = false;
        if (Math.random() < 0.5){
            ifBlock = CodeGenerator.generateIfStatement();
            conn2.connect(ifBlock.previousConnection);
            ifConnectedFirst = true;
            CodeGenerator.takeSnapshotOfWorkspace(sessionId);
        }

        if (!ifConnectedFirst){
            ifBlock = CodeGenerator.generateIfStatement();
        }

        var condition = CodeGenerator.workspace.newBlock('logic_compare');
        condition.initSvg();
        condition.render();
        CodeGenerator.structureLabelString += "condition";
        CodeGenerator.fullLabelString += "condition";
        ifBlock.getInput("IF0").connection.connect(condition.outputConnection);
        if (ifConnectedFirst) {CodeGenerator.takeSnapshotOfWorkspace(sessionId);}

        var motor1 = CodeGenerator.generateMotorBlock(speed1, 1);
        ifBlock.getInput("DO0").connection.connect(motor1.previousConnection);
        if (ifConnectedFirst) {CodeGenerator.takeSnapshotOfWorkspace(sessionId);}

        var motor2 = CodeGenerator.generateMotorBlock(speed1, 2);
        motor1.nextConnection.connect(motor2.previousConnection);
        if (ifConnectedFirst) {CodeGenerator.takeSnapshotOfWorkspace(sessionId);}

        var motor3 = CodeGenerator.generateMotorBlock(speed2, 1);
        ifBlock.getInput("ELSE").connection.connect(motor3.previousConnection);
        if (ifConnectedFirst) {CodeGenerator.takeSnapshotOfWorkspace(sessionId);}

        var motor4 = CodeGenerator.generateMotorBlock(speed2, 2);
        motor3.nextConnection.connect(motor4.previousConnection);
        if (ifConnectedFirst) {CodeGenerator.takeSnapshotOfWorkspace(sessionId);}

        condition.setFieldValue(OP, "OP");

        var sonarBlock = CodeGenerator.generateSonarBlock();
        condition.getInput("A").connection.connect(sonarBlock.outputConnection);
        if (ifConnectedFirst) {CodeGenerator.takeSnapshotOfWorkspace(sessionId);}


        var distanceBlock = CodeGenerator.workspace.newBlock('char_type');
        distanceBlock.initSvg();
        distanceBlock.render();
        CodeGenerator.structureLabelString += "distance";
        CodeGenerator.fullLabelString += "distance";
        distanceBlock.setFieldValue(30, "BITMASK");
        condition.getInput("B").connection.connect(distanceBlock.outputConnection);
        if (ifConnectedFirst) {CodeGenerator.takeSnapshotOfWorkspace(sessionId);}

        if (!ifConnectedFirst){
            conn2.connect(ifBlock.previousConnection);
            CodeGenerator.takeSnapshotOfWorkspace(sessionId);
        }

        CodeGenerator.workspace.clear();
  },
  generateSonarBlock: function(){
        var sonarBlock = CodeGenerator.workspace.newBlock("sonar_sensor");
        sonarBlock.initSvg();
        sonarBlock.render();
        CodeGenerator.structureLabelString += "sonar";
        CodeGenerator.fullLabelString += "sonar";

        var trig = CodeGenerator.workspace.newBlock("char_type");
        trig.setFieldValue(11, "BITMASK");
        trig.initSvg();
        trig.render();
        CodeGenerator.structureLabelString += "trig";
        CodeGenerator.fullLabelString += 11;

        var echo = CodeGenerator.workspace.newBlock("char_type");
        echo.setFieldValue(12, "BITMASK");
        echo.initSvg();
        echo.render();
        CodeGenerator.structureLabelString += "echo";
        CodeGenerator.fullLabelString += 12;

        sonarBlock.getInput("trig").connection.connect(trig.outputConnection);
        sonarBlock.getInput("echo").connection.connect(echo.outputConnection);

        return sonarBlock;

  },
  generateLCDBlock: function(){
        var textBlock = CodeGenerator.workspace.newBlock('text');
        textBlock.initSvg();
        textBlock.render();
        textBlock.setFieldValue('Tom Neutens', 'TEXT');
        CodeGenerator.structureLabelString += "text";
        CodeGenerator.fullLabelString += "Tom Neutens";

        var rowBlock = CodeGenerator.workspace.newBlock('char_type');
        rowBlock.initSvg();
        rowBlock.render();
        rowBlock.setFieldValue(0, 'BITMASK');
        CodeGenerator.structureLabelString += "char_type";
        CodeGenerator.fullLabelString += "0";

        var columnBlock = CodeGenerator.workspace.newBlock('char_type');
        columnBlock.initSvg();
        columnBlock.render();
        columnBlock.setFieldValue(0, 'BITMASK');
        CodeGenerator.structureLabelString += "char_type";
        CodeGenerator.fullLabelString += "0";

        var lcdBlock = CodeGenerator.workspace.newBlock('dwenguino_lcd');
        lcdBlock.initSvg();
        lcdBlock.render();
        CodeGenerator.structureLabelString += "dwenguino_lcd";
        CodeGenerator.fullLabelString += "dwenguino_lcd";
        lcdBlock.getInput('text').connection.connect(textBlock.outputConnection);
        lcdBlock.getInput('line_number').connection.connect(rowBlock.outputConnection);
        lcdBlock.getInput('character_number').connection.connect(columnBlock.outputConnection);

        return lcdBlock;
  },
  generateIfStatement: function(){
        var ifBlock = CodeGenerator.workspace.newBlock('controls_if');
        ifBlock.initSvg();
        ifBlock.render();
        CodeGenerator.structureLabelString += "ifelse";
        CodeGenerator.fullLabelString += "ifelse";
        ifBlock.elseCount_ = 1;
        ifBlock.updateShape_();

        return ifBlock;
  },
  generateSteeredRobot: function(sessionId){
        CodeGenerator.structureLabelString = "";
        CodeGenerator.fullLabelString = "";
        var parentBlock = CodeGenerator.workspace.newBlock('setup_loop_structure');
        parentBlock.initSvg();
        parentBlock.render();

        var setupConnection = parentBlock.getInput('SETUP').connection;
        var loopConnection = parentBlock.getInput('LOOP').connection;
        CodeGenerator.structureLabelString += "loop";
        CodeGenerator.fullLabelString += "loop";

        var ifElseIfElse = CodeGenerator.generateIfElseIfElse();
        ifElseIfElse.previousConnection.connect(loopConnection);
        CodeGenerator.takeSnapshotOfWorkspace(sessionId);

        var condition = CodeGenerator.workspace.newBlock('logic_compare');
        condition.initSvg();
        condition.render();
        CodeGenerator.structureLabelString += "condition";
        CodeGenerator.fullLabelString += "condition";

        ifElseIfElse.getInput("IF0").connection.connect(condition.outputConnection);
        CodeGenerator.takeSnapshotOfWorkspace(sessionId);

        var pressed = CodeGenerator.workspace.newBlock('dwenguino_pressed');
        pressed.setFieldValue("PRESSED", "BOOL");
        pressed.initSvg();
        pressed.render();
        CodeGenerator.structureLabelString += "pressed";
        CodeGenerator.fullLabelString += "pressed";

        condition.getInput("A").connection.connect(pressed.outputConnection);
        CodeGenerator.takeSnapshotOfWorkspace(sessionId);

        var readSwitch = CodeGenerator.workspace.newBlock("dwenguino_digital_read_switch");
        readSwitch.initSvg();
        readSwitch.render();
        CodeGenerator.structureLabelString += "digitalreadswitch";
        CodeGenerator.fullLabelString += "SW_W";

        condition.getInput("B").connection.connect(readSwitch.outputConnection);
        CodeGenerator.takeSnapshotOfWorkspace(sessionId);

        var motor1 = CodeGenerator.generateMotorBlock(100, 1);
        var motor2 = CodeGenerator.generateMotorBlock(-100, 2);
        var ledBlock1 = CodeGenerator.generateLedBlock("0b10000000");

        ifElseIfElse.getInput("DO0").connection.connect(motor1.previousConnection);
        CodeGenerator.takeSnapshotOfWorkspace(sessionId);
        motor1.nextConnection.connect(motor2.previousConnection);
        CodeGenerator.takeSnapshotOfWorkspace(sessionId);
        motor2.nextConnection.connect(ledBlock1.previousConnection);
        CodeGenerator.takeSnapshotOfWorkspace(sessionId);

       var condition2 = CodeGenerator.workspace.newBlock('logic_compare');
        condition2.initSvg();
        condition2.render();
        CodeGenerator.structureLabelString += "condition";
        CodeGenerator.fullLabelString += "condition";

        var pressed2 = CodeGenerator.workspace.newBlock('dwenguino_pressed');
        pressed2.setFieldValue("PRESSED", "BOOL");
        pressed2.initSvg();
        pressed2.render();
        CodeGenerator.structureLabelString += "pressed";
        CodeGenerator.fullLabelString += "pressed";

        condition2.getInput("A").connection.connect(pressed2.outputConnection);
        CodeGenerator.takeSnapshotOfWorkspace(sessionId);

        var readSwitch2 = CodeGenerator.workspace.newBlock("dwenguino_digital_read_switch");
        readSwitch2.initSvg();
        readSwitch2.render();
        CodeGenerator.structureLabelString += "digitalreadswitch";
        CodeGenerator.fullLabelString += "SW_W";

        condition2.getInput("B").connection.connect(readSwitch2.outputConnection);
        CodeGenerator.takeSnapshotOfWorkspace(sessionId);

        ifElseIfElse.getInput("IF1").connection.connect(condition2.outputConnection);

        var motor3 = CodeGenerator.generateMotorBlock(-100, 1);
        var motor4 = CodeGenerator.generateMotorBlock(100, 2);
        var ledBlock2 = CodeGenerator.generateLedBlock("0b00000001");

        ifElseIfElse.getInput("DO1").connection.connect(motor3.previousConnection);
        CodeGenerator.takeSnapshotOfWorkspace(sessionId);
        motor3.nextConnection.connect(motor4.previousConnection);
        CodeGenerator.takeSnapshotOfWorkspace(sessionId);
        motor4.nextConnection.connect(ledBlock2.previousConnection);
        CodeGenerator.takeSnapshotOfWorkspace(sessionId);

        var motor5 = CodeGenerator.generateMotorBlock(-100, 1);
        var motor6 = CodeGenerator.generateMotorBlock(100, 2);
        var ledBlock3 = CodeGenerator.generateLedBlock("0b00000000");

        ifElseIfElse.getInput("ELSE").connection.connect(motor5.previousConnection);
        CodeGenerator.takeSnapshotOfWorkspace(sessionId);
        motor5.nextConnection.connect(motor6.previousConnection);
        CodeGenerator.takeSnapshotOfWorkspace(sessionId);
        motor6.nextConnection.connect(ledBlock3.previousConnection);
        CodeGenerator.takeSnapshotOfWorkspace(sessionId);

        var wait = CodeGenerator.generateWaitBlock(100);
        ifElseIfElse.nextConnection.connect(wait.previousConnection);
        CodeGenerator.takeSnapshotOfWorkspace(sessionId);

        CodeGenerator.workspace.clear();


  },
  generateIfElseIfElse: function(){
        var ifElseIfElse = CodeGenerator.workspace.newBlock("controls_if");
        ifElseIfElse.initSvg();
        ifElseIfElse.render();
        ifElseIfElse.elseifCount_ = 1;
        ifElseIfElse.elseCount_ = 1;
        ifElseIfElse.updateShape_();
        CodeGenerator.structureLabelString += "if_elseif_else";
        CodeGenerator.fullLabelString += "if_elseif_else";

        return ifElseIfElse;
  },
  generateLedBlock: function(value){
        var led_value = CodeGenerator.workspace.newBlock("char_type");
        led_value.initSvg();
        led_value.render();
        led_value.setFieldValue(value, "BITMASK");
        CodeGenerator.structureLabelString += "char_type";
        CodeGenerator.fullLabelString += value;

        var ledBlock = CodeGenerator.workspace.newBlock('dwenguino_leds_reg');
        ledBlock.initSvg();
        ledBlock.render();
        CodeGenerator.structureLabelString += "dwenguino_leds_reg";
        CodeGenerator.fullLabelString += "dwenguino_leds_reg";

        ledBlock.getInput("MASK").connection.connect(led_value.outputConnection);

        return ledBlock;

  },
  /*
    * This function submits an event to the python logging server.
    */
    recordEvent: function(eventToRecord, sessionId){
      var serverSubmission = {
        "sessionId": sessionId.toString(),
        "structureLabelString": CodeGenerator.structureLabelString,
        "fullLabelString": CodeGenerator.fullLabelString,
        "agegroup": 0,
        "gender": 0,
        "activityId": 0,
        "timestamp": $.now(),
        "event": eventToRecord
      };
      console.log(serverSubmission);
      if (sessionId !== undefined){
        $.ajax({
            type: "POST",
            crossDomain : true,
            url: "http://localhost:8081/sessions/update",
            data: {"logEntry": JSON.stringify(serverSubmission), dbname: CodeGenerator.dbname},
        }).done(function(data){
            console.debug('Recording submitted', data);
        }).fail(function(response, status)  {
            console.warn('Failed to submit recording:', status);
        });
      }
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
    CodeGenerator.setDBName("Generated2")

    for (var i = 0 ; i < 200 ; i++){
        var rand = Math.random();
        if (rand < 0.5){
            CodeGenerator.generateRandomCorrectCodeTree(i);
        } else if (rand >= 0.5 && rand < 0.8){
            CodeGenerator.generateStopAtWall(i);
        } else {
            CodeGenerator.generateSteeredRobot(i);
        }

    }
})


