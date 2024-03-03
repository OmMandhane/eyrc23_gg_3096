
/*
   Team Id: GG_3096
   Author List: Om Mandhane, Tanay Baisware
   Filename: esp32code
   Theme: GeoGuide
   Functions: Forward, Stop, Stop2, Right, Left, NodeAlgo, MiddleAlgo, ParallelAlgo, SinglePath, ForwardTN,
              DualPath, Right90, Left90, SlightForward, FRAD, FLAD, FRB, FLB, FRC, FLC, ParallelAlgo2, FRE,
              FLE, first_node, callFunctionByName, setup, loop
   Global Variables: LEFT_SENSOR_PIN, RIGHT_SENSOR_PIN, Middle, midleft, midright, LEFT_MOTOR_IN1, LEFT_MOTOR_IN2,
                     LEFT_MOTOR_ENA, RIGHT_MOTOR_ENB, RIGHT_MOTOR_IN3, RIGHT_MOTOR_IN4, led, buzzer, ssid, password,
                     server_ip, server_port
*/

#include <WiFi.h>
#include <WiFiClient.h>

#define LEFT_SENSOR_PIN   27  // Pin for left IR proximity sensor
#define RIGHT_SENSOR_PIN  26  // Pin for right IR proximity sensor
#define Middle 12
#define midleft 13
#define midright 14

#define LEFT_MOTOR_IN1  15// Input 1 for left motor 15
#define LEFT_MOTOR_IN2  2// Input 2 for left motor 2
#define LEFT_MOTOR_ENA  17// 17

#define RIGHT_MOTOR_ENB 5 // Enable pin for right motor (PWM) 5
#define RIGHT_MOTOR_IN3 16// Input 3 for right motor 16
#define RIGHT_MOTOR_IN4  4// Input 4 for right motor 4

int  led = 18;
int buzzer = 25;

const char *ssid = "om123";
const char *password = "123456789";
const char *server_ip = "192.168.155.229";
const int server_port = 8002;

/*
   Function Name: nodebuzz
   Input: None
   Output: None
   Logic: Turns on the buzzer for a 1 second
   Example Call: nodebuzz();
*/
void nodebuzz() {
  digitalWrite(buzzer, LOW);
  delay(1000);
  digitalWrite(buzzer, HIGH);
}

/*
   Function Name: nodebuzz
   Input: None
   Output: None
   Logic: Turns on the buzzer for a 5 second
   Example Call: nodebuzz();
*/
void nodebuzz_long() {
  digitalWrite(buzzer, LOW);
  delay(5000);
  digitalWrite(buzzer, HIGH);
}
/*
   Function Name: Forward
   Input: speed - Speed of motors
   Output: None
   Logic: Moves the robot forward with specified speed
   Example Call: Forward(255);
*/
void Forward(int speed) {
  ledcWrite(LEFT_MOTOR_ENA, speed);
  digitalWrite(LEFT_MOTOR_IN1, HIGH);
  digitalWrite(LEFT_MOTOR_IN2, LOW);

  ledcWrite(RIGHT_MOTOR_ENB, speed);
  digitalWrite(RIGHT_MOTOR_IN3, HIGH);
  digitalWrite(RIGHT_MOTOR_IN4, LOW);
}

/*
   Function Name: Stop
   Input: None
   Output: None
   Logic: Stops the robot
   Example Call: Stop();
*/
void Stop() {
  ledcWrite(LEFT_MOTOR_ENA, LOW);
  digitalWrite(LEFT_MOTOR_IN1, LOW);
  digitalWrite(LEFT_MOTOR_IN2, LOW);

  ledcWrite(RIGHT_MOTOR_ENB, LOW);
  digitalWrite(RIGHT_MOTOR_IN3, LOW);
  digitalWrite(RIGHT_MOTOR_IN4, LOW);
}

/*
   Function Name: Stop2
   Input: None
   Output: None
   Logic: Stops the robot with different motor control
   Example Call: Stop2();
*/
void Stop2() {

  digitalWrite(LEFT_MOTOR_IN1, HIGH);
  digitalWrite(LEFT_MOTOR_IN2, HIGH);

  digitalWrite(RIGHT_MOTOR_IN3, HIGH);
  digitalWrite(RIGHT_MOTOR_IN4, HIGH);
}

/*
   Function Name: Right
   Input: speed - Speed of motors
   Output: None
   Logic: Turns the robot right with specified speed
   Example Call: Right(255);
*/
void Right(int speed) {
  ledcWrite(LEFT_MOTOR_ENA, speed);
  digitalWrite(LEFT_MOTOR_IN1, HIGH);
  digitalWrite(LEFT_MOTOR_IN2, LOW);

  ledcWrite(RIGHT_MOTOR_ENB, speed);
  digitalWrite(RIGHT_MOTOR_IN3, LOW);
  digitalWrite(RIGHT_MOTOR_IN4, HIGH);
}

/*
   Function Name: Left
   Input: speed - Speed of motors
   Output: None
   Logic: Turns the robot left with specified speed
   Example Call: Left(255);
*/
void Left(int speed) {
  ledcWrite(LEFT_MOTOR_ENA, speed);
  digitalWrite(LEFT_MOTOR_IN1, LOW);
  digitalWrite(LEFT_MOTOR_IN2, HIGH);

  ledcWrite(RIGHT_MOTOR_ENB, speed);
  digitalWrite(RIGHT_MOTOR_IN3, HIGH);
  digitalWrite(RIGHT_MOTOR_IN4, LOW);
}

/*
   Function Name: NodeAlgo
   Input: None
   Output: int - Returns 1 if the robot is at a node, 0 otherwise
   Logic: Checks the sensor values to determine if the robot is at a node
   Example Call: NodeAlgo();
*/
int NodeAlgo() {
  int ML = digitalRead(midleft);
  int MM = digitalRead(Middle);
  int MRR = digitalRead(midright);
  int a = 0;
  if ( ML == HIGH && MM == HIGH && MRR == HIGH ) {
    a = 1;
  } else {
    a = 0;
  }
  return a;
}

/*
   Function Name: MiddleAlgo
   Input: None
   Output: None
   Logic: Implements the algorithm for the middle line following
   Example Call: MiddleAlgo();
*/
void MiddleAlgo() {
  int ML = digitalRead(midleft);
  int MM = digitalRead(Middle);
  int MRR = digitalRead(midright);
  if (ML == LOW && MM == HIGH && MRR == LOW) {
    Forward(255);
  } else if ((ML == HIGH && MM == HIGH && MRR == LOW) || (ML == HIGH && MM == LOW && MRR == LOW )) {
    Left(255);
  } else if ((ML == LOW && MM == HIGH && MRR == HIGH) || (ML == LOW && MM == LOW && MRR == HIGH )) {
    Right(255);
  }
}

/*
   Function Name: ParallelAlgo
   Input: None
   Output: None
   Logic: Implements the algorithm for parallel line following
   Example Call: ParallelAlgo();
*/
void ParallelAlgo() {
  int leftSensorValue = digitalRead(LEFT_SENSOR_PIN);
  int rightSensorValue = digitalRead(RIGHT_SENSOR_PIN);

  if (leftSensorValue == LOW && rightSensorValue == LOW) {
    Forward(255);
  } else if (leftSensorValue == HIGH && rightSensorValue == LOW) {
    Right(255);
  } else if (leftSensorValue == LOW && rightSensorValue == HIGH) {
    Left(255);
  }
}

/*
   Function Name: ForwardTN
   Input: None
   Output: None
   Logic: Combines MiddleAlgo, ParallelAlgo and NodeAlgo so that robot follows the path till it reaches a node

  forward until a node is reached
   Example Call: ForwardTN();
*/
void ForwardTN() {
  while (1) {
    int leftSensorValue = digitalRead(LEFT_SENSOR_PIN);
    int rightSensorValue = digitalRead(RIGHT_SENSOR_PIN);
    int ML = digitalRead(midleft);
    int MM = digitalRead(Middle);
    int MRR = digitalRead(midright);
    if (ML == LOW && MM == LOW && MRR == LOW) {
      ParallelAlgo();
    } else {
      MiddleAlgo();
    }
    if (NodeAlgo() == 1) {
      Stop();
      break;
    }
  }
  Forward(200);
  delay(600);
  Stop();
}

/*
   Function Name: DualPath
   Input: None
   Output: None
   Logic: Similar to ForwardTN function with a little difference to be used inside other specific function
   Example Call: DualPath();
*/
void DualPath() {
  int ML = digitalRead(midleft);
  int MM = digitalRead(Middle);
  int MRR = digitalRead(midright);
  if (ML == LOW && MM == LOW && MRR == LOW) {
    int leftSensorValue = digitalRead(LEFT_SENSOR_PIN);
    int rightSensorValue = digitalRead(RIGHT_SENSOR_PIN);

    if (leftSensorValue == LOW && rightSensorValue == LOW) {
      Forward(255);
    } else if (leftSensorValue == HIGH && rightSensorValue == LOW) {
      Right(255);
      delay(20);
    } else if (leftSensorValue == LOW && rightSensorValue == HIGH) {
      Left(255);
    };
  } else {
    MiddleAlgo();
  }
  if (NodeAlgo() == 1) {
    Stop();
  }
}

/*
   Function Name: Right90
   Input: None
   Output: None
   Logic: Turns the robot right by 90 degrees
   Example Call: Right90();
*/
void Right90() {
  Right(255);
  delay(640);
  Stop();
}

/*
   Function Name: Left90
   Input: None
   Output: None
   Logic: Turns the robot left by 90 degrees
   Example Call: Left90();
*/
void Left90() {
  Left(255);
  delay(640);
  Stop();
}

/*
   Function Name: SlightForward
   Input: None
   Output: None
   Logic: Moves the robot slightly forward
   Example Call: SlightForward();
*/
void SlightForward() {
  Forward(200);
  delay(600);
  Stop();
}

/*
   Function Name: FRAD
   Input: None
   Output: None
   Logic: Moves the robot from Left node of event A/D to the Right node while stopping in front of event for nodebuzz
   Example Call: FRAD();
*/
void FRAD() {
  while (1) {
    int ML = digitalRead(midleft);
    int MM = digitalRead(Middle);
    int MRR = digitalRead(midright);
    MiddleAlgo();
    if (MM == LOW && ML == LOW && MRR == LOW) {
      Stop();
      break;
    }
  }
  Forward(255);
  delay(1200);
  Stop();
  nodebuzz();
  ForwardTN();
}

/*
   Function Name: FLAD
   Input: None
   Output: None
   Logic: Moves the robot from Right node of event A/D to the Left node while stopping in front of event for nodebuzz
   Example Call: FLAD();
*/
void FLAD() {
  while (1) {
    int ML = digitalRead(midleft);
    int MM = digitalRead(Middle);
    int MRR = digitalRead(midright);
    MiddleAlgo();
    if (MM == LOW && ML == LOW && MRR == LOW) {
      Stop();
      break;
    }
  }

  int start = millis();
  while ((millis() - start) <= 3000) {
    ParallelAlgo();
  }
  Stop();
  nodebuzz();
  ForwardTN();
}

/*
   Function Name: FRB
   Input: None
   Output: None
   Logic: Moves the robot from Left node of event B to the Right node while stopping in front of event for nodebuzz
   Example Call: FRB();
*/
void FRB() {
  while (1) {
    int ML = digitalRead(midleft);
    int MM = digitalRead(Middle);
    int MRR = digitalRead(midright);
    MiddleAlgo();
    if (MM == LOW && ML == LOW && MRR == LOW) {
      Stop();
      break;
    }
  }

  int start = millis();
  while ((millis() - start) <= 2350) {
    ParallelAlgo();
  }
  Stop();
  nodebuzz();
  ForwardTN();
}

/*
   Function Name: FLB
   Input: None
   Output: None
   Logic: Moves the robot from Right node of event B to the Left node while stopping in front of event for nodebuzz
   Example Call: FLB();
*/
void FLB() {
  while (1) {
    int ML = digitalRead(midleft);
    int MM = digitalRead(Middle);
    int MRR = digitalRead(midright);
    MiddleAlgo();
    if (MM == LOW && ML == LOW && MRR == LOW) {
      Stop();
      break;
    }
  }

  int start = millis();
  while ((millis() - start) <= 2250) {
    ParallelAlgo();
  }
  Stop();
  nodebuzz();
  ForwardTN();
}

/*
   Function Name: FRC
   Input: None
   Output: None
   Logic: Moves the robot from Left node of event C to the Right node while stopping in front of event for nodebuzz
   Example Call: FRC();
*/
void FRC() {
  while (1) {
    int ML = digitalRead(midleft);
    int MM = digitalRead(Middle);
    int MRR = digitalRead(midright);
    MiddleAlgo();
    if (MM == LOW && ML == LOW && MRR == LOW) {
      Stop();
      break;
    }
  }

  int start = millis();
  while ((millis() - start) <= 2700) {
    ParallelAlgo();
  }
  Stop();
  nodebuzz();
  ForwardTN();
}

/*
   Function Name: FLC
   Input: None
   Output: None
   Logic: Moves the robot from Right node of event C to the Left node while stopping in front of event for nodebuzz
   Example Call: FLC();
*/
void FLC() {
  while (1) {
    int ML = digitalRead(midleft);
    int MM = digitalRead(Middle);
    int MRR = digitalRead(midright);
    MiddleAlgo();
    if (MM == LOW && ML == LOW && MRR == LOW) {
      Stop();
      break;
    }
  }

  int start = millis();
  while ((millis() - start) <= 2250) {
    ParallelAlgo();
  }
  Stop();
  nodebuzz();
  ForwardTN();
}

/*
   Function Name: ParallelAlgo2
   Input: None
   Output: None
   Logic: Implements a modified algorithm for parallel path to be used in function FRE
   Example Call: ParallelAlgo2();
*/
void ParallelAlgo2() {
  int leftSensorValue = digitalRead(LEFT_SENSOR_PIN);
  int rightSensorValue = digitalRead(RIGHT_SENSOR_PIN);

  if (leftSensorValue == LOW && rightSensorValue == LOW) {
    Forward(255);


  } else if (leftSensorValue == HIGH && rightSensorValue == LOW) {
    Right(255);
    delay(150);
  } else if (leftSensorValue == LOW && rightSensorValue == HIGH) {
    Left(255);
  }
}

/*
   Function Name: FRE
   Input: None
   Output: None
   Logic: Moves the robot from Left node of event E to the Right node while stopping in front of event for nodebuzz
   Example Call: FRE();
*/
void FRE() {
  int ML = digitalRead(midleft);
  int MM = digitalRead(Middle);
  int MRR = digitalRead(midright);
  int Start = millis();
  while ((millis() - Start) <= 300) {
    MiddleAlgo();
  }
  int t2 = millis();
  while ((millis() - t2) <= 3800) {
    int leftSensorValue = digitalRead(LEFT_SENSOR_PIN);
    int rightSensorValue = digitalRead(RIGHT_SENSOR_PIN);

    if (leftSensorValue == LOW && rightSensorValue == LOW) {
      Forward(150);
    } else if (leftSensorValue == HIGH && rightSensorValue == LOW) {
      Right(255);
    } else if (leftSensorValue == LOW && rightSensorValue == HIGH) {
      Left(255);
    }
  }
  Stop();
  nodebuzz();
  while (1) {
    int leftSensorValue = digitalRead(LEFT_SENSOR_PIN);
    int rightSensorValue = digitalRead(RIGHT_SENSOR_PIN);
    int ML = digitalRead(midleft);
    int MM = digitalRead(Middle);
    int MRR = digitalRead(midright);
    if (ML == LOW && MM == LOW && MRR == LOW) {
      ParallelAlgo2();
    } else {
      MiddleAlgo();
    }
    if (NodeAlgo() == 1) {
      Stop();
      break;
    }
  }
  Forward(200);
  delay(600);
  Stop();
}

/*
   Function Name: FLE
   Input: None
   Output: None
   Logic: Moves the robot from Right node of event E to the Left node while stopping in front of event for nodebuzz
   Example Call: FLE();
*/
void FLE() {
  int ML = digitalRead(midleft);
  int MM = digitalRead(Middle);
  int MRR = digitalRead(midright);
  int Start = millis();
  while (millis() - Start <= 4000) {
    DualPath();
  }
  Stop();
  nodebuzz();
  ForwardTN();
}

/*
   Function Name: first_node
   Input: None
   Output: None
   Logic: Moves the Bot from starting position to the first node at (0,0) and having a Top facing orientation
   Example Call: first_node();
*/
void first_node() {
  Stop();
  delay(1000);
  while (1) {
    int ML = digitalRead(midleft);
    int MM = digitalRead(Middle);
    int MRR = digitalRead(midright);
    MiddleAlgo();

    if (NodeAlgo() == 1) {
      Stop();
      break;
    }
  }
  Forward(200);
  delay(450);
  Stop();
  Left(255);
  delay(160);
}

/*
   Array of function pointers
*/
void (*functionList[])() = {FLE, FRE, FRB, FLB, FRC, FLC, FRAD, FLAD, Left90, Right90, ForwardTN};

/*
   Array of corresponding function names
*/
const char *functionNames[] = { "FLE", "FRE", "FRB", "FLB", "FRC", "FLC", "FRAD", "FLAD", "Left90", "Right90", "ForwardTN"};

/*
   Function Name: callFunctionByName
   Input: const char *name - The name of the function to be called
   Output: None
   Logic: Calls a function by name
   Example Call: callFunctionByName("FRE");
*/
void callFunctionByName(const char *name) {
  for (int i = 0; i < 11; ++i) {
    if (strcmp(name, functionNames[i]) == 0) {
      // Call the function using the function pointer
      functionList[i]();
      return;
    }
  }

  // Handle the case when the function name is not found
  Serial.println("Function not found");
}

/*
   Function Name: setup
   Input: None
   Output: None
   Logic: Setup the esp32 i/o pins and connects to wifi
   Example Call: setup();
*/
void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");

  ledcSetup(0, 5000, 8);
  ledcAttachPin(LEFT_MOTOR_ENA, 17);
  ledcSetup(1, 5000, 8);
  ledcAttachPin(RIGHT_MOTOR_ENB, 5);
  pinMode(LEFT_SENSOR_PIN, INPUT);
  pinMode(RIGHT_SENSOR_PIN, INPUT);

  pinMode(Middle, INPUT);
  pinMode(midleft, INPUT);
  pinMode(midright, INPUT);

  pinMode(LEFT_MOTOR_ENA, OUTPUT);
  pinMode(RIGHT_MOTOR_ENB, OUTPUT);
  pinMode(LEFT_MOTOR_IN1, OUTPUT);
  pinMode(LEFT_MOTOR_IN2, OUTPUT);
  pinMode(RIGHT_MOTOR_IN3, OUTPUT);
  pinMode(RIGHT_MOTOR_IN4, OUTPUT);
  pinMode(led, OUTPUT);
  pinMode(buzzer, OUTPUT);
  digitalWrite(buzzer, HIGH);
}

/*
   Function Name: loop
   Input: None
   Output: None
   Logic: Main program loop
   Example Call: loop();
*/
void loop() {
  Stop();
  delay(1000);
  //connects to laptop and sends a hello message
  WiFiClient client;
  if (client.connect(server_ip, server_port)) {
    Serial.println("Connected to server");
    client.print("Hello from ESP32!\r\n");
    client.flush();

    //Receives the string message sent by the python path planning script
    String received_message = client.readStringUntil('\n');
    String a = received_message;
    Serial.print("Received message from server: ");
    Serial.println(received_message);

    String command_list[50]; //command_list : Array that contains the specific command/directions to follow in order for the bot to complete the path.
    int index = 0;
    String item = "";
    bool inQuote = false;
    int count = 0;
    //Parsing the long string of commands send by python script and storing each instruction in command_list array. For example ['ForwardTN','Stop','Right90',...]
    for (int i = 0; i < a.length(); i++) {
      char c = a.charAt(i);

      switch (c) {
        case '\'':
          inQuote = !inQuote;
          if (!inQuote) {
            command_list[index] = item;
            index++;
            item = "";
            count++;
          }
          break;
        case ',':
        case ' ':
          break;
        default:
          if (inQuote) {
            item += c;
          }
          break;
      }
    }

    // Starting the run and placing the bot at first node facing top
    first_node();

    //Calling the path commands stored in command_list array in order
    for (int i = 0; i < count; i++) {
      callFunctionByName(command_list[i].c_str());
    }

    //Moves the bot from node (0,0) to Stop Position
    while (1) {
      int ML = digitalRead(midleft);
      int MM = digitalRead(Middle);
      int MRR = digitalRead(midright);
      if (ML == LOW && MM == LOW && MRR == LOW) {
        break;
      }
      else {
        MiddleAlgo();
      }
    }

    Stop();
    delay(1000);

    //nodebuzz to indicate the stop of run
    nodebuzz_long();

    // Closing the wifi connection
    client.stop();
    Serial.println("Connection closed");
  } else {
    Serial.println("Connection to server failed");
  }
}
