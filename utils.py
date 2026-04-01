"""
Utility functions for the AI Classroom Attendance System.
Contains helper functions for common operations like validation,
image processing, file handling, and logging setup.
"""

import os
import logging
import csv
from datetime import datetime
from pathlib import Path
import config


def setup_logging(log_file=None, level=config.LOG_LEVEL):
    """
    Configure logging for the application.
    
    Args:
        log_file: Path to log file (uses config default if None)
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        logger: Configured logger instance
    """
    if log_file is None:
        log_file = config.LOG_FILE
    
    # Create logs directory
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure logging format
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=config.LOG_FORMAT,
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)


def validate_person_name(name):
    """
    Validate person name for capture operations.
    
    Args:
        name: Person name to validate
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not isinstance(name, str):
        return False, "Name must be a string"
    
    name = name.strip()
    
    if len(name) < config.MIN_NAME_LENGTH:
        return False, f"Name too short (minimum {config.MIN_NAME_LENGTH} characters)"
    
    if len(name) > config.MAX_NAME_LENGTH:
        return False, f"Name too long (maximum {config.MAX_NAME_LENGTH} characters)"
    
    # Allow alphanumeric, spaces, hyphens, and apostrophes
    if not all(c.isalnum() or c in ' -\'' for c in name):
        return False, "Name contains invalid characters"
    
    return True, None


def validate_image_file(file_path):
    """
    Validate if file is a valid image.
    
    Args:
        file_path: Path to image file
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not os.path.exists(file_path):
        return False, "File does not exist"
    
    if not os.path.isfile(file_path):
        return False, "Path is not a file"
    
    ext = Path(file_path).suffix.lower()
    if ext not in config.VALID_IMAGE_EXTENSIONS:
        return False, f"Invalid image extension. Supported: {config.VALID_IMAGE_EXTENSIONS}"
    
    return True, None


def is_valid_camera_index(index):
    """
    Check if camera index is a valid non-negative integer.
    
    Args:
        index: Camera index to validate
    
    Returns:
        bool: True if valid
    """
    try:
        idx = int(index)
        return idx >= 0
    except (ValueError, TypeError):
        return False


def format_timestamp(dt=None):
    """
    Format datetime to ISO format string.
    
    Args:
        dt: datetime object (uses current time if None)
    
    Returns:
        str: Formatted timestamp
    """
    if dt is None:
        dt = datetime.now()
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def parse_timestamp(timestamp_str):
    """
    Parse ISO format timestamp string to datetime.
    
    Args:
        timestamp_str: ISO format timestamp string
    
    Returns:
        datetime: Parsed datetime object
    """
    try:
        return datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        raise ValueError(f"Invalid timestamp format: {timestamp_str}")


def ensure_directory_exists(directory):
    """
    Ensure directory exists, create if necessary.
    
    Args:
        directory: Path to directory
    
    Returns:
        Path: Path object for the directory
    """
    dir_path = Path(directory)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def get_sample_count_for_person(person_name, faces_dir=None):
    """
    Get number of captured samples for a person.
    
    Args:
        person_name: Name of the person
        faces_dir: Directory containing face samples (uses config default if None)
    
    Returns:
        int: Number of samples
    """
    if faces_dir is None:
        faces_dir = config.FACES_DIR
    
    person_dir = Path(faces_dir) / person_name
    
    if not person_dir.exists():
        return 0
    
    image_files = [f for f in person_dir.iterdir() 
                   if f.suffix.lower() in config.VALID_IMAGE_EXTENSIONS]
    
    return len(image_files)


def export_attendance_to_csv(records, output_path):
    """
    Export attendance records to CSV file.
    
    Args:
        records: List of attendance record dictionaries
        output_path: Output CSV file path
    
    Returns:
        tuple: (success, message)
    """
    try:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if not records:
            return False, "No records to export"
        
        with open(output_path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=config.EXPORT_CSV_COLUMNS)
            writer.writeheader()
            
            for record in records:
                try:
                    writer.writerow({
                        'Name': record.get('person_name', 'Unknown'),
                        'Time': record.get('recognized_at', 'Unknown'),
                        'Confidence': f"{float(record.get('confidence', 0)):.2f}",
                        'Source': record.get('source', 'Unknown')
                    })
                except Exception as e:
                    logging.warning(f"Error writing record: {e}")
        
        return True, f"Exported {len(records)} records to {output_path}"
    
    except Exception as e:
        return False, f"Error exporting to CSV: {str(e)}"


def get_attended_students(records):
    """
    Get unique list of students who attended from records.
    
    Args:
        records: List of attendance records
    
    Returns:
        list: Sorted list of unique student names
    """
    names = set(record.get('person_name', 'Unknown') for record in records)
    return sorted(list(names))


def calculate_attendance_statistics(records):
    """
    Calculate attendance statistics from records.
    
    Args:
        records: List of attendance records
    
    Returns:
        dict: Statistics including count, unique people, average confidence
    """
    if not records:
        return {
            'total_records': 0,
            'unique_people': 0,
            'average_confidence': 0.0,
            'min_confidence': 0.0,
            'max_confidence': 0.0
        }
    
    confidences = [float(r.get('confidence', 0)) for r in records]
    
    return {
        'total_records': len(records),
        'unique_people': len(set(r.get('person_name') for r in records)),
        'average_confidence': sum(confidences) / len(confidences),
        'min_confidence': min(confidences),
        'max_confidence': max(confidences)
    }
