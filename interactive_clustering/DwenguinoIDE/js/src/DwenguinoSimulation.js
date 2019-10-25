var DwenguinoSimulation = {
  board: {
    lcdContent: new Array(2),
    buzzer: {
      osc: null,
      audiocontext: null,
      tonePlaying: 0
    },
    servoAngles: [0, 0],
    motorSpeeds: [0, 0],
    leds: [0,0,0,0,0,0,0,0,0],
    buttons: [1,1,1,1,1],
    sonarDistance: 50
  },

  isSimulationRunning: false,
  isSimulationPaused: false,
  speedDelay: 50,
  baseSpeedDelay: 100,
  debuggingView: false,
  scenarios: {
    "randomSimulatedEnvironment": new DwenguinoRandomSimulatedEnvironment(),
    //"spyrograph": new DwenguinoSimulationScenarioSpyrograph() /*, "moving", "wall", "spyrograph"*/
  },
  currentScenario: null,
  scenarioView: "randomSimulatedEnvironment",
  simulationViewContainerId: "#db_robot_pane",
  debugger: {
    debuggerjs: null,
    code: "",
    blocks: {
      lastBlocks: [null, null],
      lastColours: [-1, -1],
      blockMapping: {}
    }
  },
  /*
  * Initializes the environment when loading page
  */
  setupEnvironment: function(scenarioView) {
    this.currentScenario = this.scenarios[scenarioView];
    this.setupDebugger();
  },

  translateSimulatorInterface: function(){
    // translation
    document.getElementById('sim_start').innerHTML = "<span class='glyphicon glyphicon-play' alt='" + MSG.simulator['start'] + "'></span>";
    document.getElementById('sim_stop').innerHTML = "<span class='glyphicon glyphicon-stop' alt='" + MSG.simulator['stop'] + "'></span>";
    document.getElementById('sim_pause').innerHTML = "<span class='glyphicon glyphicon-pause' alt='" + MSG.simulator['pause'] + "'></span>";
    document.getElementById('sim_step').innerHTML = "<span class='glyphicon glyphicon-step-forward' alt='" + MSG.simulator['step'] + "'></span>";

    /*document.getElementById('sim_speedTag').textContent = MSG.simulator['speed'] + ":";

    document.getElementById('sim_speed_verySlow').textContent = MSG.simulator['speedVerySlow'];
    document.getElementById('sim_speed_slow').textContent = MSG.simulator['speedSlow'];
    document.getElementById('sim_speed_medium').textContent = MSG.simulator['speedMedium'];
    document.getElementById('sim_speed_fast').textContent = MSG.simulator['speedFast'];
    document.getElementById('sim_speed_veryFast').textContent = MSG.simulator['speedVeryFast'];
    document.getElementById('sim_speed_realTime').textContent = MSG.simulator['speedRealTime'];*/

    document.getElementById('sim_scenarioTag').textContent = MSG.simulator['scenario'];


    //document.getElementById('sim_components_select').textContent = MSG.simulator['components'] + ":";
    //document.getElementById('servo1').textContent = MSG.simulator['servo'] + " 1";
    //document.getElementById('servo2').textContent = MSG.simulator['servo'] + " 2";
    //document.getElementById('motor1').textContent = MSG.simulator['motor'] + " 1";
    //document.getElementById('motor2').textContent = MSG.simulator['motor'] + " 2";
    //document.getElementById('sim_scope_name').textContent = MSG.simulator['scope'] + ":";
    //TODO: put back sonar input
    document.getElementById('sim_sonar_distance').textContent = "Sonar " + MSG.simulator['distance'] + ":";
    document.getElementById('sonar_input').value = DwenguinoSimulation.board.sonarDistance;

    $("a[href$='#db_robot_pane']").text(MSG.simulator['scenario']);
    $("a[href$='#db_code_pane']").text(MSG.simulator['code']);
  },



  /*
  * Simulator event handlers
  */

  handleSimulationStop: function(){
    DwenguinoBlockly.recordEvent(DwenguinoBlockly.createEvent("simStop", ""));
    DwenguinoSimulation.isSimulationRunning = false;
    DwenguinoSimulation.isSimulationPaused = false;
    DwenguinoSimulation.setButtonsStop();
    DwenguinoSimulation.stopSimulation();
    DwenguinoSimulation.hideSonar();
    DwenguinoSimulation.lcdBacklightOff();
  },
  showSonar: function(){
    $("#sim_sonar").show();
    $("#sim_sonar_distance").show();
    $("#sim_sonar_input").show();
  },
  hideSonar: function(){
    $("#sim_sonar").hide();
    $("#sim_sonar_distance").hide();
    $("#sim_sonar_input").hide();
  },
  lcdBacklightOn: function(){
    $("#sim_lcds").addClass("on");
  },
  lcdBacklightOff: function(){
    $("#sim_lcds").removeClass("on");
  },

 /* board: {
    lcdContent: new Array(2),
    buzzer: {
      osc: null,
      audiocontext: null,
      tonePlaying: 0
    },
    servoAngles: [0, 0],
    motorSpeeds: [0, 0],
    leds: [0,0,0,0,0,0,0,0,0],
    buttons: [1,1,1,1,1],
    sonarDistance: 50
  },*/

  generateStringHistogram: function(text){
        var histogram = [];
        var histogram = [];
        var letterMapping =
        {'0': 0,
         '1': 1,
         '2': 2,
         '3': 3,
         '4': 4,
         '5': 5,
         '6': 6,
         '7': 7,
         '8': 8,
         '9': 9,
         'e': 10,
         'n': 11,
         'a': 12,
         't': 13,
         'i': 13,
         'o': 14,
         'd': 14,
         's': 15,
         'l': 15,
         'g': 15,
         'v': 15,
         'h': 15,
         'k': 16,
         'm': 16,
         'u': 16,
         'b': 16,
         'p': 16,
         'w': 16,
         'j': 16,
         'z': 17,
         'c': 17,
         'f': 17,
         'x': 17,
         'y': 17,
         'q': 17,
         };

        for (var i = 0 ; i  < 18 ; i++){
            histogram[i] = 0;
        }
        var textLower = text.toLowerCase();
        for (var i = 0 ; i < textLower.length ; i++){
            var letter = textLower.charAt(i);
            if (letter in letterMapping){
                histogram[letterMapping[letter]]++;
            }

        }
        return histogram;
        /*for (var i = 0 ; i < 256 ; i++){
            histogram[i] = 0;
        }
        var textLower = text.toLowerCase();
        for (var i = 0 ; i < textLower.length ; i++){
            var letterCode = textLower.charCodeAt(i);
            if (letterCode < histogram.length){
                histogram[letterCode]++;
            }
        }
        var reducedHistogram = [];
        // Add numbers
        for (var i = 48 ; i < 58 ; i++){
            reducedHistogram.push(histogram[i]);
        }
        // Add lowercase letters
        for (var i = 97 ; i < 126 ; i++){
            reducedHistogram.push(histogram[i]);
        }
        return reducedHistogram;*/
  },

  getStateVectorHash: function(stateVector){
        this.rand = new Math.seedrandom('fixedseed');
  },

  getCurrentStateVector: function(){
     var stateVector = [];
     stateVector.push(Math.ceil(DwenguinoSimulation.board.buzzer.tonePlaying/100)/10);
     // Limit values to valid range and go from continuous to cathegorical.
     for (var i = 0 ; i < 2 ; i++){
        stateVector.push(Math.floor(Math.min(Math.max(DwenguinoSimulation.board.servoAngles[i], 0), 180)/18)/10);
        stateVector.push(Math.floor(Math.max(Math.min(DwenguinoSimulation.board.motorSpeeds[i], 255), -255)/25)/10);
     }
     for (var i = 0 ; i < DwenguinoSimulation.board.leds.length ; i++){
        stateVector.push(DwenguinoSimulation.board.leds[i]);
     }
     // Button state is generated so directly related to the rest of the board state.
     /*
     for (var i = 0 ; i < DwenguinoSimulation.board.buttons.length ; i++){
        stateVector.push(DwenguinoSimulation.board.buttons[i]);
     }*/

    var line1Hist = DwenguinoSimulation.generateStringHistogram(DwenguinoSimulation.board.lcdContent[0]);
    var line2Hist = DwenguinoSimulation.generateStringHistogram(DwenguinoSimulation.board.lcdContent[1]);
    for (var i = 0 ; i < line1Hist.length ; i++){
        stateVector.push((line1Hist[i] + line2Hist[i])/16); // Normalize (max 16x the same char on screen)
    }
    // merge state into one value
    state = 0;
    state = stateVector;
    /*for (var i = 0 ; i < stateVector.length ; i++){
        state += stateVector[i];
    }*/
    return state;

  },
  generatedSteps: 0,
  stateLoggingInterval: 1300,
  timeIntervalMultiplier: 47,

  generateSimulatedData: function(steps, inits){
    DwenguinoSimulation.initDebugger();
    DwenguinoSimulation.generatedSteps = 0;
    var totalStateVector = [];
    DwenguinoSimulation.currentScenario.reseedRandom();



    for (var i = 0 ; i < inits ; i++){
    // Initialize new random simulation state.
    DwenguinoSimulation.currentScenario.initSimulationState();
    DwenguinoSimulation.generatedSteps = 0;
    DwenguinoSimulation.initDebugger();

    DwenguinoSimulation.code = DwenguinoSimulation.debugger.code.split("\n");
    
        while (DwenguinoSimulation.generatedSteps < steps){
            totalStateVector = DwenguinoSimulation.generateStep(steps, totalStateVector);
        }
    }
    DwenguinoSimulation.stopSimulation();
    var groupedVector = [];
    // groupedVector = totalStateVector; // If not grouping: set this line and remove the following two for loops.
    for (var i = 0 ; i < totalStateVector[0].length ; i++){
        for (var j = 0 ; j < totalStateVector.length ; j++){
            groupedVector.push(totalStateVector[j][i]);
        }
    }
    return groupedVector;

  },
  code: '',
  generateStep: function(steps, totalStateVector) {

    var line = DwenguinoSimulation.debugger.debuggerjs.machine.getCurrentLoc().start.line - 1;
    DwenguinoSimulation.debugger.debuggerjs.machine.step();


    // Get current line
    var code = DwenguinoSimulation.code[line];

    if (code === undefined){
        code = "";
    }

    if (code == undefined){
        throw "code is undefined";
    }
    /*if (code.trim().startsWith("if")){
        console.log("if statement");
    }*/

    // check if current line is not a sleep
    if (code.trim().startsWith("DwenguinoSimulation.sleep")) {
      // sleep
      var delayTime = Number(DwenguinoSimulation.debugger.code.split("\n")[line].replace(/\D+/g, ''));
      var delayStepsTaken = 0;
      var delayStepsToTake = delayTime*100; //Math.floor(Math.log(delayTime) * DwenguinoSimulation.timeIntervalMultiplier);
      for (delayStepsTaken = 0 ; delayStepsTaken < delayStepsToTake && DwenguinoSimulation.generatedSteps < steps ; delayStepsTaken++){
        DwenguinoSimulation.board = DwenguinoSimulation.currentScenario.updateScenario(DwenguinoSimulation.board);
        DwenguinoSimulation.generatedSteps++;
        if (DwenguinoSimulation.generatedSteps % DwenguinoSimulation.stateLoggingInterval == 0){
            var currentState = DwenguinoSimulation.getCurrentStateVector();
            totalStateVector.push(currentState);
            //totalStateVector = totalStateVector.concat(currentState);
        }
      }
    }else{
        // Update the scenario View
        DwenguinoSimulation.board = DwenguinoSimulation.currentScenario.updateScenario(DwenguinoSimulation.board);
        DwenguinoSimulation.generatedSteps++;
        if (DwenguinoSimulation.generatedSteps %  DwenguinoSimulation.stateLoggingInterval == 0){
            var currentState = DwenguinoSimulation.getCurrentStateVector();
            totalStateVector.push(currentState);
            //totalStateVector = totalStateVector.concat(currentState);
        }
    }
    DwenguinoSimulation.checkForEnd();
    return totalStateVector;
  },


  /* -------------------------------------------------------------------------
  * Functions for handling the simulator controls
  ----------------------------------------------------------------------------*/

  /*
  * Starts the simulation for the current code
  */
  startSimulation: function() {
    DwenguinoSimulation.startDebuggingView();
    DwenguinoSimulation.initDebugger();
    // run debugger
    DwenguinoSimulation.step();
  },
  /*
  * Starts the simulation for the current code with 1 step
  */
  startStepSimulation: function() {
    DwenguinoSimulation.startDebuggingView();
    DwenguinoSimulation.initDebugger();
    // run debugger
    DwenguinoSimulation.oneStep();
  },
  /*
  * Stops the simulation and resets the view
  */
  stopSimulation: function() {
    DwenguinoSimulation.stopDebuggingView();
    DwenguinoSimulation.resetDwenguino();
  },
  /*
  * resumes a simulation that was paused
  */
  resumeSimulation: function() {
    // restart driving robot
    //TODO: restart the timed update loop

    DwenguinoSimulation.step();
  },

  setupDebugger: function(){
    // create debugger
    DwenguinoSimulation.debugger.debuggerjs = debugjs.createDebugger({
      iframeParentElement: document.getElementById('debug'),
      // declare context that should be available in debugger
      sandbox: {
        DwenguinoSimulation: DwenguinoSimulation
      }
    });

    DwenguinoSimulation.debugger.debuggerjs.machine.on('error', function(err) {
      console.error(err.message);
      throw "Debugging machine fail";
    });
  },


  /*
  * initialize the debugging environment
  */
  initDebugger: function() {
    // initialize simulation
    DwenguinoSimulation.initDwenguino();

    // get code
    DwenguinoSimulation.debugger.code = Blockly.JavaScript.workspaceToCode(DwenguinoBlockly.workspace);
    //DwenguinoSimulation.mapBlocksToCode();


    var filename = 'DwenguinoSimulation';
    DwenguinoSimulation.debugger.debuggerjs.load(DwenguinoSimulation.debugger.code, filename);

    // Performs a single step to start the debugging process, hihglights the setup loop block.
    DwenguinoSimulation.debugger.debuggerjs.machine.step();
    //DwenguinoSimulation.updateBlocklyColour();
  },

  /*
  * While the simulation is running, this function keeps being called with "speeddelay" timeouts in between
  */
  step: function() {
    if (!DwenguinoSimulation.isSimulationRunning) {
      return;
    }

    var line = DwenguinoSimulation.debugger.debuggerjs.machine.getCurrentLoc().start.line - 1;
    DwenguinoSimulation.debugger.debuggerjs.machine.step();

    // highlight the current block
    DwenguinoSimulation.updateBlocklyColour();
    DwenguinoSimulation.handleScope();

    // Get current line
    var code = DwenguinoSimulation.debugger.code.split("\n")[line] === undefined ? '' : DwenguinoSimulation.debugger.code.split("\n")[line];

    // Update the scenario View
    DwenguinoSimulation.board = DwenguinoSimulation.currentScenario.updateScenario(DwenguinoSimulation.board);

    // check if current line is not a sleep
    if (!code.trim().startsWith("DwenguinoSimulation.sleep")) {
      setTimeout(DwenguinoSimulation.step, DwenguinoSimulation.speedDelay);
    } else {
      // sleep
      var delayTime = Number(DwenguinoSimulation.debugger.code.split("\n")[line].replace(/\D+/g, ''));
      DwenguinoSimulation.delayStepsTaken = 0;
      DwenguinoSimulation.delayStepsToTake = Math.floor(delayTime/DwenguinoSimulation.baseSpeedDelay);
      DwenguinoSimulation.delayRemainingAfterSteps = delayTime % DwenguinoSimulation.baseSpeedDelay;
      DwenguinoSimulation.performDelayLoop(DwenguinoSimulation.step);
    }
    DwenguinoSimulation.checkForEnd();
  },
  /*
   *  This function iterates until the delay has passed
   */
  performDelayLoop: function(returnCallback){
    // Here we want the simulation to keep running but not let the board state update.
    // To do so we execute the updateScenario() function of the current scenario delay/speedDelay times
    // with an interval of speedDelay.
    if (DwenguinoSimulation.delayStepsTaken < DwenguinoSimulation.delayStepsToTake){
      // Update the scenario View
      DwenguinoSimulation.board = DwenguinoSimulation.currentScenario.updateScenario(DwenguinoSimulation.board);
      DwenguinoSimulation.delayStepsTaken++;
      setTimeout(function(){
        DwenguinoSimulation.performDelayLoop(returnCallback);
      }, DwenguinoSimulation.speedDelay);
    } else {
      setTimeout(returnCallback, DwenguinoSimulation.delayRemainingAfterSteps);
    }
  },

  /*
  * Lets the simulator run one step
  */
  oneStep: function() {
    // let driving robot update 1 frame
    // Update the scenario View
    DwenguinoSimulation.board = DwenguinoSimulation.currentScenario.updateScenario(DwenguinoSimulation.board);

    // Get current line
    var line = DwenguinoSimulation.debugger.debuggerjs.machine.getCurrentLoc().start.line - 1;
    var code = DwenguinoSimulation.debugger.code.split("\n")[line] === undefined ? '' : DwenguinoSimulation.debugger.code.split("\n")[line];

    DwenguinoSimulation.debugger.debuggerjs.machine.step();
    DwenguinoSimulation.updateBlocklyColour();
    DwenguinoSimulation.handleScope();
    DwenguinoSimulation.checkForEnd();

    // check if current line is not a sleep
    if (code.trim().startsWith("DwenguinoSimulation.sleep")) {
      // sleep
      var delayTime = Number(DwenguinoSimulation.debugger.code.split("\n")[line].replace(/\D+/g, ''));
      DwenguinoSimulation.delayStepsTaken = 0;
      DwenguinoSimulation.delayStepsToTake = Math.floor(delayTime/DwenguinoSimulation.baseSpeedDelay);
      DwenguinoSimulation.delayRemainingAfterSteps = delayTime % DwenguinoSimulation.baseSpeedDelay;
      DwenguinoSimulation.performDelayLoop(function(){/*Do nothing after delay loop*/});
    }


  },


  /*
  * Displays the values of the variables during the simulation
  */
  handleScope: function() {
    var scope = DwenguinoSimulation.debugger.debuggerjs.machine.getCurrentStackFrame().scope;
    //document.getElementById('sim_scope').innerHTML = "";
    for (var i in scope) {
      var item = scope[i];
      var value = DwenguinoSimulation.debugger.debuggerjs.machine.$runner.gen.stackFrame.evalInScope(item.name);
      //document.getElementById('sim_scope').innerHTML = document.getElementById('sim_scope').innerHTML + item.name + " = " + value + "<br>";
    }
  },

  /*
  * Checks if the simulation has been interrupted
  */
  checkForEnd: function() {
    if ((DwenguinoSimulation.isSimulationRunning || DwenguinoSimulation.isSimulationPaused) &&
    DwenguinoSimulation.debugger.debuggerjs.machine.halted) {
      DwenguinoSimulation.isSimulationRunning = false;
      DwenguinoSimulation.isSimulationPaused = false;
    }
  },

  /*
  * maps line numbers to blocks
  */
  mapBlocksToCode: function() {
    var setup_block = DwenguinoBlockly.workspace.getAllBlocks()[0];

    var line = 0;
    var lines = DwenguinoSimulation.debugger.code.split("\n");
    var loopBlocks = [];

    // update variables in while loop when searching for a match between block and line
    function updateBlocks() {
      // special structure for loop blocks -> look at children
      if (lines[line].trim() === Blockly.JavaScript.blockToCode(block).split('\n')[0] &&
      (lines[line].trim().startsWith("for") || lines[line].trim().startsWith("while") ||
      lines[line].trim().startsWith("if"))) {
        loopBlocks.push(block);
        DwenguinoSimulation.debugger.blocks.blockMapping[line] = block;
        block = block.getInputTargetBlock('DO') || block.getInputTargetBlock('DO0');
      } else if (lines[line].trim() === Blockly.JavaScript.blockToCode(block).split('\n')[0]) {
        DwenguinoSimulation.debugger.blocks.blockMapping[line] = block;
        block = block.getNextBlock();
      }
      // end of loop structure
      if (block === null && loopBlocks.length > 0) {
        var parentBlock = loopBlocks.pop();
        block = parentBlock.getNextBlock();
        line++;
      }
      line++;
    };

    // look at blocks before while
    var block = setup_block.getInputTargetBlock('SETUP');
    while (block !== null && line < lines.length) {
      updateBlocks();
    }

    while (loopBlocks.length > 0) {
      loopBlocks.pop();
      line++;
    }

    // look at while
    while (line < lines.length && lines[line] !== "while (true) {") {
      line++;
    }
    if (line < lines.length) {
      DwenguinoSimulation.debugger.blocks.blockMapping[line] = setup_block;
      line++;
    }

    // look at blocks after while
    block = setup_block.getInputTargetBlock('LOOP');
    while (block !== null && line < lines.length) {
      updateBlocks();
    }
  },

  /*
  * Changes the color of the blocks at each iteration of the simulator
  * The block that was previously executed is highlighted (=blue)
  */
  updateBlocklyColour: function() {
    var highlight_colour = 210;

    var line = DwenguinoSimulation.debugger.debuggerjs.machine.getCurrentLoc().start.line - 1;
    if (DwenguinoSimulation.debugger.code !== "" && typeof DwenguinoSimulation.debugger.blocks.blockMapping[line] !== 'undefined') {
      // reset old block
      if (DwenguinoSimulation.debugger.blocks.lastBlocks[0] !== null) {
        DwenguinoSimulation.debugger.blocks.lastBlocks[0].setColour(DwenguinoSimulation.debugger.blocks.lastColours[0]);
      }

      DwenguinoSimulation.debugger.blocks.lastBlocks[0] = DwenguinoSimulation.debugger.blocks.lastBlocks[1];
      DwenguinoSimulation.debugger.blocks.lastColours[0] = DwenguinoSimulation.debugger.blocks.lastColours[1];

      // highlight current block
      DwenguinoSimulation.debugger.blocks.lastBlocks[1] = DwenguinoSimulation.debugger.blocks.blockMapping[line];
      DwenguinoSimulation.debugger.blocks.lastColours[1] = DwenguinoSimulation.debugger.blocks.blockMapping[line].getColour();

      if (DwenguinoSimulation.debugger.blocks.lastBlocks[0] !== null) {
        DwenguinoSimulation.debugger.blocks.lastBlocks[0].setColour(highlight_colour);
      }
    }
  },

  /*
  * updates the speed of the simulation
  */
  setSpeed: function() {
    var e = document.getElementById("sim_speed");
    var option = e.options[e.selectedIndex].value;

    DwenguinoBlockly.recordEvent(DwenguinoBlockly.createEvent("setSpeed", option));

    switch (option) {
      case "veryslow":
      DwenguinoSimulation.speedDelay = 600;
      break;
      case "slow":
      DwenguinoSimulation.speedDelay = 300;
      break;
      case "medium":
      DwenguinoSimulation.speedDelay = 150;
      break;
      case "fast":
      DwenguinoSimulation.speedDelay = 75;
      break;
      case "veryfast":
      DwenguinoSimulation.speedDelay = 32;
      break;
      case "realtime":
      DwenguinoSimulation.speedDelay = 16;
    }
  },

  /*
  * Makes the simulation ready (draw the board)
  */
  initDwenguino: function() {
    //Reset the Dwenguino board display
    DwenguinoSimulation.resetDwenguino();
  },

  /*
  * Resets the dwenguino (drawing) to its initial state (remove text, no sound etc)
  */
  resetDwenguino: function() {
    // delete debugger
    //DwenguinoSimulation.debugger.debuggerjs = null;
    DwenguinoSimulation.debugger.code = "";
    DwenguinoSimulation.debugger.blocks.blockMapping = {};

    // reset colours
    if (DwenguinoSimulation.debugger.blocks.lastColours[0] !== -1) {
      DwenguinoSimulation.debugger.blocks.lastBlocks[0].setColour(DwenguinoSimulation.debugger.blocks.lastColours[0]);
    }
    DwenguinoSimulation.debugger.blocks.lastColours = [-1, -1];
    DwenguinoSimulation.debugger.blocks.lastBlocks = [null, null];

    // stop sound
    if (DwenguinoSimulation.board.buzzer.tonePlaying !== 0) {
      DwenguinoSimulation.noTone("BUZZER");
    }
    // clearn lcd
    DwenguinoSimulation.clearLcd();
    // turn all lights out
    DwenguinoSimulation.board.leds = [0,0,0,0,0,0,0,0,0];
    for (var i = 0; i < 8; i++) {
      document.getElementById('sim_light_' + i).className = "sim_light sim_light_off";
    }
    document.getElementById('sim_light_13').className = "sim_light sim_light_off";

    // reset servo
    DwenguinoSimulation.board.servoAngles = [0, 0];
    //$("#sim_servo1_mov, #sim_servo2_mov").css("transform", "rotate(0deg)");

    // reset motors
    DwenguinoSimulation.board.motorSpeeds = [0, 0];
    //$("#sim_motor1, #sim_motor2").css("transform", "rotate(0deg)");

    //reset buttons
    DwenguinoSimulation.board.buttons = [1,1,1,1,1];
    $("#sim_button_N, #sim_button_E, #sim_button_C, #sim_button_S, #sim_button_W").removeClass().addClass('sim_button');

    // clear scope
    //document.getElementById('sim_scope').innerHTML = "";
  },
  /*
    * function called by the delay block to delay the simulation
    *  @param {int} delay: time in ms the simaultion should be paused
    */
    sleep: function(delay) {
      // sleep is regulated inside step funtion
    },

    /*
    * Makes the lcd display empty
    *
    */
    clearLcd: function() {
      // clear lcd by writing spaces to it
      for (var i = 0; i < 2; i++) {
        DwenguinoSimulation.board.lcdContent[i] = " ".repeat(16);
        DwenguinoSimulation.writeLcd(" ".repeat(16), i, 1);
      }
    },

    /*
    * Writes text to the lcd on the given row starting fro position column
    * @param {string} text: text to write
    * @param {int} row: 0 or 1 addresses the row
    * @param {int} column: 0-15: the start position on the given row
    */
    writeLcd: function(text, row, column) {
      DwenguinoSimulation.lcdBacklightOn();
      // replace text in current content (if text is hello and then a is written this gives aello)
      text = DwenguinoSimulation.board.lcdContent[row].substr(0, column) +
      text.substring(0, 16 - column) +
      DwenguinoSimulation.board.lcdContent[row].substr(text.length + column, 16);
      DwenguinoSimulation.board.lcdContent[row] = text;

      // write new text to lcd screen and replace spaces with &nbsp;
      $("#sim_lcd_row" + row).text(text);
      document.getElementById('sim_lcd_row' + row).innerHTML =
      document.getElementById('sim_lcd_row' + row).innerHTML.replace(/ /g, '&nbsp;');
      // repaint
      var element = document.getElementById("sim_lcds");
      element.style.display = 'none';
      element.offsetHeight;
      element.style.display = 'block';
    },

    /*
    * Write value 'HIGH' or 'LOW' to a pin, used to turn light on and off
    * @param {int} pinNumber: 13 or 32-39 adresses a light
    * @param {string} state: 'HIGH' to trun light on or 'LOW' to turn light off
    */
    digitalWrite: function(pinNumber, state) {
      // turns light on or off
      var pin = Number(pinNumber);
      if ((pin >= 32 && pin <= 39) || pin === 13) {
        if (pin >= 32 && pin <= 39) {
          pin -= 32;
        }
        if (state === 'HIGH' || state === "1") {
          pin=== 13? DwenguinoSimulation.board.leds[8] = 1 : DwenguinoSimulation.board.leds[pin] = 1;
          //document.getElementById('sim_light_' + pin).className = "sim_light sim_light_on";
        } else {
          pin === 13? DwenguinoSimulation.board.leds[8] = 0 : DwenguinoSimulation.board.leds[pin] = 0;
          //document.getElementById('sim_light_' + pin).className = "sim_light sim_light_off";
        }
      }
    },

    analogWrite: function(pinNumber, state) {

    },

    /*
    * Reads the value of the given pin, used to know the value of a button
    * @param {string} id of the button "SW_N","SW_W,SW_C","SW_E" or "SW_S"
    * @returns {int} 1 if not pressed, 0 if pressed
    */
    digitalRead: function(pin) {
      var switches = {
        "SW_N": 0,
        "SW_W": 1,
        "SW_C": 2,
        "SW_E": 3,
        "SW_S": 4
      };

      // read value from buttons
      if (pin.startsWith("SW_")) {
        return DwenguinoSimulation.board.buttons[switches[pin]];
      }

      pin = Number(pin);
      if ((pin >= 32 && pin <= 39) || pin === 13) {
        if (pin >= 32 && pin <= 39) {
          pin -= 32;
        }
        return document.getElementById('sim_light_' + pin).className.includes("sim_light_on")? 1 : 0;
      }

      return 1;
    },

    analogRead: function(pin) {
      return 0;
    },

    /*
    * Changes the state of all eight lights
    * @param {String} bin "0b00000000" to turn all lights off, "0b11111111" to turn all lights on
    */
    setLeds: function(bin) {
      for (var i = 2; i < 10; i++) {
        DwenguinoSimulation.digitalWrite(i+30, bin[i]);
      }
    },

    /*
    * Turns the buzzer to a given frequancy
    * @param {string} id of the pin "BUZZER"
    * @param {int} frequency of the wanted sound
    */
    tone: function(pin, frequency) {
      if (pin !== "BUZZER") {
        return;
      }
      if (DwenguinoSimulation.board.buzzer.osc === null) {
        // initiate sound object
        /*try {
          DwenguinoSimulation.board.buzzer.audiocontext = new(window.AudioContext || window.webkitAudioContext)();
        } catch (e) {
          alert('Web Audio API is not supported in this browser');
        }
        //DwenguinoSimulation.board.sound.audiocontextBuzzer = new AudioContext();
      }
      if (DwenguinoSimulation.board.buzzer.tonePlaying !== 0 && DwenguinoSimulation.board.buzzer.tonePlaying !== frequency) {
        DwenguinoSimulation.board.buzzer.osc.stop();
      }
      if (DwenguinoSimulation.board.buzzer.tonePlaying !== frequency) {
        // a new oscilliator for each round
        DwenguinoSimulation.board.buzzer.osc = DwenguinoSimulation.board.buzzer.audiocontext.createOscillator(); // instantiate an oscillator
        DwenguinoSimulation.board.buzzer.osc.type = 'sine'; // this is the default - also square, sawtooth, triangle

        // start tone
        DwenguinoSimulation.board.buzzer.osc.frequency.value = frequency; // Hz
        DwenguinoSimulation.board.buzzer.osc.connect(DwenguinoSimulation.board.buzzer.audiocontext.destination); // connect it to the destination
        DwenguinoSimulation.board.buzzer.osc.start(); // start the oscillator*/

        DwenguinoSimulation.board.buzzer.tonePlaying = frequency;
      }
    },

    /*
    * Stops the buzzer
    * @param {string} id of the pin "BUZZER"
    */
    noTone: function(pin) {
      if (pin === "BUZZER") {
        // stop tone
        DwenguinoSimulation.board.buzzer.tonePlaying = 0;
        //DwenguinoSimulation.board.buzzer.osc.stop();
      }
    },

    /*
    * Sets the servo to a given angle
    * @param {int} channel id of servo 1 or 2
    * @param {int} angle between 0 and 180
    */
    servo: function(channel, angle) {
      //$("#sim_servo"+channel).show();
      //document.getElementById("servo"+channel).checked = true;

      //set angle
      if (angle > 180) {
        angle = 180;
      }
      if (angle < 0) {
        angle = 0;
      }

      if (angle !== DwenguinoSimulation.board.servoAngles[channel - 1]) {
        DwenguinoSimulation.board.servoAngles[channel - 1] = angle;
        DwenguinoSimulation.servoRotate(channel, angle);
      }
    },

    /*
    * Renders the movement of the servo
    * @param {int} channel id of servo 1 or 2
    * @param {int} angle between 0 and 180
    */
    servoRotate: function(channel, angle) {
      var maxMovement = 10;
      if (angle !== DwenguinoSimulation.board.servoAngles[channel - 1]) {
        return;
      }
      //var prevAngle = DwenguinoSimulation.getAngle($("#sim_servo" + channel + "_mov"));
      // set 10 degrees closer at a time to create rotate effect
      /*if (Math.abs(angle - prevAngle) > maxMovement) {
        var direction = ((angle - prevAngle) > 0) ? 1 : -1;
        $("#sim_servo" + channel + "_mov").css("transform", "rotate(" + (prevAngle + direction * maxMovement) + "deg)");
        setTimeout(function() {
          DwenguinoSimulation.servoRotate(channel, angle);
        }, 20);
      } else {
        $("#sim_servo" + channel + "_mov").css("transform", "rotate(" + angle + "deg)");
      }*/
    },

    /*
    * Help function to get the angle in degrees of a rotated html object
    * @param {obj} obj html object
    * @returns {int} degrees of rotation
    */
    getAngle: function(obj) {
      var matrix = obj.css("-webkit-transform") ||
      obj.css("-moz-transform") ||
      obj.css("-ms-transform") ||
      obj.css("-o-transform") ||
      obj.css("transform");
      if (matrix !== "none") {
        var values = matrix.split('(')[1];
        values = values.split(')')[0];
        values = values.split(',');
        var a = values[0];
        var b = values[1];
        return Math.round(Math.atan2(b, a) * (180 / Math.PI));
      }
      return 0;
    },

    /*
    * Turn a motor on at given speed
    * @param {int} channel id of motor 1 or 2
    * @param {int} speed between 0 and 255
    */
    startDcMotor: function(channel, speed) {
      //$("#sim_motor"+channel).show();
      //document.getElementById("motor"+channel).checked = true;

      //set angle
      if (speed > 255) {
        speed = 255;
      }
      if (speed < -255) {
        speed = -255;
      }

      // change view of motor
      if (speed === DwenguinoSimulation.board.motorSpeeds[channel - 1]) {
        return;
      }
      DwenguinoSimulation.board.motorSpeeds[channel - 1] = speed;
      //DwenguinoSimulation.dcMotorRotate(channel, speed);

      // change view of driving robot
      //var e = document.getElementById("sim_scenario");
      //var option = e.options[e.selectedIndex].value;

    },

    /*
    * Renders the rotation of the motor
    * @param {int} channel id of motor 1 or 2
    * @param {int} speed between 0 and 255
    */
    dcMotorRotate: function(channel, speed) {
      var maxMovement = speed / 20 + 5;
      if (speed !== DwenguinoSimulation.board.motorSpeeds[channel - 1] && speed !== 0) {
        return;
      }
      //var prevAngle = DwenguinoSimulation.getAngle($("#sim_motor" + channel));
      // rotate x degrees at a time based on speed
      //$("#sim_motor" + channel).css("transform", "rotate(" + ((prevAngle + maxMovement) % 360) + "deg)");

      DwenguinoSimulation.timeout = setTimeout(function() {
        DwenguinoSimulation.dcMotorRotate(channel, speed);
      }, 20);
    },
    /*
    * Returns the distance between the sonar and teh wall
    * @param {int} trigPin 11
    * @param {int} echoPin 12
    * @returns {int} distance in cm
    */
    sonar: function(trigPin, echoPin) {
      DwenguinoSimulation.showSonar();
      //document.getElementById("sonar").checked = true;
      document.getElementById('sonar_input').value = DwenguinoSimulation.board.sonarDistance;
      return this.board.sonarDistance;
    },

    /*
    * Adjust css when simulation is started
    */
    setButtonsStart: function() {
      // enable pauze and stop
      //document.getElementById('sim_pause').className = "sim_item";
      //document.getElementById('sim_stop').className = "sim_item";
      // disable start and step
      //document.getElementById('sim_start').className = "sim_item disabled";
      //document.getElementById('sim_step').className = "sim_item disabled";
    },

    /*
    * Adjust css when simulation is paused
    */
    setButtonsPause: function() {
      // enable start, stop and step
      document.getElementById('sim_start').className = "sim_item";
      document.getElementById('sim_step').className = "sim_item";
      document.getElementById('sim_stop').className = "sim_item";
      // disable pause
      document.getElementById('sim_pause').className = "sim_item disabled";
    },

    /*
    * Adjust css when simulation is stopped
    */
    setButtonsStop: function() {
      // enable start, stop and step
      document.getElementById('sim_start').className = "sim_item";
      document.getElementById('sim_step').className = "sim_item";
      // disable pause
      document.getElementById('sim_stop').className = "sim_item disabled";
      document.getElementById('sim_pause').className = "sim_item disabled";
    },

    /*
    * Adjust css when simulation is run step by step
    */
    setButtonsStep: function() {
      // enable start, stop and step
      document.getElementById('sim_start').className = "sim_item";
      document.getElementById('sim_step').className = "sim_item";
      document.getElementById('sim_stop').className = "sim_item";
      // disable pause
      document.getElementById('sim_pause').className = "sim_item disabled";
    },
    /*
    * Adjusts the view during simulation
    * disables the programming and makes the simulation pane biggger
    */
    startDebuggingView: function() {
      if (document.getElementsByClassName("alertDebug").length !== 0) {
        document.getElementsByClassName("alertDebug")[0].remove();
      }
      var alertMessage = '<div class ="alertDebug">' + MSG.simulator['alertDebug'] + '</div>';
      $('#db_body').append(alertMessage);
      document.getElementsByClassName('alertDebug')[0].style.width = document.getElementById("blocklyDiv").style.width;
      document.getElementById('blocklyDiv').style.opacity = "0.5";
      //document.getElementById('blocklyDiv').style.pointerEvents = "none";
    },
    /*
    * Returns to normal view when debugging is finished
    */
    stopDebuggingView: function() {
      document.getElementById('blocklyDiv').style.opacity = "1";
      document.getElementById('blocklyDiv').style.pointerEvents = "auto";
      if (document.getElementsByClassName("alertDebug").length !== 0) {
        document.getElementsByClassName("alertDebug")[0].remove();
      }
    },
};

// initialise js functions if version older than 2015
  if (!String.prototype.repeat) {
    String.prototype.repeat = function(num) {
      return new Array(num + 1).join(this);
    };
  }

  if (!String.prototype.startsWith) {
    String.prototype.startsWith = function(searchString, position) {
      position = position || 0;
      return this.substr(position, searchString.length) === searchString;
    };
  }
