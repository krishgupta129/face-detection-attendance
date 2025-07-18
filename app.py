from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import os
import base64
from database import init_db, save_user, get_all_users, mark_attendance, delete_user_by_id, get_attendance_records, update_user
from face_utils import get_face_encodings, recognize_face_from_encoding

app = Flask(__name__)
app.secret_key = 'supersecretkey'

if not os.path.exists('database'):
    os.makedirs('database')

init_db()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_id = request.form['user_id']
        name = request.form['name']
        phone = request.form['phone']
        image_data = request.form['image_data']

        if not image_data:
            flash("Please capture a face image before submitting!")
            return redirect(url_for('register'))

        image_data = image_data.split(',')[1]
        image_bytes = base64.b64decode(image_data)

        encodings = get_face_encodings(image_bytes)
        if not encodings:
            flash("No face detected in the image, please try again.")
            return redirect(url_for('register'))

        save_user(user_id, name, phone, encodings[0])
        flash("User registered successfully!")
        return redirect(url_for('register'))

    return render_template('register.html')

@app.route('/recognize')
def recognize():
    return render_template('recognize.html')

@app.route('/recognize_face', methods=['POST'])
def recognize_face():
    data = request.get_json()
    image_data = data.get('image')

    if not image_data:
        return jsonify({'status': 'fail', 'message': 'No image data received'})

    image_data = image_data.split(',')[1]
    image_bytes = base64.b64decode(image_data)
    unknown_encodings = get_face_encodings(image_bytes)

    if not unknown_encodings:
        return jsonify({'status': 'fail', 'message': 'No face detected'})

    users = get_all_users()
    user_found = recognize_face_from_encoding(unknown_encodings[0], users)

    if user_found:
        user_id, name = user_found
        mark_attendance(user_id, name)
        return jsonify({'status': 'success', 'name': name, 'user_id': user_id})
    else:
        return jsonify({'status': 'fail', 'message': 'Face not recognized'})

@app.route('/dashboard')
def dashboard():
    users = get_all_users()
    attendance_records = get_attendance_records()
    return render_template('dashboard.html', users=users, records=attendance_records)

@app.route('/delete_user/<user_id>', methods=['POST'])
def delete_user(user_id):
    delete_user_by_id(user_id)
    flash(f"User {user_id} deleted.")
    return redirect(url_for('dashboard'))

@app.route('/edit_user', methods=['POST'])
def edit_user():
    user_id = request.form['edit_user_id']
    name = request.form['edit_name']
    phone = request.form['edit_phone']
    update_user(user_id, name, phone)
    flash(f"User {user_id} updated.")
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
