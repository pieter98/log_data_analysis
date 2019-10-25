var DwenguinoBackgroundSimulation = {
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
    //"spyrograph": new DwenguinoBackgroundSimulationScenarioSpyrograph() /*, "moving", "wall", "spyrograph"*/
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
    document.getElementById('sonar_input').value = DwenguinoBackgroundSimulation.board.sonarDistance;

    $("a[href$='#db_robot_pane']").text(MSG.simulator['scenario']);
    $("a[href$='#db_code_pane']").text(MSG.simulator['code']);
  },



  /*
  * Simulator event handlers
  */

  handleSimulationStop: function(){
    DwenguinoBlockly.recordEvent(DwenguinoBlockly.createEvent("simStop", ""));
    DwenguinoBackgroundSimulation.isSimulationRunning = false;
    DwenguinoBackgroundSimulation.isSimulationPaused = false;
    DwenguinoBackgroundSimulation.setButtonsStop();
    DwenguinoBackgroundSimulation.stopSimulation();
    DwenguinoBackgroundSimulation.hideSonar();
    DwenguinoBackgroundSimulation.lcdBacklightOff();
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
        for (var i = 0 ; i < 256 ; i++){
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
        return reducedHistogram;
  },

  getStateVectorHash: function(stateVector){
        this.rand = new Math.seedrandom('fixedseed');
  },

  getCurrentStateVector: function(){
     var stateVector = [];
     stateVector.push(Math.ceil(DwenguinoBackgroundSimulation.board.buzzer.tonePlaying/100)/10);
     // Limit values to valid range and go from continuous to cathegorical.
     for (var i = 0 ; i < 2 ; i++){
        stateVector.push(Math.floor(Math.min(Math.max(DwenguinoBackgroundSimulation.board.servoAngles[i], 0), 180)/18)/10);
        stateVector.push(Math.floor(Math.max(Math.min(DwenguinoBackgroundSimulation.board.motorSpeeds[i], 255), -255)/25)/10);
     }
     for (var i = 0 ; i < DwenguinoBackgroundSimulation.board.leds.length ; i++){
        stateVector.push(DwenguinoBackgroundSimulation.board.leds[i]);
     }
     // Button state is generated so directly related to the rest of the board state.
     /*
     for (var i = 0 ; i < DwenguinoBackgroundSimulation.board.buttons.length ; i++){
        stateVector.push(DwenguinoBackgroundSimulation.board.buttons[i]);
     }*/

    var line1Hist = DwenguinoBackgroundSimulation.generateStringHistogram(DwenguinoBackgroundSimulation.board.lcdContent[0]);
    var line2Hist = DwenguinoBackgroundSimulation.generateStringHistogram(DwenguinoBackgroundSimulation.board.lcdContent[1]);
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
  stateLoggingInterval: 33,
  timeIntervalMultiplier: 47,

  generateSimulatedData: function(steps, inits){
    DwenguinoBackgroundSimulation.initDebugger();
    DwenguinoBackgroundSimulation.generatedSteps = 0;
    var totalStateVector = [];
    DwenguinoBackgroundSimulation.currentScenario.reseedRandom();

    for (var i = 0 ; i < inits ; i++){
    // Initialize new random simulation state.
    DwenguinoBackgroundSimulation.currentScenario.initSimulationState();
    DwenguinoBackgroundSimulation.generatedSteps = 0;
    DwenguinoBackgroundSimulation.initDebugger();
        while (DwenguinoBackgroundSimulation.generatedSteps < steps){
            totalStateVector = DwenguinoBackgroundSimulation.generateStep(steps, totalStateVector);
        }
    }
    DwenguinoBackgroundSimulation.stopSimulation();
    var groupedVector = [];
    // groupedVector = totalStateVector; // If not grouping: set this line and remove the following two for loops.
    for (var i = 0 ; i < totalStateVector[0].length ; i++){
        for (var j = 0 ; j < totalStateVector.length ; j++){
            groupedVector.push(totalStateVector[j][i]);
        }
    }
    return groupedVector;

  },
  generateStep: function(steps, totalStateVector) {

    var line = DwenguinoBackgroundSimulation.debugger.debuggerjs.machine.getCurrentLoc().start.line - 1;
    DwenguinoBackgroundSimulation.debugger.debuggerjs.machine.step();


    // Get current line
    var code = DwenguinoBackgroundSimulation.debugger.code.split("\n")[line] === undefined ? '' : DwenguinoBackgroundSimulation.debugger.code.split("\n")[line];


    if (code == undefined){
        throw "code is undefined";
    }
    /*if (code.trim().startsWith("if")){
        console.log("if statement");
    }*/

    // check if current line is not a sleep
    if (code.trim().startsWith("DwenguinoBackgroundSimulation.sleep")) {
      // sleep
      var delayTime = Number(DwenguinoBackgroundSimulation.debugger.code.split("\n")[line].replace(/\D+/g, ''));
      var delayStepsTaken = 0;
      var delayStepsToTake = delayTime; //Math.floor(Math.log(delayTime) * DwenguinoBackgroundSimulation.timeIntervalMultiplier);
      for (delayStepsTaken = 0 ; delayStepsTaken < delayStepsToTake && DwenguinoBackgroundSimulation.generatedSteps < steps ; delayStepsTaken++){
        DwenguinoBackgroundSimulation.board = DwenguinoBackgroundSimulation.currentScenario.updateScenario(DwenguinoBackgroundSimulation.board);
        DwenguinoBackgroundSimulation.generatedSteps++;
        if (DwenguinoBackgroundSimulation.generatedSteps % DwenguinoBackgroundSimulation.stateLoggingInterval == 0){
            var currentState = DwenguinoBackgroundSimulation.getCurrentStateVector();
            totalStateVector.push(currentState);
            //totalStateVector = totalStateVector.concat(currentState);
        }
      }
    }else{
        // Update the scenario View
        DwenguinoBackgroundSimulation.board = DwenguinoBackgroundSimulation.currentScenario.updateScenario(DwenguinoBackgroundSimulation.board);
        DwenguinoBackgroundSimulation.generatedSteps++;
        if (DwenguinoBackgroundSimulation.generatedSteps %  DwenguinoBackgroundSimulation.stateLoggingInterval == 0){
            var currentState = DwenguinoBackgroundSimulation.getCurrentStateVector();
            totalStateVector.push(currentState);
            //totalStateVector = totalStateVector.concat(currentState);
        }
    }
    DwenguinoBackgroundSimulation.checkForEnd();
    return totalStateVector;
  },


  /* -------------------------------------------------------------------------
  * Functions for handling the simulator controls
  ----------------------------------------------------------------------------*/

  /*
  * Starts the simulation for the current code
  */
  startSimulation: function() {
    DwenguinoBackgroundSimulation.startDebuggingView();
    DwenguinoBackgroundSimulation.initDebugger();
    // run debugger
    DwenguinoBackgroundSimulation.step();
  },
  /*
  * Starts the simulation for the current code with 1 step
  */
  startStepSimulation: function() {
    DwenguinoBackgroundSimulation.startDebuggingView();
    DwenguinoBackgroundSimulation.initDebugger();
    // run debugger
    DwenguinoBackgroundSimulation.oneStep();
  },
  /*
  * Stops the simulation and resets the view
  */
  stopSimulation: function() {
    DwenguinoBackgroundSimulation.stopDebuggingView();
    DwenguinoBackgroundSimulation.resetDwenguino();
  },
  /*
  * resumes a simulation that was paused
  */
  resumeSimulation: function() {
    // restart driving robot
    //TODO: restart the timed update loop

    DwenguinoBackgroundSimulation.step();
  },

  setupDebugger: function(){
    // create debugger
    DwenguinoBackgroundSimulation.debugger.debuggerjs = debugjs.createDebugger({
      iframeParentElement: document.getElementById('debug'),
      // declare context that should be available in debugger
      sandbox: {
        DwenguinoBackgroundSimulation: DwenguinoBackgroundSimulation
      }
    });

    DwenguinoBackgroundSimulation.debugger.debuggerjs.machine.on('error', function(err) {
      console.error(err.message);
      throw "Debugging machine fail";
    });
  },


  /*
  * initialize the debugging environment
  */
  initDebugger: function() {
    // initialize simulation
    DwenguinoBackgroundSimulation.initDwenguino();

    // get code
    DwenguinoBackgroundSimulation.debugger.code = Blockly.JavaScript.workspaceToCode(DwenguinoBlockly.workspace);
    //DwenguinoBackgroundSimulation.mapBlocksToCode();


    var filename = 'DwenguinoBackgroundSimulation';
    DwenguinoBackgroundSimulation.debugger.debuggerjs.load(DwenguinoBackgroundSimulation.debugger.code, filename);

    // Performs a single step to start the debugging process, hihglights the setup loop block.
    DwenguinoBackgroundSimulation.debugger.debuggerjs.machine.step();
    //DwenguinoBackgroundSimulation.updateBlocklyColour();
  },

  /*
  * While the simulation is running, this function keeps being called with "speeddelay" timeouts in between
  */
  step: function() {
    if (!DwenguinoBackgroundSimulation.isSimulationRunning) {
      return;
    }

    var line = DwenguinoBackgroundSimulation.debugger.debuggerjs.machine.getCurrentLoc().start.line - 1;
    DwenguinoBackgroundSimulation.debugger.debuggerjs.machine.step();

    // highlight the current block
    DwenguinoBackgroundSimulation.updateBlocklyColour();
    DwenguinoBackgroundSimulation.handleScope();

    // Get current line
    var code = DwenguinoBackgroundSimulation.debugger.code.split("\n")[line] === undefined ? '' : DwenguinoBackgroundSimulation.debugger.code.split("\n")[line];

    // Update the scenario View
    DwenguinoBackgroundSimulation.board = DwenguinoBackgroundSimulation.currentScenario.updateScenario(DwenguinoBackgroundSimulation.board);

    // check if current line is not a sleep
    if (!code.trim().startsWith("DwenguinoBackgroundSimulation.sleep")) {
      setTimeout(DwenguinoBackgroundSimulation.step, DwenguinoBackgroundSimulation.speedDelay);
    } else {
      // sleep
      var delayTime = Number(DwenguinoBackgroundSimulation.debugger.code.split("\n")[line].replace(/\D+/g, ''));
      DwenguinoBackgroundSimulation.delayStepsTaken = 0;
      DwenguinoBackgroundSimulation.delayStepsToTake = Math.floor(delayTime/DwenguinoBackgroundSimulation.baseSpeedDelay);
      DwenguinoBackgroundSimulation.delayRemainingAfterSteps = delayTime % DwenguinoBackgroundSimulation.baseSpeedDelay;
      DwenguinoBackgroundSimulation.performDelayLoop(DwenguinoBackgroundSimulation.step);
    }
    DwenguinoBackgroundSimulation.checkForEnd();
  },
  /*
   *  This function iterates until the delay has passed
   */
  performDelayLoop: function(returnCallback){
    // Here we want the simulation to keep running but not let the board state update.
    // To do so we execute the updateScenario() function of the current scenario delay/speedDelay times
    // with an interval of speedDelay.
    if (DwenguinoBackgroundSimulation.delayStepsTaken < DwenguinoBackgroundSimulation.delayStepsToTake){
      // Update the scenario View
      DwenguinoBackgroundSimulation.board = DwenguinoBackgroundSimulation.currentScenario.updateScenario(DwenguinoBackgroundSimulation.board);
      DwenguinoBackgroundSimulation.delayStepsTaken++;
      setTimeout(function(){
        DwenguinoBackgroundSimulation.performDelayLoop(returnCallback);
      }, DwenguinoBackgroundSimulation.speedDelay);
    } else {
      setTimeout(returnCallback, DwenguinoBackgroundSimulation.delayRemainingAfterSteps);
    }
  },

  /*
  * Lets the simulator run one step
  */
  oneStep: function() {
    // let driving robot update 1 frame
    // Update the scenario View
    DwenguinoBackgroundSimulation.board = DwenguinoBackgroundSimulation.currentScenario.updateScenario(DwenguinoBackgroundSimulation.board);

    // Get current line
    var line = DwenguinoBackgroundSimulation.debugger.debuggerjs.machine.getCurrentLoc().start.line - 1;
    var code = DwenguinoBackgroundSimulation.debugger.code.split("\n")[line] === undefined ? '' : DwenguinoBackgroundSimulation.debugger.code.split("\n")[line];

    DwenguinoBackgroundSimulation.debugger.debuggerjs.machine.step();
    DwenguinoBackgroundSimulation.updateBlocklyColour();
    DwenguinoBackgroundSimulation.handleScope();
    DwenguinoBackgroundSimulation.checkForEnd();

    // check if current line is not a sleep
    if (code.trim().startsWith("DwenguinoBackgroundSimulation.sleep")) {
      // sleep
      var delayTime = Number(DwenguinoBackgroundSimulation.debugger.code.split("\n")[line].replace(/\D+/g, ''));
      DwenguinoBackgroundSimulation.delayStepsTaken = 0;
      DwenguinoBackgroundSimulation.delayStepsToTake = Math.floor(delayTime/DwenguinoBackgroundSimulation.baseSpeedDelay);
      DwenguinoBackgroundSimulation.delayRemainingAfterSteps = delayTime % DwenguinoBackgroundSimulation.baseSpeedDelay;
      DwenguinoBackgroundSimulation.performDelayLoop(function(){/*Do nothing after delay loop*/});
    }


  },


  /*
  * Displays the values of the variables during the simulation
  */
  handleScope: function() {
    var scope = DwenguinoBackgroundSimulation.debugger.debuggerjs.machine.getCurrentStackFrame().scope;
    //document.getElementById('sim_scope').innerHTML = "";
    for (var i in scope) {
      var item = scope[i];
      var value = DwenguinoBackgroundSimulation.debugger.debuggerjs.machine.$runner.gen.stackFrame.evalInScope(item.name);
      //document.getElementById('sim_scope').innerHTML = document.getElementById('sim_scope').innerHTML + item.name + " = " + value + "<br>";
    }
  },

  /*
  * Checks if the simulation has been interrupted
  */
  checkForEnd: function() {
    if ((DwenguinoBackgroundSimulation.isSimulationRunning || DwenguinoBackgroundSimulation.isSimulationPaused) &&
    DwenguinoBackgroundSimulation.debugger.debuggerjs.machine.halted) {
      DwenguinoBackgroundSimulation.isSimulationRunning = false;
      DwenguinoBackgroundSimulation.isSimulationPaused = false;
    }
  },

  /*
  * maps line numbers to blocks
  */
  mapBlocksToCode: function() {
    var setup_block = DwenguinoBlockly.workspace.getAllBlocks()[0];

    var line = 0;
    var lines = DwenguinoBackgroundSimulation.debugger.code.split("\n");
    var loopBlocks = [];

    // update variables in while loop when searching for a match between block and line
    function updateBlocks() {
      // special structure for loop blocks -> look at children
      if (lines[line].trim() === Blockly.JavaScript.blockToCode(block).split('\n')[0] &&
      (lines[line].trim().startsWith("for") || lines[line].trim().startsWith("while") ||
      lines[line].trim().startsWith("if"))) {
        loopBlocks.push(block);
        DwenguinoBackgroundSimulation.debugger.blocks.blockMapping[line] = block;
        block = block.getInputTargetBlock('DO') || block.getInputTargetBlock('DO0');
      } else if (lines[line].trim() === Blockly.JavaScript.blockToCode(block).split('\n')[0]) {
        DwenguinoBackgroundSimulation.debugger.blocks.blockMapping[line] = block;
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
      DwenguinoBackgroundSimulation.debugger.blocks.blockMapping[line] = setup_block;
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

    var line = DwenguinoBackgroundSimulation.debugger.debuggerjs.machine.getCurrentLoc().start.line - 1;
    if (DwenguinoBackgroundSimulation.debugger.code !== "" && typeof DwenguinoBackgroundSimulation.debugger.blocks.blockMapping[line] !== 'undefined') {
      // reset old block
      if (DwenguinoBackgroundSimulation.debugger.blocks.lastBlocks[0] !== null) {
        DwenguinoBackgroundSimulation.debugger.blocks.lastBlocks[0].setColour(DwenguinoBackgroundSimulation.debugger.blocks.lastColours[0]);
      }

      DwenguinoBackgroundSimulation.debugger.blocks.lastBlocks[0] = DwenguinoBackgroundSimulation.debugger.blocks.lastBlocks[1];
      DwenguinoBackgroundSimulation.debugger.blocks.lastColours[0] = DwenguinoBackgroundSimulation.debugger.blocks.lastColours[1];

      // highlight current block
      DwenguinoBackgroundSimulation.debugger.blocks.lastBlocks[1] = DwenguinoBackgroundSimulation.debugger.blocks.blockMapping[line];
      DwenguinoBackgroundSimulation.debugger.blocks.lastColours[1] = DwenguinoBackgroundSimulation.debugger.blocks.blockMapping[line].getColour();

      if (DwenguinoBackgroundSimulation.debugger.blocks.lastBlocks[0] !== null) {
        DwenguinoBackgroundSimulation.debugger.blocks.lastBlocks[0].setColour(highlight_colour);
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
      DwenguinoBackgroundSimulation.speedDelay = 600;
      break;
      case "slow":
      DwenguinoBackgroundSimulation.speedDelay = 300;
      break;
      case "medium":
      DwenguinoBackgroundSimulation.speedDelay = 150;
      break;
      case "fast":
      DwenguinoBackgroundSimulation.speedDelay = 75;
      break;
      case "veryfast":
      DwenguinoBackgroundSimulation.speedDelay = 32;
      break;
      case "realtime":
      DwenguinoBackgroundSimulation.speedDelay = 16;
    }
  },

  /*
  * Makes the simulation ready (draw the board)
  */
  initDwenguino: function() {
    //Reset the Dwenguino board display
    DwenguinoBackgroundSimulation.resetDwenguino();
  },

  /*
  * Resets the dwenguino (drawing) to its initial state (remove text, no sound etc)
  */
  resetDwenguino: function() {
    // delete debugger
    //DwenguinoBackgroundSimulation.debugger.debuggerjs = null;
    DwenguinoBackgroundSimulation.debugger.code = "";
    DwenguinoBackgroundSimulation.debugger.blocks.blockMapping = {};

    // reset colours
    if (DwenguinoBackgroundSimulation.debugger.blocks.lastColours[0] !== -1) {
      DwenguinoBackgroundSimulation.debugger.blocks.lastBlocks[0].setColour(DwenguinoBackgroundSimulation.debugger.blocks.lastColours[0]);
    }
    DwenguinoBackgroundSimulation.debugger.blocks.lastColours = [-1, -1];
    DwenguinoBackgroundSimulation.debugger.blocks.lastBlocks = [null, null];

    // stop sound
    if (DwenguinoBackgroundSimulation.board.buzzer.tonePlaying !== 0) {
      DwenguinoBackgroundSimulation.noTone("BUZZER");
    }
    // clearn lcd
    DwenguinoBackgroundSimulation.clearLcd();
    // turn all lights out
    DwenguinoBackgroundSimulation.board.leds = [0,0,0,0,0,0,0,0,0];
    for (var i = 0; i < 8; i++) {
      document.getElementById('sim_light_' + i).className = "sim_light sim_light_off";
    }
    document.getElementById('sim_light_13').className = "sim_light sim_light_off";

    // reset servo
    DwenguinoBackgroundSimulation.board.servoAngles = [0, 0];
    //$("#sim_servo1_mov, #sim_servo2_mov").css("transform", "rotate(0deg)");

    // reset motors
    DwenguinoBackgroundSimulation.board.motorSpeeds = [0, 0];
    //$("#sim_motor1, #sim_motor2").css("transform", "rotate(0deg)");

    //reset buttons
    DwenguinoBackgroundSimulation.board.buttons = [1,1,1,1,1];
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
        DwenguinoBackgroundSimulation.board.lcdContent[i] = " ".repeat(16);
        DwenguinoBackgroundSimulation.writeLcd(" ".repeat(16), i, 1);
      }
    },

    /*
    * Writes text to the lcd on the given row starting fro position column
    * @param {string} text: text to write
    * @param {int} row: 0 or 1 addresses the row
    * @param {int} column: 0-15: the start position on the given row
    */
    writeLcd: function(text, row, column) {
      DwenguinoBackgroundSimulation.lcdBacklightOn();
      // replace text in current content (if text is hello and then a is written this gives aello)
      text = DwenguinoBackgroundSimulation.board.lcdContent[row].substr(0, column) +
      text.substring(0, 16 - column) +
      DwenguinoBackgroundSimulation.board.lcdContent[row].substr(text.length + column, 16);
      DwenguinoBackgroundSimulation.board.lcdContent[row] = text;

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
          pin=== 13? DwenguinoBackgroundSimulation.board.leds[8] = 1 : DwenguinoBackgroundSimulation.board.leds[pin] = 1;
          document.getElementById('sim_light_' + pin).className = "sim_light sim_light_on";
        } else {
          pin === 13? DwenguinoBackgroundSimulation.board.leds[8] = 0 : DwenguinoBackgroundSimulation.board.leds[pin] = 0;
          document.getElementById('sim_light_' + pin).className = "sim_light sim_light_off";
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
      // read value from buttons
      if (pin.startsWith("SW_")) {
        return document.getElementById("sim_button_" + pin[3]).className === "sim_button" ? 1 : 0;
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
        DwenguinoBackgroundSimulation.digitalWrite(i+30, bin[i]);
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
      if (DwenguinoBackgroundSimulation.board.buzzer.osc === null) {
        // initiate sound object
        try {
          DwenguinoBackgroundSimulation.board.buzzer.audiocontext = new(window.AudioContext || window.webkitAudioContext)();
        } catch (e) {
          alert('Web Audio API is not supported in this browser');
        }
        //DwenguinoBackgroundSimulation.board.sound.audiocontextBuzzer = new AudioContext();
      }
      if (DwenguinoBackgroundSimulation.board.buzzer.tonePlaying !== 0 && DwenguinoBackgroundSimulation.board.buzzer.tonePlaying !== frequency) {
        DwenguinoBackgroundSimulation.board.buzzer.osc.stop();
      }
      if (DwenguinoBackgroundSimulation.board.buzzer.tonePlaying !== frequency) {
        // a new oscilliator for each round
        DwenguinoBackgroundSimulation.board.buzzer.osc = DwenguinoBackgroundSimulation.board.buzzer.audiocontext.createOscillator(); // instantiate an oscillator
        DwenguinoBackgroundSimulation.board.buzzer.osc.type = 'sine'; // this is the default - also square, sawtooth, triangle

        // start tone
        DwenguinoBackgroundSimulation.board.buzzer.osc.frequency.value = frequency; // Hz
        DwenguinoBackgroundSimulation.board.buzzer.osc.connect(DwenguinoBackgroundSimulation.board.buzzer.audiocontext.destination); // connect it to the destination
        DwenguinoBackgroundSimulation.board.buzzer.osc.start(); // start the oscillator

        DwenguinoBackgroundSimulation.board.buzzer.tonePlaying = frequency;
      }
    },

    /*
    * Stops the buzzer
    * @param {string} id of the pin "BUZZER"
    */
    noTone: function(pin) {
      if (pin === "BUZZER") {
        // stop tone
        DwenguinoBackgroundSimulation.board.buzzer.tonePlaying = 0;
        DwenguinoBackgroundSimulation.board.buzzer.osc.stop();
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

      if (angle !== DwenguinoBackgroundSimulation.board.servoAngles[channel - 1]) {
        DwenguinoBackgroundSimulation.board.servoAngles[channel - 1] = angle;
        DwenguinoBackgroundSimulation.servoRotate(channel, angle);
      }
    },

    /*
    * Renders the movement of the servo
    * @param {int} channel id of servo 1 or 2
    * @param {int} angle between 0 and 180
    */
    servoRotate: function(channel, angle) {
      var maxMovement = 10;
      if (angle !== DwenguinoBackgroundSimulation.board.servoAngles[channel - 1]) {
        return;
      }
      //var prevAngle = DwenguinoBackgroundSimulation.getAngle($("#sim_servo" + channel + "_mov"));
      // set 10 degrees closer at a time to create rotate effect
      /*if (Math.abs(angle - prevAngle) > maxMovement) {
        var direction = ((angle - prevAngle) > 0) ? 1 : -1;
        $("#sim_servo" + channel + "_mov").css("transform", "rotate(" + (prevAngle + direction * maxMovement) + "deg)");
        setTimeout(function() {
          DwenguinoBackgroundSimulation.servoRotate(channel, angle);
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
      if (speed === DwenguinoBackgroundSimulation.board.motorSpeeds[channel - 1]) {
        return;
      }
      DwenguinoBackgroundSimulation.board.motorSpeeds[channel - 1] = speed;
      DwenguinoBackgroundSimulation.dcMotorRotate(channel, speed);

      // change view of driving robot
      var e = document.getElementById("sim_scenario");
      //var option = e.options[e.selectedIndex].value;

    },

    /*
    * Renders the rotation of the motor
    * @param {int} channel id of motor 1 or 2
    * @param {int} speed between 0 and 255
    */
    dcMotorRotate: function(channel, speed) {
      var maxMovement = speed / 20 + 5;
      if (speed !== DwenguinoBackgroundSimulation.board.motorSpeeds[channel - 1] && speed !== 0) {
        return;
      }
      //var prevAngle = DwenguinoBackgroundSimulation.getAngle($("#sim_motor" + channel));
      // rotate x degrees at a time based on speed
      //$("#sim_motor" + channel).css("transform", "rotate(" + ((prevAngle + maxMovement) % 360) + "deg)");

      DwenguinoBackgroundSimulation.timeout = setTimeout(function() {
        DwenguinoBackgroundSimulation.dcMotorRotate(channel, speed);
      }, 20);
    },
    /*
    * Returns the distance between the sonar and teh wall
    * @param {int} trigPin 11
    * @param {int} echoPin 12
    * @returns {int} distance in cm
    */
    sonar: function(trigPin, echoPin) {
      DwenguinoBackgroundSimulation.showSonar();
      //document.getElementById("sonar").checked = true;
      document.getElementById('sonar_input').value = DwenguinoBackgroundSimulation.board.sonarDistance;
      return this.board.sonarDistance;
    },

    /*
    * Adjust css when simulation is started
    */
    setButtonsStart: function() {
      // enable pauze and stop
      document.getElementById('sim_pause').className = "sim_item";
      document.getElementById('sim_stop').className = "sim_item";
      // disable start and step
      document.getElementById('sim_start').className = "sim_item disabled";
      document.getElementById('sim_step').className = "sim_item disabled";
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
