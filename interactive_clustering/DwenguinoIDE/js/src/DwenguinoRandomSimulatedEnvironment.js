/*
 * This Object is the abstraction of the random robot scenario for data generation
 * It handles the layout and behaviour of a certain simulator scenario.
 * It provides a step function which uses and updates the state of the dwenguino board.
 * For example it uses the motor speed states to change the location of a robot or changes the sonar distance state depending on how far it is form an object.
 *
 */
function DwenguinoRandomSimulatedEnvironment(){
  if (!(this instanceof DwenguinoRandomSimulatedEnvironment)){
    return new DwenguinoRandomSimulatedEnvironment();
  }
  //call super prototype
  DwenguinoSimulationScenario.call(this);
  //Init predictable random generator
  this.rand = new Math.seedrandom('fixedseed');
  //init robot state
  this.initSimulationState();

}

DwenguinoRandomSimulatedEnvironment.prototype.reseedRandom = function(){
    this.rand = new Math.seedrandom('fixedseed');
}

/* @brief Initializes the simulator robot.
 * This resets the simulation state.
 *
 * @param containerIdSelector The jquery selector of the conainer to put the robot display.
 *
 */
DwenguinoRandomSimulatedEnvironment.prototype.initSimulationState = function(){
  // init superclass
   DwenguinoSimulationScenario.prototype.initSimulationState.call(this);
   this.tick = 0;
   // Randomize start state based on seed
   var w = 10 + Math.floor(this.rand() * 100);
   var h = 10 + Math.floor(this.rand() * 100);
   var startX = Math.floor(this.rand() * w);
   var startY = Math.floor(this.rand() * h)
   var startAngle = Math.floor(this.rand() * 360);
   this.robot = {
     image: {
       width: w,
       height: h
     },
     start: {
       x: startX,
       y: startY,
       angle: startAngle
     },
     position: {
       x: startX,
       y: startY,
       angle: startAngle
     },
     collision: [{
       type: 'circle',
       radius: 25
     }]
   };
 }

/* @brief Initializes the simulator robot display.
 * This function puts all the nececary visuals inside the container with the id containerId.
 * Additionally, it sets up the state of the simulated robot.
 * The function also resets the internal state of the simulation so the display is initialized from its original position.
 *
 * @param containerIdSelector The jquery selector of the conainer to put the robot display.
 *
 */
DwenguinoRandomSimulatedEnvironment.prototype.initSimulationDisplay = function(containerIdSelector){
  // init superclass
   DwenguinoSimulationScenario.prototype.initSimulationDisplay.call(this, containerIdSelector);


};

/* @brief updates the simulation state and display
 * This function updates the simulation state and display using the supplied board state.
 *
 * @param boardState The state of the Dwenguino board.
 * @return The updated Dwenguino board state.
 *
 */
DwenguinoRandomSimulatedEnvironment.prototype.updateScenario = function(dwenguinoState){
    var state = DwenguinoSimulationScenario.prototype.updateScenario.call(this, dwenguinoState);
    state = this.updateScenarioState(state);
  return state;
;
};

/* @brief updates the simulation state
 * This function updates the simulation state using the supplied board state.
 *
 * @param boardState The state of the Dwenguino board. It has the following structure:
 * {
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
 }
 * @return The updated Dwenguino board state.
 *
 */
DwenguinoRandomSimulatedEnvironment.prototype.updateScenarioState = function(dwenguinoState){
  DwenguinoSimulationScenario.prototype.updateScenarioState.call(this, dwenguinoState);
  var returnState = dwenguinoState
  this.tick += 1;
  this.tick = this.tick % 10000;

  // Pick the distance to the closest intersecting line.
  var D = Math.sin(this.tick/Math.PI*50) * 250;


  if (isNaN(D)){
    returnState.sonarDistance = -1;
  }else{
    returnState.sonarDistance = D;
  }


  // Generate random button presses
  for (var i = 0 ; i < 5 ; i++){
    var B = Math.sin(this.tick/(15));
    if (B < 0){
        returnState.buttons[i] = 0;
    }else{
        returnState.buttons[i] = 1;
    }

  }

  return returnState;
};

DwenguinoRandomSimulatedEnvironment.prototype.calcDistanceBetweenPoints = function(p1, p2){
  return Math.sqrt((p2[0] - p1[0])*(p2[0] - p1[0])+(p2[1] - p1[1])*(p2[1] - p1[1]));
};

/* @brief updates the simulation display
 * This function updates the simulation display using the supplied board state.
 *
 * @param boardState The state of the Dwenguino board.
 *
 */
DwenguinoRandomSimulatedEnvironment.prototype.updateScenarioDisplay = function(dwenguinoState){
  DwenguinoSimulationScenario.prototype.updateScenarioDisplay.call(this, dwenguinoState);

  /*var robot = this.robot;
  var $robot = $('#sim_animation');

  // Update field size
  this.containerWidth = $("#sim_container").width();
  this.containerHeight = $("#sim_container").height();

  $robot
  .css('top', this.robot.position.y + 'px')
  .css('left', this.robot.position.x + 'px')
  .css('transform', 'rotate(' + this.robot.position.angle + 'deg)');*/
};
