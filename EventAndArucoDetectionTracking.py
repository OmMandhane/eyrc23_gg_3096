import numpy as np
import cv2 as cv       
from PIL import Image
from torchvision import transforms
import torch 
import csv
import numpy as np
from cv2 import aruco

'''
* Team Id: GG_3096
* Author List: Om Mandhane
* Filename: EventAndArucoDetectionTracking
* Theme: GeoGuide
* Functions: read_csv, write_csv, tracker, euclidean_distance, find_nearest_aruco, getAruco, detect_ArUco_details,
              cropframe, eventlist, classify_event, denoise_classify, textImshow
* Global Variables: cap (OpenCV VideoCapture object), display_width (int), display_height (int),
                    properorder (dictionary), lat_lon (dictionary), ArUco_details_dict (dictionary), ArUco_corners (dictionary)
'''

def read_csv():
    '''
    * Function Name: read_csv
    * Input: None
    * Output: Dictionary containing aruco id as keys and lat, lon as values
    * Logic: Reads data from a CSV file and stores it in a dictionary
    * Example Call: lat_lon = read_csv()
    '''
    csv_file_path = r"C:\Users\Gayatri\Desktop\eyantra\stage 2\5b\lat_long.csv"
    lat_lon = {}

    with open(csv_file_path, 'r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            lat_lon[row[0]] = [row[1], row[2]]
    return lat_lon 

def write_csv(loc, csv_name):
    '''
    * Function Name: write_csv
    * Input: loc - List containing [lat, lon], csv_name - Name of the CSV file
    * Output: None
    * Logic: Writes lat and lon values to a CSV file
    * Example Call: write_csv([latitude, longitude], 'output.csv')
    '''
    csv_file_path = csv_name
    with open(csv_file_path, 'w', newline='') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(['lat', 'lon'])
        csv_writer.writerow(loc)

def tracker(ar_id, lat_lon):
    '''
    * Function Name: tracker
    * Input: ar_id - ArUco id, lat_lon - Dictionary with aruco id as keys and lat, lon as values
    * Output: [lat, lon] if ar_id is found in lat_lon, None otherwise
    * Logic: Finds the lat, lon associated with ar_id and writes them to "live_data.csv"
    * Example Call: tracker(123, lat_lon_dict)
    '''
    ar_id = str(ar_id)
    if ar_id in lat_lon:
        coordinate = lat_lon[ar_id]
        write_csv(coordinate, 'live_data.csv')
        return coordinate

def euclidean_distance(point1, point2):
    '''
    * Function Name: euclidean_distance
    * Input: point1 - List [x1, y1], point2 - List [x2, y2]
    * Output: Euclidean distance between point1 and point2
    * Logic: Calculates Euclidean distance between two points in a 2D space
    * Example Call: distance = euclidean_distance([x1, y1], [x2, y2])
    '''
    return np.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)

def find_nearest_aruco(ArUco_details_dict):
    '''
    * Function Name: find_nearest_aruco
    * Input: ArUco_details_dict - Dictionary containing ArUco details
    * Output: ArUco id of the nearest ArUco marker
    * Logic: Finds the nearest ArUco marker based on Euclidean distance 
    * Example Call: nearest_id = find_nearest_aruco(ArUco_details_dict)
    '''
    targetaruco = ArUco_details_dict[100]
    Dict = ArUco_details_dict
    del Dict[100]
    allaruco = list(Dict.values())
    nearest_distance = float('inf')
    nearest_aruco = None

    for aruco in allaruco:
        distance = euclidean_distance(targetaruco[0], aruco[0])
        if distance < nearest_distance:
            nearest_distance = distance
            nearest_aruco = aruco
    result_key = next((key for key, value in ArUco_details_dict.items() if value == nearest_aruco), None)
    return result_key

def detect_ArUco_details(image):
    # Function Level Comments
    '''
    * Function Name: detect_ArUco_details
    * Input: image - Input image with ArUco markers
    * Output: ArUco_details_dict - Dictionary containing ArUco details, ArUco_corners - Dictionary containing ArUco corners
    * Logic: Detects ArUco markers in the input image and extracts their details
    * Example Call: details_dict, corners_dict = detect_ArUco_details(input_image)
    '''
    ArUco_details_dict = {}
    ArUco_corners = {}

    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    markerIds = []
    markerCorners = []
    rejectedCandidates = []
    detectorParams = aruco.DetectorParameters()
    dictionary = aruco.getPredefinedDictionary(aruco.DICT_4X4_250)
    detector = aruco.ArucoDetector(dictionary, detectorParams)
    markerCorners, markerIds, rejectedCandidates = aruco.detectMarkers(gray, dictionary, parameters=detectorParams)
    
    if markerIds is None:
        return [0], [0]
    
    for i in range(len(markerIds)):
        ArUco_corners[int(markerIds[i])] = markerCorners[i][0]

    for key, value in ArUco_corners.items():
        corner1 = value[0]
        corner2 = value[1]
        corner3 = value[2]
        corner4 = value[3]
        centre = [int((corner1[0] + corner2[0] + corner3[0] + corner4[0]) / 4), int((corner1[1] + corner2[1] + corner3[1] + corner4[1]) / 4)]
        ArUco_details_dict[key] = [centre]

    return ArUco_details_dict, ArUco_corners

def cropframe(frame, ArUco_details_dict, ArUco_corners):
    '''
    * Function Name: cropframe
    * Input: frame - Input frame, ArUco_details_dict - Dictionary containing ArUco details, ArUco_corners - Dictionary containing ArUco corners
    * Output: Cropped region of the frame
    * Logic: Crops the camera frame using the corner 4 aruco ids so that only map is visible
    * Example Call: cropped_frame = cropframe(input_frame, details_dict, corners_dict)
    '''
    topleft = ArUco_corners[5][0]
    topright = ArUco_corners[4][1]
    bottomright = ArUco_corners[6][2]
    bottomleft = ArUco_corners[7][3]

    tl_x, tl_y = topleft
    tr_x, tr_y = topright 
    br_x, br_y = bottomright
    bl_x, bl_y = bottomleft

    width = int(tr_x - tl_x)
    height = int(br_y - tr_y)

    cropped_region = frame[int(tl_y):int(tl_y) + height, int(tl_x):int(tl_x) + width]
    return cropped_region

def eventlist(frame):
    '''
    * Function Name: eventlist
    * Input: frame - Input frame
    * Output: event_list - List of detected events[Square boxes on the map], square_corners - List of corners for detected squares
    * Logic: Detects squares in the input frame based on contours and extracts event regions
    * Example Call: events, corners = eventlist(input_frame)
    '''
    arena = frame.copy()
    imagecopy = arena.copy()

    gray = cv.cvtColor(imagecopy, cv.COLOR_BGR2GRAY)
    blurred = cv.GaussianBlur(gray, (5, 5), 0)
    
    min_square_area = 6600
    max_square_area = 12000
    square_corners = []
    event_list = []
    threshold_range = range(165, 220, 5)
    
    for threshold_value in threshold_range:
        square_corners.clear()
        event_list.clear()

        _, thresh = cv.threshold(blurred, threshold_value, 255, cv.THRESH_BINARY)
        contours, _ = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            epsilon = 0.04 * cv.arcLength(contour, True)
            approx = cv.approxPolyDP(contour, epsilon, True)

            if len(approx) == 4:
                area = cv.contourArea(approx)

                if min_square_area <= area <= max_square_area:
                    square_corners.append(approx)
                    cv.drawContours(imagecopy, [approx], 0, (0, 255, 0), 2)

                    pts = approx.reshape(-1, 2)
                    x, y, w, h = cv.boundingRect(approx)
                    square = arena[y:y + h, x:x + w]
                    square = cv.cvtColor(square, cv.COLOR_BGR2RGB)
                    event_list.append(square)

        if len(event_list) == 5:
            break

    return event_list, square_corners


def classify_event(image):
    '''
    * Function Name: classify_event
    * Input: image - Event image
    * Output: Event type and confidence level
    * Logic: Classifies the event type based on the trained ml model
    * Example Call: event_type, confidence = classify_event(event_image)
    '''
    test_transform = transforms.Compose([
        transforms.Resize(224),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    
    #loading the trained ml model
    modell = torch.load(r'C:\Users\Gayatri\Desktop\eyantra\Task_2B\AlexCustomedTrain4.pth')
    modell.eval()

    event_image = Image.fromarray(image, 'RGB')

    transformed_image = test_transform(event_image)
    tensor_image = transformed_image.unsqueeze(0)
    class_names = ['combat', 'destroyed_buildings', 'fire', 'human_aid_rehabilitation', 'military_vehicles']

    with torch.no_grad():
        output = modell(tensor_image.view(1, 3, 224, 224))
        _, predicted_class = output.max(1)
        confidence = torch.nn.functional.softmax(output, dim=1)[0][predicted_class.item()].item()

    event = class_names[predicted_class.item()]
    return event, confidence

def classify_and_map(event_list):
    '''
    * Function Name: denoise_classify
    * Input: event_list - List of detected events
    * Output: Dictionary mapping event names to the event alphabet
    * Logic: Classifies events and  maps the letter to the classified event in a dictionary, also removes events with low confidence 
    * Example Call: identified_dict = denoise_classify(events)
    '''
    class_names = ['combat', 'destroyed_buildings', 'fire', 'human_aid_rehabilitation', 'military_vehicles']
    keylist = ["A", "B", "C", "D", "E"]
    numlist1 = [0, 1, 3, 2, 4]
    numlist2 = [0, 1, 2, 3, 4]
    identified_dict = {}

    for index1, index2 in zip(numlist1, numlist2):
        event, confidence = classify_event(event_list[index1])
        #Assigns 0 to event key if the confidence of that event is lower than 0.80
        if confidence > 0.80:
            identified_dict[keylist[index2]] = event
        else:
            identified_dict[keylist[index2]] = 0

    return identified_dict


if __name__ == "__main__":
    cap = cv.VideoCapture(0)
    cap.set(cv.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, 1080)
    
    #only take a frame when 50 arucos are detected
    points = 0
    while points != 50:
        ret, frame = cap.read()
        ArUco_details_dict, ArUco_corners = detect_ArUco_details(frame)
        points = len(ArUco_corners)

    display_width = 430
    display_height = 430

    frame = cropframe(frame, ArUco_details_dict, ArUco_corners)
    event_list, square_corners = eventlist(frame)

    event_dictionary = classify_and_map(event_list)
    newlist = []
    listtt = list(event_dictionary.keys())

    for i in listtt:
        if event_dictionary[i] != 0:
            newlist.append([i, event_dictionary[i]])

    properorder = {"fire": 5, "destroyed_buildings": 4, "human_aid_rehabilitation": 3, "military_vehicles": 2, "combat": 1}
    #Sorting events according to proper priority order
    newlist.sort(key=lambda x: properorder[x[1]], reverse=True)
    value = [item[0] for item in newlist]
    
    #writes the proper order to a csv so that the path planning code can read it
    with open('event_to_visit.csv', 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(value)
        print(value)

    keylist = ["A", "B", "D", "C", "E"]
    print(event_dictionary)

    lat_lon = read_csv()
    count = 0

    while True:
        ret, frame = cap.read()
        frame = cropframe(frame, ArUco_details_dict, ArUco_corners)

        #Updates the lat_lon of the nearest aruco from the bot every 15 frames
        count += 1
        if count == 15:
            NewArUco_details_dict, _ = detect_ArUco_details(frame)
            #To avoid error, only updates if aruco-id of bot(100) is in the list 
            if 100 in NewArUco_details_dict:
                id = find_nearest_aruco(ArUco_details_dict=NewArUco_details_dict)
                t_point = tracker(id, lat_lon)
            count = 0
        
        #Draws bounding boxes and event labels and display the frames
        for i in range(5):
            approx = square_corners[i]
            cv.drawContours(frame, [approx], 0, (0, 255, 0), 2)

            pts = approx.reshape(-1, 2)
            x, y, w, h = cv.boundingRect(approx)

            text = str(event_dictionary[keylist[i]])
            font = cv.FONT_HERSHEY_SIMPLEX
            font_scale = 1 
            font_thickness = 4  
            text_position = (x, y - 5)  
            cv.putText(frame, text, text_position, font, font_scale, (0, 255, 0), font_thickness)
            resized_frame = cv.resize(frame, (display_width, display_height))
        cv.imshow("Frame", resized_frame)

        key = cv.waitKey(1) & 0xFF
        if key == 27:  # Press 'Esc' key to exit
            break

    cap.release()
    cv.destroyAllWindows()




