# YouTube Live Streamer

A Flask-based web application that allows users to upload multiple pre-recorded MP4 video files and stream them simultaneously to YouTube Live using FFmpeg. Each video upload is accompanied by a YouTube stream key and an optional custom stream title.

## Features

- **Multiple Video Upload**: Upload multiple MP4, AVI, MOV, or MKV video files
- **Simultaneous Streaming**: Stream multiple videos to YouTube Live simultaneously
- **Independent Streams**: Each stream runs in a separate background process using threading
- **Dynamic Interface**: Add/remove video upload fields dynamically
- **Real-time Status**: Monitor stream status in real-time
- **Responsive Design**: Works on both desktop and mobile devices
- **No Login Required**: Direct access to upload panel

## Requirements

- Python 3.11+
- FFmpeg
- YouTube Live stream keys

## Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd youtube-live-streamer
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install FFmpeg**
   - **Ubuntu/Debian**: `sudo apt install ffmpeg`
   - **macOS**: `brew install ffmpeg`
   - **Windows**: Download from [FFmpeg website](https://ffmpeg.org/download.html)

5. **Run the application**
   ```bash
   python src/main.py
   ```

6. **Access the application**
   Open your browser and go to `http://localhost:3000`

## Deployment

### Railway

1. **Connect your GitHub repository to Railway**
2. **Set environment variables** (if needed)
3. **Deploy** - Railway will automatically detect the configuration

### Replit

1. **Import the repository into Replit**
2. **Run the application** - Replit will automatically install dependencies
3. **Access via the provided URL**

### Heroku

1. **Create a new Heroku app**
   ```bash
   heroku create your-app-name
   ```

2. **Add FFmpeg buildpack**
   ```bash
   heroku buildpacks:add --index 1 https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest.git
   heroku buildpacks:add --index 2 heroku/python
   ```

3. **Deploy**
   ```bash
   git push heroku main
   ```

### Docker

1. **Build the image**
   ```bash
   docker build -t youtube-live-streamer .
   ```

2. **Run the container**
   ```bash
   docker run -p 3000:3000 youtube-live-streamer
   ```

## Usage

1. **Access the application** in your web browser
2. **Upload videos**:
   - Click "Choose File" or drag and drop video files
   - Enter your YouTube stream key for each video
   - Optionally add a custom stream title
3. **Add more videos** using the "+ Add Another Video" button
4. **Start streaming** by clicking "🚀 Start Streaming"
5. **Monitor streams** in the Stream Status section
6. **Stop streams** individually or all at once

## Getting YouTube Stream Keys

1. Go to [YouTube Studio](https://studio.youtube.com)
2. Click "Go Live" in the top right
3. Choose "Stream" option
4. Copy the "Stream key" from the stream settings
5. Use this key in the application

## Technical Details

### Architecture

- **Backend**: Flask with CORS enabled
- **Frontend**: HTML/CSS/JavaScript (no frameworks)
- **Streaming**: FFmpeg with RTMP to YouTube
- **Concurrency**: Python threading for multiple simultaneous streams
- **File Handling**: Secure file uploads with size limits (500MB)

### API Endpoints

- `POST /api/streaming/upload` - Upload videos and start streaming
- `GET /api/streaming/streams` - Get all stream statuses
- `GET /api/streaming/streams/<id>` - Get specific stream status
- `POST /api/streaming/streams/<id>/stop` - Stop specific stream
- `POST /api/streaming/streams/stop-all` - Stop all streams

### FFmpeg Configuration

The application uses optimized FFmpeg settings for YouTube Live:
- Video codec: H.264 (libx264)
- Audio codec: AAC
- Bitrate: 3000k max
- Frame rate: Native
- Resolution: Original

## Environment Variables

- `PORT` - Server port (default: 3000)
- `SECRET_KEY` - Flask secret key (auto-generated)

## File Structure

```
youtube-live-streamer/
├── src/
│   ├── main.py              # Main Flask application
│   ├── routes/
│   │   ├── streaming.py     # Streaming API routes
│   │   └── user.py          # User routes (template)
│   ├── models/
│   │   └── user.py          # Database models (template)
│   ├── static/
│   │   └── index.html       # Frontend interface
│   └── database/
│       └── app.db           # SQLite database
├── uploads/                 # Uploaded video files
├── requirements.txt         # Python dependencies
├── Procfile                 # Railway/Heroku config
├── railway.toml            # Railway config
├── .replit                 # Replit config
├── replit.nix              # Replit Nix config
├── Dockerfile              # Docker config
└── README.md               # This file
```

## Security Considerations

- File upload size limited to 500MB
- Only specific video formats allowed
- Secure filename handling
- CORS enabled for frontend-backend communication
- Stream keys are not logged or stored permanently

## Troubleshooting

### Common Issues

1. **FFmpeg not found**
   - Ensure FFmpeg is installed and in PATH
   - On cloud platforms, use appropriate buildpacks

2. **Port already in use**
   - Change the PORT environment variable
   - Kill existing processes using the port

3. **Stream fails to start**
   - Verify YouTube stream key is correct
   - Check internet connection
   - Ensure video file is valid

4. **Upload fails**
   - Check file size (max 500MB)
   - Verify file format is supported
   - Ensure sufficient disk space

### Logs

Check application logs for detailed error messages:
- Local: Console output
- Railway: Railway dashboard logs
- Heroku: `heroku logs --tail`
- Docker: `docker logs <container-id>`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs for error messages
3. Create an issue on GitHub with detailed information

## Disclaimer

This application is for educational and personal use. Ensure you comply with YouTube's Terms of Service and have proper rights to stream the content you upload.

