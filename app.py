import os
import csv
import io
import shutil
import tempfile
import zipfile
import requests
from flask import Flask, request, send_file, render_template
from mutagen.flac import FLAC
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Increase max upload size just in case, though we only upload CSVs
app.config['DOWNLOAD_FOLDER'] = os.getenv('DOWNLOAD_DIR', '/downloads')

# Ensure download directory exists
os.makedirs(app.config['DOWNLOAD_FOLDER'], exist_ok=True)

def clean_filename(name):
    return secure_filename(name)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/dataset', methods=['POST'])
def process_csv():
    if 'file' not in request.files:
        return "No file part", 400
    
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400

    if not file.filename.endswith('.csv'):
        return "File must be a CSV", 400

    processed_files = []
    errors = []

    try:
        # Read CSV content
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_reader = csv.DictReader(stream)

        for row in csv_reader:
            flac_url = row.get('FLAC URL')
            artist = row.get('Artist', 'Unknown Artist')
            title = row.get('Title', 'Unknown Title')
            album = row.get('Album', '')

            if not flac_url:
                continue

            # Construct safe filename
            # We want "Artist - Title.flac"
            unsafe_filename = f"{artist} - {title}.flac"
            safe_filename = unsafe_filename.replace("/", "-").replace("\\", "-")
            
            file_path = os.path.join(app.config['DOWNLOAD_FOLDER'], safe_filename)
            
            # Simple check if file already exists to skip? 
            # User didn't ask, but it's good practice. Overwriting is fine too.
            print(f"Processing: {safe_filename}")

            try:
                # Download
                with requests.get(flac_url, stream=True) as r:
                    r.raise_for_status()
                    with open(file_path, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
                
                # Tag
                try:
                    audio = FLAC(file_path)
                    audio['title'] = title
                    audio['artist'] = artist
                    if album:
                        audio['album'] = album
                    audio.save()
                    processed_files.append(safe_filename)
                except Exception as e:
                    errors.append(f"Downloaded but failed to tag {safe_filename}: {e}")
                    processed_files.append(safe_filename) # Still count as processed

            except Exception as e:
                errors.append(f"Failed to download {safe_filename}: {e}")

        # Return a simple summary
        summary_html = "<h1>Download Complete</h1>"
        summary_html += f"<p>Successfully processed: {len(processed_files)} files.</p>"
        summary_html += f"<p>Saved to: {app.config['DOWNLOAD_FOLDER']}</p>"
        
        if errors:
            summary_html += "<h2>Errors:</h2><ul>"
            for err in errors:
                summary_html += f"<li>{err}</li>"
            summary_html += "</ul>"
        
        summary_html += '<br><a href="/">Go Back</a>'
        return summary_html

    except Exception as e:
        return f"An error occurred: {str(e)}", 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
