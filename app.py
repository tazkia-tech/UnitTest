from flask import Flask, request, render_template, jsonify, redirect, url_for
from auth.logic_login_register import register_user, login_user

app = Flask(__name__)


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.form
        username = data.get('username')
        password = data.get('password')
        success, message = login_user(username, password)
        if success:
            return jsonify({"message": "Login berhasil!"})
        else:
            return jsonify({"error": message}), 401
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.form
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        success, message = register_user(username, email, password)
        if success:
            return jsonify({"message": "Registrasi berhasil!"})
        else:
            return jsonify({"error": message}), 400
    return render_template('register.html')


if __name__ == '__main__':
    app.run(debug=True)
