from flask import Flask, request, jsonify, send_from_directory, render_template
import yt_dlp
import os
import uuid # Used to generate unique filenames

# Initialize the Flask application
app = Flask(__name__)

# Configure the download folder
DOWNLOAD_FOLDER = os.path.join(os.getcwd(), "downloads")
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# --- Route to serve the main HTML page ---
@app.route('/')
def index():
    # Renders the index.html file from the 'templates' folder
    return render_template('index.html')

# --- API endpoint for downloading the video ---
@app.route('/download', methods=['POST'])
def download():
    # Get the YouTube URL from the JSON request sent by the frontend
    url = request.json.get('url')
    if not url:
        return jsonify({'error': 'URL is required'}), 400

    # Generate a unique filename to prevent conflicts
    unique_filename = f"{uuid.uuid4()}.mkv"
    output_path_template = os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s')
    
    # Final output path for the merged file
    # We don't know the final title yet, so we will find it after download
    final_output_path = None
    
    try:
        # yt-dlp options
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best',
            'outtmpl': output_path_template,
            'merge_output_format': 'mkv',
            'cookiefile': 'cookies.txt' # <-- ADDED: Tell yt-dlp to use the cookie file
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            # Construct the final filename based on the video title
            filename = ydl.prepare_filename(info_dict).replace('.mp4', '.mkv').replace('.webm', '.mkv')
            final_filename = os.path.basename(filename)

        # Return the filename for the user to download
        return jsonify({'download_filename': final_filename})

    except Exception as e:
        # Check for the specific age-gate error and provide a helpful message
        error_message = str(e)
        if 'Sign in to confirm your age' in error_message:
            return jsonify({'error': 'This is an age-restricted video. Please provide a cookies.txt file from your browser to download it.'}), 403 # HTTP 403 Forbidden
        
        # Return a generic error for other issues
        return jsonify({'error': 'An error occurred during download.'}), 500

# --- Route to serve the downloaded files ---
@app.route('/downloads/<filename>')
def download_file(filename):
    # Provides the file from the 'downloads' directory to the user's browser
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)

# --- Run the application ---
if __name__ == '__main__':
    # Starts the web server
    # Use host='0.0.0.0' to make it accessible on your local network
    app.run(host='0.0.0.0', port=5000, debug=True)

