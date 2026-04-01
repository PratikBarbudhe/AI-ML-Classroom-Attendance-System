"""
Face detection and recognition utilities.
Handles face capture, model training, and recognition with comprehensive error handling.
"""

import os
import cv2
import numpy as np
import pickle
import logging
from datetime import datetime
from pathlib import Path

import config
import utils

logger = logging.getLogger(__name__)

try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    logger.warning("face_recognition library not available. Some features will be disabled.")


class FaceUtils:
    """Utilities for face detection and recognition."""
    
    def __init__(self, faces_dir=None, models_dir=None):
        """
        Initialize FaceUtils.
        
        Args:
            faces_dir: Directory for storing face samples (uses config default if None)
            models_dir: Directory for storing trained models (uses config default if None)
        """
        self.faces_dir = Path(faces_dir) if faces_dir else config.FACES_DIR
        self.models_dir = Path(models_dir) if models_dir else config.MODELS_DIR
        
        self.face_encodings = []
        self.face_names = []
        self.model_trained = False
        self.model_path = self.models_dir / 'face_model.pkl'
        
        # Create directories if they don't exist
        self.faces_dir.mkdir(parents=True, exist_ok=True)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"FaceUtils initialized - Faces: {self.faces_dir}, Models: {self.models_dir}")
        
        # Try to load existing model
        self.load_model()
    
    def _validate_person_name(self, person_name):
        """Validate person name."""
        is_valid, error = utils.validate_person_name(person_name)
        if not is_valid:
            logger.warning(f"Invalid person name: {error}")
        return is_valid, error
    
    def capture_face_samples(self, person_name, source='webcam', image_path=None, num_samples=None):
        """
        Capture face samples from webcam or image file.
        
        Args:
            person_name: Name of the person
            source: 'webcam' or 'image'
            image_path: Path to image file (required if source='image')
            num_samples: Number of samples (uses config default if None)
        
        Returns:
            tuple: (success, message)
        """
        if not FACE_RECOGNITION_AVAILABLE:
            return False, "face_recognition library not available"
        
        is_valid, error_msg = self._validate_person_name(person_name)
        if not is_valid:
            return False, error_msg
        
        if num_samples is None:
            num_samples = config.FACE_SAMPLES_REQUIRED
        
        person_dir = self.faces_dir / person_name
        person_dir.mkdir(parents=True, exist_ok=True)
        
        if source == 'webcam':
            return self._capture_from_webcam(person_name, person_dir, num_samples)
        elif source == 'image':
            if not image_path:
                return False, "Image path required for image source"
            return self._capture_from_image(image_path, person_name, person_dir, num_samples)
        else:
            return False, f"Invalid source: {source}"
    
    def _capture_from_webcam(self, person_name, person_dir, num_samples):
        """Capture face samples from webcam."""
        try:
            cap = cv2.VideoCapture(config.DEFAULT_CAMERA_INDEX)
            if not cap.isOpened():
                logger.error("Could not open webcam")
                return False, config.ERROR_MESSAGES['camera_not_found']
            
            samples_captured = 0
            
            try:
                while samples_captured < num_samples:
                    ret, frame = cap.read()
                    if not ret:
                        logger.error("Failed to read frame")
                        break
                    
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    face_locations = face_recognition.face_locations(rgb_frame, model='hog')
                    
                    for (top, right, bottom, left) in face_locations:
                        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                    
                    cv2.putText(frame, f"Person: {person_name}", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    cv2.putText(frame, f"Captured: {samples_captured}/{num_samples}", (10, 60),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    cv2.putText(frame, "Press 'c' to capture, 'q' to quit", (10, 90),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    
                    cv2.imshow("Capture Face Samples", frame)
                    
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('c') and len(face_locations) > 0:
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                        filename = person_dir / f"{timestamp}.jpg"
                        cv2.imwrite(str(filename), frame)
                        samples_captured += 1
                    elif key == ord('q'):
                        break
            
            finally:
                cap.release()
                cv2.destroyAllWindows()
            
            if samples_captured == 0:
                return False, config.ERROR_MESSAGES['no_faces_detected']
            
            logger.info(f"Captured {samples_captured} samples for {person_name}")
            return True, f"Captured {samples_captured}/{num_samples} samples"
        
        except Exception as e:
            logger.error(f"Error capturing from webcam: {e}")
            return False, f"Error: {str(e)}"
    
    def _capture_from_image(self, image_path, person_name, person_dir, num_samples):
        """Capture face samples from an image file."""
        try:
            is_valid, error_msg = utils.validate_image_file(image_path)
            if not is_valid:
                return False, error_msg
            
            image = face_recognition.load_image_file(image_path)
            face_locations = face_recognition.face_locations(image, model='hog')
            
            if len(face_locations) == 0:
                return False, config.ERROR_MESSAGES['no_faces_in_image']
            
            samples_captured = 0
            for i, (top, right, bottom, left) in enumerate(face_locations):
                if samples_captured >= num_samples:
                    break
                face_image = image[top:bottom, left:right]
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                filename = person_dir / f"{timestamp}_{i}.jpg"
                face_image_bgr = cv2.cvtColor(face_image, cv2.COLOR_RGB2BGR)
                cv2.imwrite(str(filename), face_image_bgr)
                samples_captured += 1
            
            return True, f"Extracted {samples_captured} faces from image"
        
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            return False, f"Error: {str(e)}"
    
    def train_model(self):
        """
        Train face recognition model using captured samples.
        
        Returns:
            tuple: (success, message)
        """
        if not FACE_RECOGNITION_AVAILABLE:
            return False, "face_recognition library not available"
        
        try:
            logger.info("Starting model training...")
            
            self.face_encodings = []
            self.face_names = []
            
            people_count = 0
            encodings_count = 0
            
            for person_dir in self.faces_dir.iterdir():
                if not person_dir.is_dir():
                    continue
                
                person_name = person_dir.name
                people_count += 1
                
                for image_file in person_dir.iterdir():
                    if image_file.suffix.lower() not in config.VALID_IMAGE_EXTENSIONS:
                        continue
                    
                    try:
                        face_image = face_recognition.load_image_file(str(image_file))
                        face_encodings = face_recognition.face_encodings(face_image, model='small')
                        
                        if len(face_encodings) > 0:
                            self.face_encodings.append(face_encodings[0])
                            self.face_names.append(person_name)
                            encodings_count += 1
                    except Exception as e:
                        logger.warning(f"Error processing {image_file}: {e}")
            
            if len(self.face_encodings) == 0:
                return False, config.ERROR_MESSAGES['insufficient_samples']
            
            self.models_dir.mkdir(parents=True, exist_ok=True)
            with open(self.model_path, 'wb') as f:
                pickle.dump({'encodings': self.face_encodings, 'names': self.face_names}, f)
            
            self.model_trained = True
            logger.info(f"Model trained: {encodings_count} encodings from {people_count} people")
            return True, f"Model trained: {encodings_count} encodings from {people_count} people"
        
        except Exception as e:
            logger.error(f"Error training model: {e}")
            return False, f"Error: {str(e)}"
    
    def load_model(self):
        """Load a previously trained face recognition model."""
        if not self.model_path.exists():
            logger.info("No saved model found")
            return False, "No saved model"
        
        try:
            with open(self.model_path, 'rb') as f:
                model_data = pickle.load(f)
            
            self.face_encodings = model_data.get('encodings', [])
            self.face_names = model_data.get('names', [])
            
            if len(self.face_encodings) > 0:
                self.model_trained = True
                people = len(set(self.face_names))
                logger.info(f"Model loaded: {len(self.face_encodings)} encodings from {people} people")
                return True, f"Model loaded"
            return False, "Model file empty"
        
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False, f"Error: {str(e)}"
    
    def recognize_faces(self, frame, tolerance=None):
        """
        Recognize faces in a frame.
        
        Args:
            frame: OpenCV frame (BGR format)
            tolerance: Match tolerance (uses config if None)
        
        Returns:
            list: [(name, confidence, location), ...]
        """
        if not FACE_RECOGNITION_AVAILABLE or not self.model_trained:
            return []
        
        if tolerance is None:
            tolerance = config.FACE_MATCH_TOLERANCE
        
        try:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame, model='hog')
            
            if not face_locations:
                return []
            
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations, model='small')
            results = []
            
            for face_encoding, face_location in zip(face_encodings, face_locations):
                distances = face_recognition.face_distance(self.face_encodings, face_encoding)
                
                if len(distances) > 0:
                    min_idx = np.argmin(distances)
                    min_dist = distances[min_idx]
                    
                    if min_dist < tolerance:
                        name = self.face_names[min_idx]
                        confidence = 1 - min_dist
                        results.append((name, confidence, face_location))
                    else:
                        results.append(("Unknown", 0.0, face_location))
            
            return results
        
        except Exception as e:
            logger.error(f"Error recognizing faces: {e}")
            return []
    
    
    def get_person_sample_count(self, person_name):
        """Get number of samples for a person."""
        return utils.get_sample_count_for_person(person_name, self.faces_dir)
    
    def get_trained_people(self):
        """Get list of people with samples."""
        people = []
        for person_dir in self.faces_dir.iterdir():
            if person_dir.is_dir():
                people.append(person_dir.name)
        return sorted(people)
                
                return True, f"Recognized {len(face_locations)} faces in the image"
                
            except Exception as e:
                return False, f"Error processing image: {str(e)}"
        
        return False, "Invalid source specified" 