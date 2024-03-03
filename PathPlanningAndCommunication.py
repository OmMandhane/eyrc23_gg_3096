'''
Team Id: GG_3096
Author List: Om Mandhane
Filename: PathPlanningAndCommunication
Theme: GG_3096
Functions: find_nearest, Bot, node_to_event, execute_commands
Global Variables: G, layout, node_to_remove, file, first_column, second_column, third_column, fourth_column, fifth_column,
                  closest_node, first_nodes, second_nodes, third_nodes, fourth_nodes, fifth_nodes, my_bot, ip

'''                  
import time
import networkx as nx
import pandas as pd
import socket

# Create a graph representing a 2D grid of the map with coordinates at nodes 
G = nx.grid_2d_graph(3, 4)  

layout = {node: (node[0], node[1]) for node in G.nodes}
node_to_remove = (2, 0)
G.remove_node(node_to_remove)

# Visualize the modified graph
nx.draw(G, pos=layout, with_labels=True, font_weight='bold')

#the events to visit in the priority order is saved in the csv "event_to_visit"
file = pd.read_csv("event_to_visit.csv")
first_event = file.columns[0]
second_event = file.columns[1]
third_event = file.columns[2]
fourth_event = file.columns[3]
fifth_event = file.columns[4]

#closest_nodes: dictionary with event as keys and the nodes closest to the event as value
closest_nodes = {"A": [(0, 0), (1, 0)],
                 "B": [(1, 1), (2, 1)],
                 "C": [(1, 2), (2, 2)],
                 "D": [(0, 2), (1, 2)],
                 "E": [(0, 3), (2, 3)]}

# contains the coordinates of the closest node to the respective event
first_nodes = closest_nodes[first_event] 
second_nodes = closest_nodes[second_event ]
third_nodes = closest_nodes[third_event]
fourth_nodes = closest_nodes[fourth_event]
fifth_nodes = closest_nodes[fifth_event]

def find_nearest(A, B):
    '''
    * Function Name: find_nearest
    * Input: A - List of two nodes that can used to got to the particular event, B - Current location/node of the bot
    * Output: The nearest node from A to the target node B
    * Logic: Calculates the Euclidean distance from both nodes in A to the target node B and returns the closest one.
    * Example Call: find_nearest([(0, 0), (1, 0)], [0, 0])
    '''
    x1, y1 = A[0]
    x2, y2 = A[1]
    x, y = B
    first = (x1 - x) ** 2 + (y1 - y) ** 2
    second = (x2 - x) ** 2 + (y2 - y) ** 2
    if first <= second:
        return A[0]
    else:
        return A[1]



class Bot:
    def __init__(self, start_position):
        '''
        * Function Name: __init__
        * Input: start_position - Tuple representing the initial position of the bot (x, y)
        * Output: None
        * Logic: Initializes the Bot object with the given start position and default orientation ('up')
        * Example Call: my_bot = Bot((0, 0))
        '''
        self.position = start_position
        self.orientation = 'up'  # Initial orientation (up, down, left, right)
        self.commands = [] #the path commands to reach all the events keep getting appended to this attribute

    def move_forward(self):
        '''
        * Function Name: move_forward
        * Input: None
        * Output: None
        * Logic: Moves the bot one step forward based on its current orientation and updates the position along with
                along appending the esp32 function name that moves the bot forward to the commands attribute.
        * Example Call: my_bot.move_forward()
        '''
        x, y = self.position
        self.commands.append("ForwardTN")
        if self.orientation == 'up':
            self.position = (x, y + 1)
        elif self.orientation == 'down':
            self.position = (x, y - 1)
        elif self.orientation == 'left':
            self.position = (x - 1, y)
        elif self.orientation == 'right':
            self.position = (x + 1, y)

    def turn_left(self):
        '''
        * Function Name: turn_left
        * Input: None
        * Output: None
        * Logic: Adds the esp32 function name that turns the bot 90 degrees to the left to the commands
                list and updates its orientation
        * Example Call: my_bot.turn_left()
        '''
        self.commands.append("Left90")
        orientations = ['up', 'left', 'down', 'right']
        current_index = orientations.index(self.orientation)
        self.orientation = orientations[(current_index + 1) % 4]

    def turn_right(self):
        '''
        * Function Name: turn_right
        * Input: None
        * Output: None
        * Logic: Adds the esp32 function name that turns the bot 90 degrees to the right to the commands
                list and updates its orientation
        * Example Call: my_bot.turn_right()
        '''
        self.commands.append("Right90")
        orientations = ['up', 'left', 'down', 'right']
        current_index = orientations.index(self.orientation)
        self.orientation = orientations[(current_index - 1) % 4]

    def forward_right_ad(self):
        '''
        * Function Name: forward_right_ad
        * Input: None
        * Output: None
        * Logic: Adds the esp32 function name that moves the bot from left of event A/D to the right
                 while stopping at A/D, to the command list. This function updates the position accordingly
        * Example Call: my_bot.forward_right_ad()
        '''
        x, y = self.position
        self.position = (x + 1, y)
        self.commands.append("FRAD")

    def forward_left_ad(self):
        '''
        * Function Name: forward_left_ad
        * Input: None
        * Output: None
        * Logic: Adds the esp32 function name that moves the bot from right of event A/D to the left
                 while stopping at A/D, to the command list. This function updates the position accordingly
        * Example Call: my_bot.forward_left_ad()
        '''
        x, y = self.position
        self.position = (x - 1, y)
        self.commands.append("FLAD")

    def forward_right_b(self):
        '''
        * Function Name: forward_right_b
        * Input: None
        * Output: None
        * Logic: Adds the esp32 function name that moves the bot from left of event B to the right
                 while stopping at B, to the command list. This function updates the position accordingly
        * Example Call: my_bot.forward_right_b()
        '''
        x, y = self.position
        self.position = (x + 1, y)
        self.commands.append("FRB")

    def forward_left_b(self):
        '''
        * Function Name: forward_left_b
        * Input: None
        * Output: None
        * Logic: Adds the esp32 function name that moves the bot from right of event B to the left
                 while stopping at B, to the command list. This function updates the position accordingly
        * Example Call: my_bot.forward_left_b()
        '''
        x, y = self.position
        self.position = (x - 1, y)
        self.commands.append("FLB")

    def forward_right_c(self):
        '''
        * Function Name: forward_right_c
        * Input: None
        * Output: None
        * Logic: Does the same as the above functions, but for event C
        * Example Call: my_bot.forward_right_c()
        '''
        x, y = self.position
        self.position = (x + 1, y)
        self.commands.append("FRC")

    def forward_left_c(self):
        '''
        * Function Name: forward_left_c
        * Input: None
        * Output: None
        * Logic: Does the same as the above functions, but for event C
        * Example Call: my_bot.forward_left_c()
        '''
        x, y = self.position
        self.position = (x - 1, y)
        self.commands.append("FLC")

    def forward_right_e(self):
        '''
        * Function Name: forward_right_e
        * Input: None
        * Output: None
        * Logic: Does the same as the above functions, but for event C
        * Example Call: my_bot.forward_right_e()
        '''
        self.position = (2, 3)
        self.orientation = 'down'
        self.commands.append("FRE")

    def forward_left_e(self):
        '''
        * Function Name: forward_left_e
        * Input: None
        * Output: None
        * Logic: Moves the bot to the target position and changes its orientation for event 'E'.
        * Example Call: my_bot.forward_left_e()
        '''
        self.position = (0, 3)
        self.orientation = 'down'
        self.commands.append("FLE")

def node_to_event(event, node, bot):
    '''
    * Function Name: node_to_event
    * Input: event - The event to be executed (A, B, C, D, E), node - Current node, bot - Bot object
    * Output: None
    * Logic: Determines which function to execute from Bot class to move the bot from current node
             to the given event and then till the next node. Adjusts the orientation of the bot till  
             it is facing in the right directiom                        
    * Example Call: node_to_event('A', (1, 0), my_bot)
    '''
    if event == 'A' and node == (0, 0):
        while bot.orientation != "right":
            bot.turn_right()
        bot.forward_right_ad()
    elif event == 'A' and node == (1, 0):
        while bot.orientation != "left":
            bot.turn_left()
        bot.forward_left_ad()
    elif event == 'B' and node == (1, 1):
        while bot.orientation != "right":
            bot.turn_right()
        bot.forward_right_b()
    elif event == 'B' and node == (2, 1):
        while bot.orientation != "left":
            bot.turn_left()
        bot.forward_left_b()
    elif event == 'C' and node == (1, 2):
        while bot.orientation != "right":
            bot.turn_right()
        bot.forward_right_c()
    elif event == 'C' and node == (2, 2):
        while bot.orientation != "left":
            bot.turn_left()
        bot.forward_left_c()
    elif event == 'D' and node == (0, 2):
        while bot.orientation != "right":
            bot.turn_right()
        bot.forward_right_ad()
    elif event == 'D' and node == (1, 2):
        while bot.orientation != "left":
            bot.turn_left()
        bot.forward_left_ad()
    elif event == 'E' and node == (0, 3):
        while bot.orientation != "up":
            bot.turn_right()
        bot.forward_right_e()
    elif event == 'E' and node == (2, 3):
        while bot.orientation != "up":
            bot.turn_left()
        bot.forward_left_e()


my_bot = Bot((0, 0)) #initialising bot object at node (0,0)


def execute_commands(path):
    '''
    * Function Name: execute_commands
    * Input: path - List of nodes representing the path the bot needs to traverse
    * Output: List of commands to be executed by the bot
    * Logic: Takes a path as input and generates the commands for the bot to traverse that path.
    * Example Call: execute_commands([(0, 0), (1, 0), (1, 1)])
    '''
    for node in path:
        if node[0] > my_bot.position[0]:
            while my_bot.orientation != 'right':
                my_bot.turn_right()
            my_bot.move_forward()
        elif node[0] < my_bot.position[0]:
            while my_bot.orientation != 'left':
                my_bot.turn_left()
            my_bot.move_forward()
        elif node[1] > my_bot.position[1]:
            while my_bot.orientation != 'up':
                my_bot.turn_left()
            my_bot.move_forward()
        elif node[1] < my_bot.position[1]:
            while my_bot.orientation != 'down':
                my_bot.turn_left()
            my_bot.move_forward()
    return my_bot.commands

#finding the nearest node to the first event
first_to_visit = find_nearest(first_nodes, [0, 0])
#using the dijkstras algorithm to find shortest path
path1 = nx.shortest_path(G, source=(0, 0), target=first_to_visit) 
#commands to be executed to reach first event nearest node
command1 = execute_commands(path1)
#function to go from the node to the event
node_to_event(first_event, path1[-1], my_bot)

#path/commands to go from first event to second is appended in the commands attribute
second_to_visit = find_nearest(second_nodes, my_bot.position)
path2 = nx.shortest_path(G, source=my_bot.position, target=second_to_visit)
command2 = execute_commands(path2)
node_to_event(second_event, path2[-1], my_bot)

#path/commands to go from second event to third is appended in the commands attribute
third_to_visit = find_nearest(third_nodes, my_bot.position)
path3 = nx.shortest_path(G, source=my_bot.position, target=third_to_visit)
command3 = execute_commands(path3)
node_to_event(third_event, path3[-1], my_bot)

#path/commands to go from third event to fourth is appended in the commands attribute
fourth_to_visit = find_nearest(fourth_nodes, my_bot.position)
path4 = nx.shortest_path(G, source=my_bot.position, target=fourth_to_visit)
command4 = execute_commands(path4)
node_to_event(fourth_event, path4[-1], my_bot)

#path/commands to go from fourth event to fifth is appended in the commands attribute
fifth_to_visit = find_nearest(fifth_nodes, my_bot.position)
path5 = nx.shortest_path(G, source=my_bot.position, target=fifth_to_visit)
command5 = execute_commands(path5)
node_to_event(fifth_event, path5[-1], my_bot)

##path to go from last event to (0,0)
path6 = nx.shortest_path(G, source=my_bot.position, target=(0, 0))
command6 = execute_commands(path6)

#turning the bot left till it is facing downward at node (0,0)
while my_bot.orientation != "down":
    my_bot.turn_left()

#converting the command list to a string
string = str(my_bot.commands)
print(string)
message = string[1:-1] #removing inverted commas from the string and storing the commands in message variable

ip = "192.168.155.229"  # IP address of the laptop after connecting it to the WIFI hotspot

#using socket library to establish connection and sending the message string to the esp32 on the bot
while True:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((ip, 8002))
            s.listen()
            conn, addr = s.accept()
            print("done")
            with conn:
                print(f"Connected by {addr}")
                data = conn.recv(1024)
                print(data)
                conn.sendall(message.encode('utf-8'))
                print("done2")
            break

    except Exception as e:
        print(f"An error occurred: {e}")

    # Wait for some time before attempting to reconnect
    time.sleep(5)
