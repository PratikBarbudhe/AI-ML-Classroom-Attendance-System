import os
import cv2
import numpy as np
import face_recognition
import pickle
from datetime import datetime

class FaceUtils:
    def __init__(self, faces_dir='data/faces', models_dir='data/models'):
        self.faces_dir = faces_dir
        self.models_dir = models_dir
        self.face_encodings = []
        self.face_names = []
        self.model_trained = False
        self.model_path = os.path.join(self.models_dir, 'face_recognition_model.pkl')
        
        # Create directories if they don't exist
        os.makedirs(self.faces_dir, exist_ok=True)
        os.makedirs(self.models_dir, exist_ok=True)
        
        # Try to load existing model
        self.load_model()
    
    def capture_face_samples(self, person_name, source='webcam', image_path=None, num_samples=10):
        """Capture face samples from webcam or image file"""
        person_dir = os.path.join(self.faces_dir, person_name)
        os.makedirs(person_dir, exist_ok=True)
        
        samples_captured = 0
        
        if source == 'webcam':
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                return False, "Error: Could not open webcam"
                
            while samples_captured < num_samples:
                ret, frame = cap.read()
                if not ret:
                    break
                    
                # Find faces in the frame
                face_locations = face_recognition.face_locations(frame)
                
                # Display the frame with face rectangles
                for (top, right, bottom, left) in face_locations:
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                
                # Display count
                cv2.putText(frame, f"Person: {person_name}", (10, 30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                cv2.putText(frame, f"Captured: {samples_captured}/{num_samples}", (10, 60), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                cv2.putText(frame, "Press 'c' to capture, 'q' to quit", (10, 90), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                cv2.imshow("Capture Face Samples", frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('c') and len(face_locations) > 0:
                    # Save the face image
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                    filename = os.path.join(person_dir, f"{timestamp}.jpg")
                    cv2.imwrite(filename, frame)
                    samples_captured += 1
                elif key == ord('q'):
                    break
            
            cap.release()
            cv2.destroyAllWindows()
            
            if samples_captured < num_samples:
                return False, f"Only captured {samples_captured}/{num_samples} samples. Process interrupted."
            return True, f"Successfully captured {samples_captured} samples for {person_name}"
            
        elif source == 'image' and image_path is not None:
            if not os.path.exists(image_path):
                return False, f"Error: Image file {image_path} not found"
                
            try:
                # Load the image
                image = face_recognition.load_image_file(image_path)
                face_locations = face_recognition.face_locations(image)
                
                if len(face_locations) == 0:
                    return False, "No faces detected in the image"
                
                # Save individual faces from the image
                for i, (top, right, bottom, left) in enumerate(face_locations):
                    if samples_captured >= num_samples:
                        break
                        
                    face_image = image[top:bottom, left:right]
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                    filename = os.path.join(person_dir, f"{timestamp}_{i}.jpg")
                    
                    # Convert from RGB to BGR for OpenCV
                    face_image_bgr = cv2.cvtColor(face_image, cv2.COLOR_RGB2BGR)
                    cv2.imwrite(filename, face_image_bgr)
                    samples_captured += 1
                
                if samples_captured < num_samples:
                    return False, f"Only captured {samples_captured}/{num_samples} samples. Not enough faces in the image."
                return True, f"Successfully captured {samples_captured} samples for {person_name}"
                
            except Exception as e:
                return False, f"Error processing image: {str(e)}"
        
        return False, "Invalid source specified"
    
    def train_model(self):
        """Train face recognition model using the captured samples"""
        # Reset existing data
        self.face_encodings = []
        self.face_names = []
        
        try:
            # Iterate through each person's directory
            for person_name in os.listdir(self.faces_dir):
                person_dir = os.path.join(self.faces_dir, person_name)
                
                if not os.path.isdir(person_dir):
                    continue
                
                # Process each image file
                for image_file in os.listdir(person_dir):
                    image_path = os.path.join(person_dir, image_file)
                    
                    # Load image and find face encoding
                    face_image = face_recognition.load_image_file(image_path)
                    face_encodings = face_recognition.face_encodings(face_image)
                    
                    if len(face_encodings) > 0:
                        # Use the first face found in the image
                        self.face_encodings.append(face_encodings[0])
                        self.face_names.append(person_name)
            
            if len(self.face_encodings) == 0:
                return False, "No face samples found to train on"
            
            # Save the trained model
            model_data = {
                'encodings': self.face_encodings,
                'names': self.face_names
            }
            
            with open(self.model_path, 'wb') as f:
                pickle.dump(model_data, f)
            
            self.model_trained = True
            return True, f"Model trained successfully with {len(self.face_encodings)} face samples from {len(set(self.face_names))} people"
            
        except Exception as e:
            return False, f"Error training model: {str(e)}"
    
    def load_model(self):
        """Load a previously trained face recognition model"""
        if not os.path.exists(self.model_path):
            return False, "No saved model found"
        
        try:
            with open(self.model_path, 'rb') as f:
                model_data = pickle.load(f)
            
            self.face_encodings = model_data['encodings']
            self.face_names = model_data['names']
            self.model_trained = True
            
            return True, f"Model loaded successfully with {len(self.face_encodings)} face samples from {len(set(self.face_names))} people"
            
        except Exception as e:
            return False, f"Error loading model: {str(e)}"
    
    def recognize_faces(self, source='webcam', image_path=None, tolerance=0.6):
        """Recognize faces from webcam or image file"""
        if not self.model_trained:
            return False, "No trained model available. Please train the model first."
        
        if source == 'webcam':
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                return False, "Error: Could not open webcam"
            
            try:
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    # Convert from BGR (OpenCV) to RGB (face_recognition)
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    # Find faces and encodings
                    face_locations = face_recognition.face_locations(rgb_frame)
                    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
                    
                    # Loop through each face
                    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                        # Compare with known faces
                        matches = face_recognition.compare_faces(self.face_encodings, face_encoding, tolerance=tolerance)
                        name = "Unknown"
                        
                        # Use the known face with the smallest distance
                        face_distances = face_recognition.face_distance(self.face_encodings, face_encoding)
                        if len(face_distances) > 0:
                            best_match_index = np.argmin(face_distances)
                            if matches[best_match_index]:
                                name = self.face_names[best_match_index]
                        
                        # Draw rectangle and name
                        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
                        cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)
                    
                    # Display frame
                    cv2.putText(frame, "Press 'q' to quit", (10, 30), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    cv2.imshow('Face Recognition', frame)
                    
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                
                cap.release()
                cv2.destroyAllWindows()
                return True, "Face recognition completed"
                
            except Exception as e:
                cap.release()
                cv2.destroyAllWindows()
                return False, f"Error during face recognition: {str(e)}"
                
        elif source == 'image' and image_path is not None:
            if not os.path.exists(image_path):
                return False, f"Error: Image file {image_path} not found"
            
            try:
                # Load image
                image = cv2.imread(image_path)
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                
                # Find faces and encodings
                face_locations = face_recognition.face_locations(rgb_image)
                face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
                
                if len(face_locations) == 0:
                    return False, "No faces detected in the image"
                
                # Process each face
                for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                    # Compare with known faces
                    matches = face_recognition.compare_faces(self.face_encodings, face_encoding, tolerance=tolerance)
                    name = "Unknown"
                    
                    # Use the known face with the smallest distance
                    face_distances = face_recognition.face_distance(self.face_encodings, face_encoding)
                    if len(face_distances) > 0:
                        best_match_index = np.argmin(face_distances)
                        if matches[best_match_index]:
                            name = self.face_names[best_match_index]
                    
                    # Draw rectangle and name
                    cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 2)
                    cv2.rectangle(image, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
                    cv2.putText(image, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)
                
                # Display the image
                cv2.imshow('Face Recognition', image)
                cv2.waitKey(0)
                cv2.destroyAllWindows()
                
                return True, f"Recognized {len(face_locations)} faces in the image"
                
            except Exception as e:
                return False, f"Error processing image: {str(e)}"
        
        return False, "Invalid source specified" 