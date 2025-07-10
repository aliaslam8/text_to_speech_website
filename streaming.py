import os
import subprocess
import threading
import time
import uuid
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import logging

streaming_bp = Blueprint('streaming', __name__)

# Global dictionary to track active streams
active_streams = {}

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def ensure_upload_folder():
    """Ensure upload folder exists"""
    upload_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), UPLOAD_FOLDER)
    if not os.path.exists(upload_path):
        os.makedirs(upload_path)
    return upload_path

class StreamManager:
    def __init__(self, stream_id, video_path, stream_key, title="Live Stream"):
        self.stream_id = stream_id
        self.video_path = video_path
        self.stream_key = stream_key
        self.title = title
        self.process = None
        self.status = "preparing"
        self.start_time = None
        
    def start_stream(self):
        """Start FFmpeg streaming process"""
        try:
            self.status = "starting"
            
            # YouTube RTMP URL
            rtmp_url = f"rtmp://a.rtmp.youtube.com/live2/{self.stream_key}"
            
            # FFmpeg command for streaming to YouTube
            ffmpeg_cmd = [
                'ffmpeg',
                '-re',  # Read input at native frame rate
                '-i', self.video_path,  # Input video file
                '-c:v', 'libx264',  # Video codec
                '-preset', 'veryfast',  # Encoding preset
                '-maxrate', '3000k',  # Max bitrate
                '-bufsize', '6000k',  # Buffer size
                '-pix_fmt', 'yuv420p',  # Pixel format
                '-g', '50',  # GOP size
                '-c:a', 'aac',  # Audio codec
                '-b:a', '160k',  # Audio bitrate
                '-ac', '2',  # Audio channels
                '-ar', '44100',  # Audio sample rate
                '-f', 'flv',  # Output format
                rtmp_url  # RTMP URL
            ]
            
            logger.info(f"Starting stream {self.stream_id} with command: {' '.join(ffmpeg_cmd)}")
            
            # Start FFmpeg process
            self.process = subprocess.Popen(
                ffmpeg_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            self.status = "streaming"
            self.start_time = time.time()
            
            # Monitor the process
            self._monitor_process()
            
        except Exception as e:
            logger.error(f"Error starting stream {self.stream_id}: {str(e)}")
            self.status = "error"
            
    def _monitor_process(self):
        """Monitor FFmpeg process in a separate thread"""
        def monitor():
            try:
                # Wait for process to complete
                stdout, stderr = self.process.communicate()
                
                if self.process.returncode == 0:
                    self.status = "completed"
                    logger.info(f"Stream {self.stream_id} completed successfully")
                else:
                    self.status = "error"
                    logger.error(f"Stream {self.stream_id} failed with return code {self.process.returncode}")
                    logger.error(f"FFmpeg stderr: {stderr}")
                    
            except Exception as e:
                logger.error(f"Error monitoring stream {self.stream_id}: {str(e)}")
                self.status = "error"
                
        monitor_thread = threading.Thread(target=monitor)
        monitor_thread.daemon = True
        monitor_thread.start()
        
    def stop_stream(self):
        """Stop the streaming process"""
        if self.process and self.process.poll() is None:
            self.process.terminate()
            self.status = "stopped"
            logger.info(f"Stream {self.stream_id} stopped")
            
    def get_status(self):
        """Get current stream status"""
        return {
            'stream_id': self.stream_id,
            'status': self.status,
            'title': self.title,
            'start_time': self.start_time,
            'duration': time.time() - self.start_time if self.start_time else 0
        }

@streaming_bp.route('/upload', methods=['POST'])
def upload_video():
    """Handle video upload and start streaming"""
    try:
        # Check if files are present
        if 'videos' not in request.files:
            return jsonify({'error': 'No video files provided'}), 400
            
        files = request.files.getlist('videos')
        stream_keys = request.form.getlist('stream_keys')
        titles = request.form.getlist('titles')
        
        if len(files) != len(stream_keys):
            return jsonify({'error': 'Number of videos must match number of stream keys'}), 400
            
        # Ensure upload folder exists
        upload_path = ensure_upload_folder()
        
        results = []
        
        for i, file in enumerate(files):
            if file.filename == '':
                continue
                
            if file and allowed_file(file.filename):
                # Generate unique stream ID
                stream_id = str(uuid.uuid4())
                
                # Secure filename
                filename = secure_filename(file.filename)
                timestamp = str(int(time.time()))
                unique_filename = f"{timestamp}_{stream_id}_{filename}"
                
                # Save file
                file_path = os.path.join(upload_path, unique_filename)
                file.save(file_path)
                
                # Get stream key and title
                stream_key = stream_keys[i] if i < len(stream_keys) else ""
                title = titles[i] if i < len(titles) else f"Stream {i+1}"
                
                if not stream_key:
                    results.append({
                        'stream_id': stream_id,
                        'status': 'error',
                        'message': 'Stream key is required'
                    })
                    continue
                
                # Create stream manager
                stream_manager = StreamManager(stream_id, file_path, stream_key, title)
                active_streams[stream_id] = stream_manager
                
                # Start streaming in a separate thread
                stream_thread = threading.Thread(target=stream_manager.start_stream)
                stream_thread.daemon = True
                stream_thread.start()
                
                results.append({
                    'stream_id': stream_id,
                    'status': 'started',
                    'title': title,
                    'filename': filename
                })
                
            else:
                results.append({
                    'status': 'error',
                    'message': f'Invalid file type: {file.filename}'
                })
                
        return jsonify({'results': results}), 200
        
    except Exception as e:
        logger.error(f"Error in upload_video: {str(e)}")
        return jsonify({'error': str(e)}), 500

@streaming_bp.route('/streams', methods=['GET'])
def get_streams():
    """Get status of all active streams"""
    try:
        streams = []
        for stream_id, manager in active_streams.items():
            streams.append(manager.get_status())
        return jsonify({'streams': streams}), 200
    except Exception as e:
        logger.error(f"Error in get_streams: {str(e)}")
        return jsonify({'error': str(e)}), 500

@streaming_bp.route('/streams/<stream_id>', methods=['GET'])
def get_stream_status(stream_id):
    """Get status of a specific stream"""
    try:
        if stream_id not in active_streams:
            return jsonify({'error': 'Stream not found'}), 404
            
        manager = active_streams[stream_id]
        return jsonify(manager.get_status()), 200
    except Exception as e:
        logger.error(f"Error in get_stream_status: {str(e)}")
        return jsonify({'error': str(e)}), 500

@streaming_bp.route('/streams/<stream_id>/stop', methods=['POST'])
def stop_stream(stream_id):
    """Stop a specific stream"""
    try:
        if stream_id not in active_streams:
            return jsonify({'error': 'Stream not found'}), 404
            
        manager = active_streams[stream_id]
        manager.stop_stream()
        
        return jsonify({'message': f'Stream {stream_id} stopped'}), 200
    except Exception as e:
        logger.error(f"Error in stop_stream: {str(e)}")
        return jsonify({'error': str(e)}), 500

@streaming_bp.route('/streams/stop-all', methods=['POST'])
def stop_all_streams():
    """Stop all active streams"""
    try:
        stopped_count = 0
        for stream_id, manager in active_streams.items():
            if manager.status == "streaming":
                manager.stop_stream()
                stopped_count += 1
                
        return jsonify({'message': f'Stopped {stopped_count} streams'}), 200
    except Exception as e:
        logger.error(f"Error in stop_all_streams: {str(e)}")
        return jsonify({'error': str(e)}), 500

