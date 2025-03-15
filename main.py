import cv2
import mediapipe as mp
import math
import time
import streamlit as st
import requests  # New import for API requests
import google.generativeai as genai  # New import for Gemini API
from PIL import Image, ImageDraw, ImageFont

# Initialize MediaPipe Hands module
mp_hands = mp.solutions.hands
max_num_hands = 1
min_detection_confidence = 0.5
min_tracking_confidence = 0.5
hands = mp_hands.Hands(
    max_num_hands=max_num_hands,
    min_detection_confidence=min_detection_confidence,
    min_tracking_confidence=min_tracking_confidence
)

# Define drawing specifications for landmarks and connections
drawLandmark = mp.solutions.drawing_utils
landmark_spec = drawLandmark.DrawingSpec(color=(255, 0, 0), thickness=2, circle_radius=3)
connection_spec = drawLandmark.DrawingSpec(color=(180, 180, 180), thickness=2)

# Define metro station constants
stations = {
    "Miyapur": (255, 255, 255),
    "Ameerpet": (0, 165, 255),
    "Hitech City": (0, 0, 255),
    "Jubilee Hills": (255, 255, 0),
    "Raidurg": (0, 255, 0),
    "Nagole": (255, 0, 0),
    "LB Nagar": (255, 0, 255),
    "MGBS": (0, 255, 255),
}

# Initialize variables for metro booking
last_click_time = time.time()
selected_start_station = None
selected_dest_station = None
msg = 'Welcome To Hyderabad Metro Ticket Booking'
confirm_selection = False  # New variable to track confirmation
info_displayed = False  # New flag to track if information has been displayed
destination_image = None # stores destination image

def set_cooldown_period():
    return 0.8

border_color = (138, 11, 246)

# Placeholder function for getting destination image URL
def get_destination_image_url(station_name):
    # You should replace this with a real API call or a dictionary lookup
    # based on the station name
    image_urls = {
        "Miyapur": "https://www.99acres.com/microsite/articles/files/2024/07/invest-in-Miyapur-Hyderabad.jpg",
        "Ameerpet": "https://c8.alamy.com/comp/K12BDE/aditya-enclave-ameerpet-hyderabad-K12BDE.jpg",
        "Hitech City": "https://c8.alamy.com/comp/ANXTJ0/india-andhra-pradesh-hyderabad-hitec-city-major-center-of-indian-software-ANXTJ0.jpg",
        "Jubilee Hills": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/Kbrpark.jpg/220px-Kbrpark.jpg",
        "Raidurg": "https://www.shutterstock.com/shutterstock/videos/1110580143/thumb/1.jpg?ip=x480",
        "Nagole": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcScszE4ffxphMI33kZ6UdZ34BF04yBRtefvPQ&s",
        "LB Nagar": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRs-Bk7tMCOELeRFDszaWv2CSiwkZPqWAMgRA&s",
        "MGBS": "https://upload.wikimedia.org/wikipedia/commons/f/f3/Mgbs_hyderabad.jpg"
    }
    return image_urls.get(station_name, None) # None if not found

def stationBar(frame):
    y = 10
    for station, color in stations.items():
        cv2.rectangle(frame, (10, y), (200, y + 70), color, -1)
        cv2.putText(frame, station, (20, y + 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        y += 80
    cv2.rectangle(frame, (210, 10), (500, 100), border_color, -1)
    if selected_start_station:
        cv2.putText(frame, f'Start: {selected_start_station}', (220, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    if selected_dest_station:
        cv2.putText(frame, f'Dest: {selected_dest_station}', (220, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        cv2.putText(frame, f'Click Here to Confirm', (220, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    # Draw reset button
    cv2.rectangle(frame, (w - 150, h - 50), (w - 10, h - 10), (0, 0, 255), -1)
    cv2.putText(frame, 'Reset', (w - 140, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

# Function to calculate distance between two points
def disx(pt1, pt2):
    x1, y1 = pt1
    x2, y2 = pt2
    return round(math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2), 3)

# Function to calculate fare between two stations (Placeholder)
def calculate_fare(start, dest):
    # Placeholder fare calculation logic
    # Replace with actual fare calculation based on stations
    # Here's a simple example (replace with a real fare matrix)
    if start and dest:
        station_list = list(stations.keys())
        start_index = station_list.index(start)
        dest_index = station_list.index(dest)
        distance = abs(dest_index - start_index)
        fare = 10 + distance * 5  # Base fare + per station cost
        return fare
    return 50  # Example fare

# Function to get suggestions from Gemini API
def get_gemini_suggestions(start, dest):
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key) #Configure the API KEY
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"Provide user-friendly information about {dest} metro station in Hyderabad in natural language. Include a short description, a list of 2-3 nearby attractions with their distances, and a list of connecting metro lines. Format the information for easy reading, not as code or JSON. Be concise."
    response = model.generate_content(prompt)
    station_info_text = response.text.strip()
    return station_info_text

def reset_selections():
    global selected_start_station, selected_dest_station, msg, confirm_selection, info_displayed, destination_image
    selected_start_station = None
    selected_dest_station = None
    msg = 'Welcome To Hyderabad Metro Ticket Booking'
    confirm_selection = False
    info_displayed = False
    destination_image = None

# Streamlit UI
st.title("Hyderabad Metro Ticket Booking")

# Load the sky background image
sky_image_path = r'C:\Users\91944\Downloads\sky.jpeg'  # Replace with the actual path to the sky image
sky_image = Image.open(sky_image_path)

# Convert the image to base64
import base64
from io import BytesIO

buffered = BytesIO()
sky_image.save(buffered, format="JPEG")
img_str = base64.b64encode(buffered.getvalue()).decode()

# Set the background image using Streamlit's HTML component
st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpeg;base64,{img_str}");
        background-size: cover;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

col1, col2 = st.columns([0.7, 0.3])  # Adjust the ratio as needed

with col1:
    frame_placeholder = st.empty()  # Placeholder for video frame
    cap = cv2.VideoCapture(0)

with col2:
    info_placeholder = st.empty()  # Placeholder for information

# Display image if destination is selected
if selected_dest_station:
    image_url = get_destination_image_url(selected_dest_station)
    if image_url:
        try:
            response = requests.get(image_url, stream=True)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            image = Image.open(response.raw)
            st.image(image, caption=f"{selected_dest_station} Metro Station", use_container_width=True)
            destination_image = image  # Store image object
        except Exception as e:
            st.error(f"Error loading image: {e}")
    else:
        st.warning("No image available for the selected destination.")

while cap.isOpened():
    stat, frame = cap.read()
    frame = cv2.flip(frame, 1)
    if not stat:
        print("Error: Couldn't read frame.")
        break
    height, width, _ = frame.shape
    h = int(height * 1.4)
    w = int(width * 1.4)
    frame = cv2.resize(frame, (w, h))
    rgb = image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    cv2.putText(frame, str(msg), (200, min(130, h - 30)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 4)
    stationBar(frame)

    # Process hand landmarks
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            points = []
            drawLandmark.draw_landmarks(frame, hand_landmarks,
                                        mp_hands.HAND_CONNECTIONS,
                                        landmark_drawing_spec=landmark_spec,
                                        connection_drawing_spec=connection_spec
                                        )
            for idx, landmark in enumerate(hand_landmarks.landmark):
                if idx == 8:
                    cx8, cy8 = int(landmark.x * w), int(landmark.y * h)
                    cv2.circle(frame, (cx8, cy8), 6, (255, 0, 0), -1)
                    points.append((cx8, cy8))
                if idx == 4:
                    cx4, cy4 = int(landmark.x * w), int(landmark.y * h)
                    cv2.circle(frame, (cx4, cy4), 6, (255, 0, 0), -1)
                    points.append((cx4, cy4))

                if len(points) == 2:
                    cv2.line(frame, points[0], points[1], (0, 255, 0), 2)
                    midpoint = ((points[0][0] + points[1][0]) // 2, (points[0][1] + points[1][1]) // 2)
                    cv2.circle(frame, midpoint, 6, (0, 0, 180), -1)
                    dis = disx(points[0], midpoint)
                    if dis < 25:
                        current_time = time.time()
                        cooldown_period = set_cooldown_period()
                        if current_time - last_click_time > cooldown_period:
                            last_click_time = time.time()
                            x = midpoint[0]
                            y = midpoint[1]
                            if 10 < x < 200:
                                y_cursor = 10
                                for station, color in stations.items():
                                    if y_cursor < y < (y_cursor + 70):
                                        if not selected_start_station:
                                            selected_start_station = station
                                            msg = f'Starting station [{station}] selected'
                                        elif station != selected_start_station:
                                            selected_dest_station = station
                                            msg = f'Destination station [{station}] selected'

                                            # Load and display destination image upon selection
                                            image_url = get_destination_image_url(selected_dest_station)
                                            if image_url:
                                                try:
                                                    response = requests.get(image_url, stream=True)
                                                    response.raise_for_status()  # Check for HTTP errors
                                                    image = Image.open(response.raw)
                                                    destination_image = image
                                                    with col2:
                                                        st.image(image, caption=f"{selected_dest_station} Metro Station", use_container_width=True)
                                                except Exception as e:
                                                    st.error(f"Error loading image: {e}")
                                            else:
                                                st.warning("No image available for the selected destination.")
                                        else:
                                            msg = 'Starting and destination stations cannot be the same'
                                        break
                                    y_cursor += 80  # Increment cursor for next button

                            elif w - 150 < x < w - 10 and h - 50 < y < h - 10:
                                reset_selections()
                                msg = 'Selections have been reset'

                            elif 210 < x < 400 and 10 < y < 80:
                                if selected_start_station and selected_dest_station and selected_start_station != "None" and selected_dest_station != "None":
                                    fare = calculate_fare(selected_start_station, selected_dest_station)
                                    # Display results and information in right column
                                    with col2:
                                        st.markdown(f"<p style='color:black;'>Ticket from {selected_start_station} to {selected_dest_station}</p>", unsafe_allow_html=True)
                                        st.markdown(f"<p style='color:black;'>Fare: ₹{fare}</p>", unsafe_allow_html=True)
                                        try:
                                            suggestions = get_gemini_suggestions(selected_start_station, selected_dest_station)
                                            st.write("Information about Destination Station:")
                                            st.write(suggestions)
                                        except Exception as e:
                                            st.error(f"Error getting suggestions from Gemini: {e}")
                                    cap.release()
                                    cv2.destroyAllWindows()
                                    st.stop()  # Stop Streamlit execution

    frame_placeholder.image(frame, channels="BGR")

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
