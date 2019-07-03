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
  var speed1 = dwenguinoState.motorSpeeds[0];
  var speed2 = dwenguinoState.motorSpeeds[1];

  // Save the current state of the robot into local variables.
  var x = this.robot.position.x;
  var y = this.robot.position.y;
  var angle = this.robot.position.angle;

  // decide on angle (in deg) and distance (in px) based on 2 motor speeds
  var distance = (speed1 + speed2) / 100;

  if (speed1 !== speed2) {
    angle += ((speed2 - speed1) / 30)%360;
  }

  x += distance * Math.cos(Math.PI / 180 * angle);
  y += distance * Math.sin(Math.PI / 180 * angle);

  // move to other side of frame if out of frame
  if (x > this.containerWidth - this.robot.image.width){
    x = this.containerWidth - this.robot.image.width;
  }else if (x < 0){
    x = 0;
  }
  if (y > this.containerHeight - this.robot.image.height){
    y = this.containerHeight - this.robot.image.height;
  } else if (y < 0) {
    y = 0;
  }

  // Calulate distance to wall
  //calculate distance between front of car and wall

  var xMiddle = x;
  var yMiddle = y;

  angle = ((angle % 360)+360)%360;  // Normalize angle

  var xFront = xMiddle + (this.robot.image.width/2) * Math.cos(Math.PI / 180 * angle);
  var yFront = yMiddle + (this.robot.image.width/2) * Math.sin(Math.PI / 180 * angle);


  //Calculate the intersection point between the two possible intersecting horizontal and vertical lines
  // and the line through the robot with a slope defined by its angle.
  var intersectionPoint = [0, 0];
  var intersectionLiness = [[this.containerWidth, this.containerHeight], [0, this.containerHeight], [0, 0], [this.containerWidth, 0]];
  var intersectionPointX = [0, 0];
  var intersectionPointY = [0, 0];

  // do edge cases first
  if (angle == 90){
    intersectionPointX = intersectionPointY = [xFront, this.containerHeight];
  } else if (angle == 270){
    intersectionPointX = intersectionPointY = [xFront, 0];
  } else if (angle == 180){
    intersectionPointX = intersectionPointY = [0, yFront];
  } else if (angle == 0){
    intersectionPointX = intersectionPointY = [this.containerWidth, yFront];
  } else {
    var slope = Math.tan(angle);
    var intersectionLines = intersectionLiness[Math.floor(angle/90)%4];
    intersectionPointX = [intersectionLines[0], Math.tan(angle*Math.PI / 180) * (intersectionLines[0] - xFront) + yFront];
    intersectionPointY = [(intersectionLines[1] - yFront) / Math.tan(angle*Math.PI / 180) + xFront, intersectionLines[1]];
  }

  // Pick the distance to the closest intersecting line.
  var D = Math.min(this.calcDistanceBetweenPoints(intersectionPointX, [xFront, yFront]),
      this.calcDistanceBetweenPoints(intersectionPointY, [xFront, yFront]));

  dwenguinoState.sonarDistance = Math.abs(D - 25); // Compensate for borders

  if (isNaN(dwenguinoState.sonarDistance)){
    dwenguinoState.sonarDistance = -1;
  }

  this.robot.position = {
    x: x,
    y: y,
    angle: angle
  };

  // Generate random button presses
  for (var i = 0 ; i < 5 ; i++){
    var test = this.rand();
    if (test < 0.5){
        dwenguinoState.buttons[i] = 0;
    }else{
        dwenguinoState.buttons[i] = 1;
    }

  }

  return dwenguinoState;
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
