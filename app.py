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
    url = request.json.get('url')
    if not url:
        return jsonify({'error': 'URL is required'}), 400

    output_path_template = os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s')
    
    try:
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best',
            'outtmpl': output_path_template,
            'merge_output_format': 'mkv',
            'cookiefile': 'cookies.txt'
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info_dict).replace('.mp4', '.mkv').replace('.webm', '.mkv')
            final_filename = os.path.basename(filename)

        return jsonify({'download_filename': final_filename})

    except Exception as e:
        # --- MODIFIED: Enhanced Error Logging ---
        # Print the full, detailed error to the server logs for debugging.
        # The flush=True ensures the message appears immediately in the logs.
        print(f"--- DETAILED ERROR --- \n{e}\n--- END ERROR ---", flush=True)

        error_message = str(e)
        if 'Sign in to confirm your age' in error_message:
            return jsonify({'error': 'This is an age-restricted video. Please provide a cookies.txt file from your browser to download it.'}), 403
        
        # Return a more informative generic error for the user
        return jsonify({'error': 'An unexpected error occurred on the server. The issue has been logged.'}), 500

# --- Route to serve the downloaded files ---
@app.route('/downloads/<filename>')
def download_file(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)

# --- Run the application ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

