import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, session, abort
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your-secret-key'

ROOT_DIR = os.getcwd()  # Serve from current working directory

# Users: admin and guest with permissions
USERS = {
    'admin': 'admin',
    'guest': 'guest',
}

def safe_join(base, *paths):
    # Prevent directory traversal attacks
    final_path = os.path.abspath(os.path.join(base, *paths))
    if not final_path.startswith(base):
        raise ValueError("Invalid path")
    return final_path

def list_dir(rel_path=""):
    abs_path = safe_join(ROOT_DIR, rel_path)
    entries = []
    with os.scandir(abs_path) as it:
        for entry in it:
            entries.append({
                "name": entry.name,
                "is_dir": entry.is_dir(),
                "size": entry.stat().st_size if not entry.is_dir() else None,
            })
    # Sort folders first, then files
    entries.sort(key=lambda e: (not e["is_dir"], e["name"].lower()))
    return entries

def get_breadcrumbs(rel_path):
    parts = rel_path.split('/') if rel_path else []
    crumbs = []
    for i in range(len(parts)):
        crumb_path = '/'.join(parts[:i+1])
        crumbs.append((parts[i], crumb_path))
    return crumbs

def is_logged_in():
    return 'username' in session

def is_admin():
    return session.get('username') == 'admin'

@app.route('/', methods=['GET', 'POST'])
def index():
    if not is_logged_in():
        return redirect(url_for('login'))
    
    rel_path = request.args.get('path', '')
    try:
        abs_path = safe_join(ROOT_DIR, rel_path)
    except ValueError:
        flash('Invalid path', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        # Upload file to current directory
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(url_for('index', path=rel_path))
        file = request.files['file']
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(url_for('index', path=rel_path))
        filename = secure_filename(file.filename)
        save_path = safe_join(abs_path, filename)
        try:
            file.save(save_path)
            flash(f'File "{filename}" uploaded successfully', 'success')
        except Exception as e:
            flash(f'Failed to upload file: {e}', 'danger')
        return redirect(url_for('index', path=rel_path))

    files = list_dir(rel_path)
    breadcrumbs = get_breadcrumbs(rel_path)

    return render_template('index.html', files=files, path=rel_path, breadcrumbs=breadcrumbs, user=session.get('username'), is_admin=is_admin())

@app.route('/files/<path:filename>')
def files(filename):
    if not is_logged_in():
        return redirect(url_for('login'))
    try:
        abs_file = safe_join(ROOT_DIR, filename)
        dir_name = os.path.dirname(abs_file)
        file_name_only = os.path.basename(abs_file)
        return send_from_directory(directory=dir_name, path=file_name_only, as_attachment=True)
    except Exception:
        abort(404)

@app.route('/delete/<path:filename>', methods=['POST'])
def delete_file(filename):
    if not is_logged_in() or not is_admin():
        flash('Permission denied', 'danger')
        return redirect(url_for('index'))
    try:
        abs_file = safe_join(ROOT_DIR, filename)
        if os.path.isfile(abs_file):
            os.remove(abs_file)
            flash(f'File "{os.path.basename(filename)}" deleted', 'success')
        else:
            flash('File not found', 'danger')
    except Exception as e:
        flash(f'Failed to delete file: {e}', 'danger')
    # Redirect to folder containing the file
    folder_path = os.path.dirname(filename)
    return redirect(url_for('index', path=folder_path))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        if username in USERS and USERS[username] == password:
            session['username'] = username
            flash(f'Welcome, {username}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('login'))

def main():
    app.run(debug=True)

if __name__ == '__main__':
    main()
