from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
import subprocess
import os
import mysql.connector

app = Flask(_name_)
app.secret_key = 'your_secret_key'  # Needed for sessions

# Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="your_mysql_password",  # Change this to your actual MySQL password
    database="ssh_files"
)
cursor = conn.cursor()

# Store command history
command_history = []

@app.route('/')
def home():
    if 'username' in session:
        return render_template('index.html')
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = ''
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == '1234':
            session['username'] = request.form['username']
            return redirect(url_for('home'))
        else:
            error = 'Invalid credentials. Try again.'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/execute', methods=['POST'])
def execute():
    command = request.json.get('command')
    try:
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        result = output.decode()
    except Exception as e:
        result = str(e)

    command_history.append({"command": command, "result": result})
    return {'output': result}

@app.route('/history')
def history():
    return render_template('history.html', history=command_history)

@app.route('/clear_history')
def clear_history():
    command_history.clear()
    return redirect(url_for('history'))

@app.route('/files')
def files():
    cursor.execute("SELECT filename FROM files")
    file_list = cursor.fetchall()
    return render_template('files.html', files=[f[0] for f in file_list])

@app.route('/upload', methods=['POST'])
def upload():
    uploaded_file = request.files['file']
    if uploaded_file.filename != '':
        file_path = os.path.join('/media/sf_SimulatedSSHWeb', uploaded_file.filename)
        uploaded_file.save(file_path)
        cursor.execute("INSERT INTO files (filename) VALUES (%s)", (uploaded_file.filename,))
        conn.commit()
    return redirect(url_for('files'))

@app.route('/download/<filename>')
def download(filename):
    file_path = f"/media/sf_SimulatedSSHWeb/{filename}"
    if os.path.exists(file_path):
        return send_from_directory(directory="/media/sf_SimulatedSSHWeb", path=filename, as_attachment=True)
    return "File not found", 404

if _name_ == '_main_':
    app.run(host="0.0.0.0", port=5000)
