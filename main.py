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
        "Ameerpet": "data:image/jpeg;base64,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",
        "Hitech City": "https://c8.alamy.com/comp/ANXTJ0/india-andhra-pradesh-hyderabad-hitec-city-major-center-of-indian-software-ANXTJ0.jpg",
        "Jubilee Hills": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/Kbrpark.jpg/220px-Kbrpark.jpg",
        "Raidurg": "https://upload.wikimedia.org/wikipedia/commons/a/ae/Raidurg%2C_Hyderabad%2C_Telangana_State.jpg",
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
        cv2.putText(frame, f'Click Here to Confirm', (220, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        cv2.putText(frame, f'Start: {selected_start_station}', (220, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    if selected_dest_station:
        cv2.putText(frame, f'Dest: {selected_dest_station}', (220, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
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
                                        st.success(f'Ticket from {selected_start_station} to {selected_dest_station}')
                                        st.write(f"Fare: ₹{fare}")
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
