# app.py with GitHub link and photo upload features
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import json
import os
import re
import base64
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this in production
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

# Add custom Jinja2 filter for newlines to <br> conversion
@app.template_filter('nl2br')
def nl2br_filter(s):
    if s:
        return s.replace('\n', '<br>')
    return s

# Data file paths
DATA_DIR = 'data'
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
PROJECTS_FILE = os.path.join(DATA_DIR, 'projects.json')

# Initialize data files if they don't exist
def initialize_data_files():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w') as f:
            json.dump({
                "users": [],
                "admins": ["admin"]  # Default admin username
            }, f)
    
    if not os.path.exists(PROJECTS_FILE):
        with open(PROJECTS_FILE, 'w') as f:
            json.dump([], f)

# Load users data
def load_users():
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

# Save users data
def save_users(data):
    with open(USERS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# Load projects data
def load_projects():
    with open(PROJECTS_FILE, 'r') as f:
        return json.load(f)

# Save projects data
def save_projects(data):
    with open(PROJECTS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# Helper function to convert video links to embeddable format
def convert_to_embed_link(video_url):
    if not video_url:
        return None
        
    # Handle YouTube links
    youtube_pattern = r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})'
    youtube_match = re.match(youtube_pattern, video_url)
    
    if youtube_match:
        video_id = youtube_match.group(1)
        return f'https://www.youtube.com/embed/{video_id}'
    
    # Handle Google Drive links
    drive_pattern = r'https://drive\.google\.com/file/d/([^/]+)/view'
    drive_match = re.match(drive_pattern, video_url)
    
    if drive_match:
        file_id = drive_match.group(1)
        return f'https://drive.google.com/file/d/{file_id}/preview'
    
    # Return original if not recognized
    return video_url

# Helper function to encode image to base64
def encode_image(file_data):
    if not file_data:
        return None
    
    encoded_string = base64.b64encode(file_data.read()).decode('utf-8')
    file_type = file_data.content_type
    return f"data:{file_type};base64,{encoded_string}"

# Routes
@app.route('/')
def index():
    projects = load_projects()
    return render_template('index.html', projects=projects)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        data = load_users()
        
        # Check if username already exists
        if any(user['username'] == username for user in data['users']):
            flash('Username already exists!')
            return redirect(url_for('register'))
        
        # Add new user
        data['users'].append({
            'username': username,
            'password': generate_password_hash(password),
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
        save_users(data)
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        data = load_users()
        
        # Check if user exists
        user = next((user for user in data['users'] if user['username'] == username), None)
        
        if user and check_password_hash(user['password'], password):
            session['username'] = username
            session['is_admin'] = username in data['admins']
            flash('Logged in successfully!')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password!')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!')
    return redirect(url_for('index'))

@app.route('/submit', methods=['GET', 'POST'])
def submit_project():
    if 'username' not in session:
        flash('Please log in to submit a project.')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        category = request.form['category']
        video_url = request.form.get('video_url', '')
        github_url = request.form.get('github_url', '')
        layout = request.form.get('layout', 'standard')
        
        # Convert video URL to embeddable format if provided
        embed_url = convert_to_embed_link(video_url) if video_url else None
        
        # Process uploaded photos
        photos = []
        photo_files = request.files.getlist('photos')
        
        for photo in photo_files:
            if photo and photo.filename:
                # Encode the image to base64
                photo_data = encode_image(photo)
                if photo_data:
                    photos.append({
                        'name': photo.filename,
                        'data': photo_data
                    })
        
        projects = load_projects()
        projects.append({
            'id': len(projects) + 1,
            'title': title,
            'description': description,
            'category': category,
            'video_url': video_url,
            'embed_url': embed_url,
            'github_url': github_url,
            'photos': photos,
            'layout': layout,
            'submitted_by': session['username'],
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
        save_projects(projects)
        flash('Project submitted successfully!')
        return redirect(url_for('index'))
    
    return render_template('submit.html')

@app.route('/admin')
def admin_panel():
    if 'username' not in session or not session.get('is_admin', False):
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('index'))
    
    users = load_users()['users']
    projects = load_projects()
    
    return render_template('admin.html', users=users, projects=projects)

@app.route('/project/<int:project_id>')
def view_project(project_id):
    projects = load_projects()
    project = next((p for p in projects if p['id'] == project_id), None)
    
    if project:
        return render_template('project_detail.html', project=project)
    else:
        flash('Project not found!')
        return redirect(url_for('index'))

@app.route('/api/projects')
def api_projects():
    projects = load_projects()
    return jsonify(projects)

@app.route('/api/delete_project/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    if 'username' not in session or not session.get('is_admin', False):
        return jsonify({'error': 'Access denied'}), 403
    
    projects = load_projects()
    projects = [p for p in projects if p['id'] != project_id]
    
    # Reassign IDs to maintain consistency
    for i, project in enumerate(projects):
        project['id'] = i + 1
    
    save_projects(projects)
    return jsonify({'success': True})

@app.route('/toggle-theme')
def toggle_theme():
    current_theme = session.get('theme', 'light')
    session['theme'] = 'dark' if current_theme == 'light' else 'light'
    return redirect(request.referrer or url_for('index'))

@app.context_processor
def inject_theme():
    return {'theme': session.get('theme', 'light')}

if __name__ == '__main__':
    initialize_data_files()
    app.run()