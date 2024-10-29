from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import mediapipe as mp
import math
import numpy as np

app = Flask(__name__)
CORS(app)




# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

# Initialize drawing utility for visualizing pose landmarks
mp_drawing = mp.solutions.drawing_utils

rep_count = {
    'Push-ups': 0,
    'Squats': 0,
    'Pull-ups': 0,
    'Deadlifts': 0
}
down = False
workout_type = None
workout_started = False
calories_burned = {
    'Push-ups': 0,
    'Squats': 0,
    'Pull-ups': 0,
    'Deadlifts': 0
}

WHITE = (255, 255, 255)
BLUE = (245, 117, 25)

CALORIES_PER_REP = {
    'Push-ups': 0.29,
    'Squats': 0.32,
    'Pull-ups': 0.35,
    'Deadlifts': 0.4
}

# Function to calculate the angle between three points
def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    radians = math.atan2(c[1] - b[1], c[0] - b[0]) - math.atan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / math.pi)
    if angle > 180.0:
        angle = 360 - angle
    return angle

# Function to classify workout type based on body landmark positions
def classify_workout(landmarks):
    global workout_type, workout_started
    left_shoulder = landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER]
    right_shoulder = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER]
    left_hip = landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP]
    right_hip = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP]
    left_knee = landmarks.landmark[mp_pose.PoseLandmark.LEFT_KNEE]
    right_knee = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_KNEE]
    left_ankle = landmarks.landmark[mp_pose.PoseLandmark.LEFT_ANKLE]

    shoulder_avg_y = (left_shoulder.y + right_shoulder.y) / 2
    hip_avg_y = (left_hip.y + right_hip.y) / 2
    knee_avg_y = (left_knee.y + right_knee.y) / 2

    knee_angle = calculate_angle(
        [left_hip.x, left_hip.y],
        [left_knee.x, left_knee.y],
        [left_ankle.x, left_ankle.y]
    )

    if shoulder_avg_y < knee_avg_y and abs(shoulder_avg_y - hip_avg_y) < 0.1:
        workout_type = 'Push-ups'
        workout_started = True
    elif hip_avg_y > shoulder_avg_y and hip_avg_y > knee_avg_y and knee_angle < 120:
        workout_type = 'Squats'
        workout_started = True
    elif shoulder_avg_y < hip_avg_y and shoulder_avg_y < knee_avg_y:
        workout_type = 'Pull-ups'
        workout_started = True
    elif left_knee.y > left_hip.y and abs(left_knee.y - left_hip.y) < 0.15 and left_ankle.y > left_knee.y:
        workout_type = 'Deadlifts'
        workout_started = True
    else:
        if workout_started:
            workout_type = None

# Function to count reps based on the workout type and calculating calories burned
def count_reps(landmarks,workout_type):
    global rep_count, down, calories_burned

    if workout_type == 'Push-ups':
        left_wrist = landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST]
        left_elbow = landmarks.landmark[mp_pose.PoseLandmark.LEFT_ELBOW]
        left_shoulder = landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER]

        wrist = [left_wrist.x, left_wrist.y]
        elbow = [left_elbow.x, left_elbow.y]
        shoulder = [left_shoulder.x, left_shoulder.y]

        angle = calculate_angle(wrist, elbow, shoulder)

        if angle > 150:
            down = True
        elif angle < 80 and down:
            rep_count[workout_type] += 1
            down = False
            calories_burned[workout_type] += CALORIES_PER_REP[workout_type]

    elif workout_type == 'Squats':
        left_knee = landmarks.landmark[mp_pose.PoseLandmark.LEFT_KNEE]
        left_hip = landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP]
        left_ankle = landmarks.landmark[mp_pose.PoseLandmark.LEFT_ANKLE]

        knee = [left_knee.x, left_knee.y]
        hip = [left_hip.x, left_hip.y]
        ankle = [left_ankle.x, left_ankle.y]

        angle = calculate_angle(hip, knee, ankle)

        if angle < 90:
            down = True
        elif angle > 160 and down:
            rep_count[workout_type] += 1
            down = False
            calories_burned[workout_type] += CALORIES_PER_REP[workout_type]

    elif workout_type == 'Pull-ups':
        left_wrist = landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST]
        left_elbow = landmarks.landmark[mp_pose.PoseLandmark.LEFT_ELBOW]
        left_shoulder = landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER]

        wrist = [left_wrist.x, left_wrist.y]
        elbow = [left_elbow.x, left_elbow.y]
        shoulder = [left_shoulder.x, left_shoulder.y]

        angle = calculate_angle(wrist, elbow, shoulder)

        if angle > 160:
            down = True
        elif angle < 70 and down:
            rep_count[workout_type] += 1
            down = False
            calories_burned[workout_type] += CALORIES_PER_REP[workout_type]

    elif workout_type == 'Deadlifts':
        hip = [landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP.value].x,
               landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP.value].y]
        knee = [landmarks.landmark[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                landmarks.landmark[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
        ankle = [landmarks.landmark[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                 landmarks.landmark[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]

        angle = calculate_angle(hip, knee, ankle)

        if angle > 170:
            down = False
        elif angle < 145 and not down:
            rep_count[workout_type] += 1
            down = True
            calories_burned[workout_type] += CALORIES_PER_REP[workout_type]

@app.route('/upload', methods=['POST'])
def upload_file():
    global rep_count, workout_type, calories_burned, down, workout_started
    source = request.form.get('source')
    
    # Reset counters and state variables for a fresh start
    rep_count = {
        'Push-ups': 0,
        'Squats': 0,
        'Pull-ups': 0,
        'Deadlifts': 0
    }
    calories_burned = {
        'Push-ups': 0,
        'Squats': 0,
        'Pull-ups': 0,
        'Deadlifts': 0
    }
    down = False
    workout_type = None
    workout_started = False

    try:
        if source == "0":
            # Live camera capture
            cap = cv2.VideoCapture(0)
        else:
            # File upload
            if 'file' not in request.files:
                return "No file part in request", 400

            file = request.files['file']
            
            # If no file was selected
            if file.filename == '':
                return "No selected file", 400
            
            # Define the file path and save it
            file_path = './uploads/' + file.filename
            file.save(file_path)
            cap = cv2.VideoCapture(file_path)

        # Open the video and process frames
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Convert the frame to RGB
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False

            # Process the image and get pose landmarks
            results = pose.process(image)

            # Convert the image back to BGR for OpenCV
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            # Draw the pose annotations on the image
            if results.pose_landmarks:
                mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

                # Classify workout if landmarks are present
                classify_workout(results.pose_landmarks)

                # Count repetitions based on workout type
                if workout_started:
                    count_reps(results.pose_landmarks, workout_type)

            # Display the rep count and workout type on the frame
            cv2.putText(image, f'Workout: {workout_type if workout_type else "None"}', (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
            cv2.putText(image, f'Reps: {rep_count.get(workout_type, 0)}', (10, 60), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)

            if workout_type:
                cv2.putText(image, f'Calories: {calories_burned.get(workout_type, 0):.2f}', (10, 90), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
            
            # Show the processed image
            cv2.imshow('Workout Counter', image)

            # Break the loop on 'q' key press
            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

        # Release the capture when done
        cap.release()
        cv2.destroyAllWindows()


        # Generate a summary
        summary = {workout: {'reps': reps, 'calories': calories_burned[workout]} 
                   for workout, reps in rep_count.items() if reps > 0}
        
        return jsonify(summary)
    
    except Exception as e:
        print(f"Error: {e}")
        return "An error occurred during processing", 500

if __name__ == '__main__':
    app.run(debug=True)