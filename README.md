# Gesture-Based-Metro-Ticket-Booking-System

This project implements a contactless ticket booking system for the Hyderabad Metro using hand gestures and Google's Gemini AI model. It allows users to select their start and end stations, calculate the fare, and confirm payment through gesture-based interaction.

## Features
- **Contactless Interaction:** Uses hand gestures for navigation and selection, minimizing physical contact.
- **AI-Powered Fare Calculation:** Leverages Google's Gemini AI model to calculate approximate fares between stations.
- **Station Information:** Provides user-friendly information about metro stations, including nearby attractions and connecting lines, using Gemini AI.
- **Place Suggestions:** Suggests interesting places to visit near a selected metro station, powered by Gemini AI.
- **Streamlit UI:** Presents a user-friendly web interface for interaction.
- **Real-time Gesture Recognition:** Uses MediaPipe for robust hand tracking and gesture detection.
- **State Management:** Maintains application state for a seamless user experience.

## Prerequisites
- Python 3.7+
- A Google Cloud project with the Gemini API enabled and an API key.
- A webcam connected to your computer.

## Installation
Clone the repository:
```bash
git clone <your_repository_url>
cd <your_repository_directory>
```
Install the dependencies:
```bash
python -m pip install -r requirements.txt
```
Set up the Gemini API key:

Create a Streamlit secrets file (`.streamlit/secrets.toml`) and add your Gemini API key:
```toml
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
```
**Important:** Do not commit your secrets file to your repository!

Alternatively, you can set the `GEMINI_API_KEY` as an environment variable.

## Usage
Run the Streamlit application:
```bash
streamlit run OpenCVPaint.py  # Or the name of your main script
```
Access the application: Open your web browser and navigate to the URL provided by Streamlit (usually http://localhost:8501).

### Interact with the application:
- Use hand gestures to interact with the buttons and make selections.
- Form a click gesture (pinch your index finger and thumb together) to select a button.

## Application Flow
1. The application starts in the `IDLE` state.
2. Click the **"Book Ticket"** button to start the process.
3. The application transitions to the `SELECTING_START` state, displaying a list of metro stations.
4. Select a starting station using a click gesture.
5. The application transitions to the `SELECTING_END` state, displaying the list of metro stations again.
6. Select a destination station.
7. The application calculates the fare using the Gemini AI model and transitions to the `SHOW_FARE` state.
8. Confirm the payment by clicking the **"Confirm Payment"** button.
9. A ticket ID is generated, and the application transitions to the `PAYMENT_DONE` state.

## Code Structure
- **`OpenCVPaint.py`**: The main script containing the Streamlit application logic, gesture recognition, and AI integration.
- **`requirements.txt`**: A list of Python dependencies required to run the application.
- **`README.md`**: This file, providing an overview of the project.
- **`.streamlit/secrets.toml`** (Not in the repository): Stores sensitive information like the Gemini API key.

## Key Functions
- `detect_finger_click(hand_landmarks, width, height)`: Detects a finger click based on the distance between the fingertip and thumb tip.
- `handle_button_click(click_x, click_y, frame, current_state, frame_width, frame_height)`: Handles button clicks based on the provided click coordinates and the current application state.
- `calculate_fare(start_station, end_station)`: Calculates the approximate metro fare using the Gemini AI model.
- `get_station_info(station_name)`: Retrieves information about a metro station using the Gemini AI model.
- `suggest_places(station_name, time_of_day="day")`: Suggests places to visit near a metro station using the Gemini AI model.

## Technologies Used
- Streamlit
- OpenCV (cv2)
- MediaPipe
- Pillow (PIL)
- Google Generative AI (Gemini)
- NumPy

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request with your changes.

