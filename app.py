from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import MySQLdb.cursors, re, hashlib
import NTRU2

app = Flask(__name__)

# Change this to your secret key (it can be anything, it's for extra protection)
app.secret_key = 'your secret key'

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '@Koenokatachi18'
app.config['MYSQL_DB'] = 'geeklogin'

# Intialize MySQL
mysql = MySQL(app)

@app.route('/', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        #enc_username = NTRU2.encrypt("test", username)
        password = request.form['password']
        # Retrieve the hashed password
        hash = password + app.secret_key
        hash = hashlib.sha1(hash.encode())
        password = hash.hexdigest()

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
        # Fetch one record and return the result
        account = cursor.fetchone()

         # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            session['first_name'] = account['first_name']
            # Redirect to home page
            return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    return render_template('index.html', msg='')

@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username'] #request.form['username']
        password = request.form['password']
        email = request.form['email']
        birthday_month = request.form['birthday_month']
        birthday_day = request.form['birthday_day']
        birthday_year = request.form['birthday_year'] 
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        middle_name = request.form['middle_name']

        enc_email = NTRU2.encrypt("test", email) #request.form['email']
        enc_birthday_month = NTRU2.encrypt("test", birthday_month)
        enc_birthday_day = NTRU2.encrypt("test", birthday_day)
        enc_birthday_year = NTRU2.encrypt("test", birthday_year)
        enc_first_name = NTRU2.encrypt("test", first_name)
        enc_last_name = NTRU2.encrypt("test", last_name)
        enc_middle_name = NTRU2.encrypt("test", middle_name)
        

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', NTRU2.decrypt("test", enc_email)):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        elif 'password' in request.form and 'confirm_password' in request.form:
                password = request.form['password']
                confirm_password = request.form['confirm_password']
                if password and confirm_password:
                    if password != confirm_password:
                        return render_template('register.html', msg='Passwords do not match')
                    else:
                        hash = password + app.secret_key
                        hash = hashlib.sha1(hash.encode())
                        password = hash.hexdigest()
                        values = (username, password, enc_email, first_name, middle_name, last_name, birthday_month, birthday_day, birthday_year)
                        cursor.execute('INSERT INTO accounts (id, username, password, email, first_name, middle_name, last_name, birthday_month, birthday_day, birthday_year) VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s)', 
                                       (username, password, enc_email, enc_first_name, enc_middle_name, enc_last_name, enc_birthday_month, enc_birthday_day, enc_birthday_year, ))
                        mysql.connection.commit()
                        msg = 'You have successfully registered! You can now login!'
                        return render_template('index.html')
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)

@app.route('/home')
def home():
    # Check if the user is logged in
    if 'loggedin' in session:
        # User is loggedin show them the home page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        account['first_name'] = NTRU2.decrypt("test", account['first_name'])
        return render_template('home.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/profile')
def profile():
    # Check if the user is logged in
    
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()

        account['email'] = NTRU2.decrypt("test", account['email'])
        account['first_name'] = NTRU2.decrypt("test", account['first_name'])
        account['middle_name'] = NTRU2.decrypt("test", account['middle_name'])        
        account['last_name'] = NTRU2.decrypt("test", account['last_name'])
        account['birthday_month'] = NTRU2.decrypt("test", account['birthday_month'])
        account['birthday_day'] = NTRU2.decrypt("test", account['birthday_day'])
        account['birthday_year'] = NTRU2.decrypt("test", account['birthday_year'])


        if account['PCN'] is not None:
            account['PCN'] = NTRU2.decrypt("test", account['PCN'])
        else:
            account['PCN'] = None

        if account['house_number'] is not None:
            account['house_number'] = NTRU2.decrypt("test", account['house_number'])
        else:
            account['house_number'] = None

        if account['street'] is not None:
            account['street'] = NTRU2.decrypt("test", account['street'])
        else:
            account['street'] = None

        if account['barangay'] is not None:
            account['barangay'] = NTRU2.decrypt("test", account['barangay'])
        else:
            account['barangay'] = None

        if account['city'] is not None:
            account['city'] = NTRU2.decrypt("test", account['city'])
        else:
            account['city'] = None

        if account['province'] is not None:
            account['province'] = NTRU2.decrypt("test", account['province'])
        else:
            account['province'] = None

        if account['sex'] is not None:
            account['sex'] = NTRU2.decrypt("test", account['sex'])
        else:
            account['sex'] = None

        if account['blood_type'] is not None:
            account['blood_type'] = NTRU2.decrypt("test", account['blood_type'])
        else:
            account['blood_type'] = None

        if account['marital_status'] is not None:
            account['marital_status'] = NTRU2.decrypt("test", account['marital_status'])
        else:
            account['marital_status'] = None

        if account['place_of_birth'] is not None:
            account['place_of_birth'] = NTRU2.decrypt("test", account['place_of_birth'])
        else:
            account['place_of_birth'] = None
            
          
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not logged in redirect to login page
    return redirect(url_for('login'))

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    # Check if the user is logged in
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        account['email'] = NTRU2.decrypt("test", account['email'])
        account['first_name'] = NTRU2.decrypt("test", account['first_name'])
        account['middle_name'] = NTRU2.decrypt("test", account['middle_name'])        
        account['last_name'] = NTRU2.decrypt("test", account['last_name'])
        account['birthday_month'] = NTRU2.decrypt("test", account['birthday_month'])
        account['birthday_day'] = NTRU2.decrypt("test", account['birthday_day'])
        account['birthday_year'] = NTRU2.decrypt("test", account['birthday_year'])
        
        if account['PCN'] is not None:
            account['PCN'] = NTRU2.decrypt("test", account['PCN'])
        else:
            account['PCN'] = None

        if account['house_number'] is not None:
            account['house_number'] = NTRU2.decrypt("test", account['house_number'])
        else:
            account['house_number'] = None

        if account['street'] is not None:
            account['street'] = NTRU2.decrypt("test", account['street'])
        else:
            account['street'] = None

        if account['barangay'] is not None:
            account['barangay'] = NTRU2.decrypt("test", account['barangay'])
        else:
            account['barangay'] = None

        if account['city'] is not None:
            account['city'] = NTRU2.decrypt("test", account['city'])
        else:
            account['city'] = None

        if account['province'] is not None:
            account['province'] = NTRU2.decrypt("test", account['province'])
        else:
            account['province'] = None

        if account['sex'] is not None:
            account['sex'] = NTRU2.decrypt("test", account['sex'])
        else:
            account['sex'] = None

        if account['blood_type'] is not None:
            account['blood_type'] = NTRU2.decrypt("test", account['blood_type'])
        else:
            account['blood_type'] = None

        if account['marital_status'] is not None:
            account['marital_status'] = NTRU2.decrypt("test", account['marital_status'])
        else:
            account['marital_status'] = None

        if account['place_of_birth'] is not None:
            account['place_of_birth'] = NTRU2.decrypt("test", account['place_of_birth'])
        else:
            account['place_of_birth'] = None

        if request.method == 'POST':

            if 'username' in request.form:
                username = request.form['username']
                if username:
                    cursor.execute('UPDATE accounts SET username = %s WHERE id = %s', (username, session['id']))
            
            if 'email' in request.form:
                email = request.form['email']
                if email:
                    if not re.match(r'[^@]+@(gmail\.com|yahoo\.com|plm\.edu\.ph)$', email):
                        return render_template('edit.html', error='Invalid email address!') 
                    elif email:
                        enc_email = NTRU2.encrypt("test", email)
                        cursor.execute('UPDATE accounts SET email = %s WHERE id = %s', (enc_email, session['id']))
            
            if 'password' in request.form and 'confirm_password' in request.form:
                password = request.form['password']
                confirm_password = request.form['confirm_password']
                if password and confirm_password:
                    if password != confirm_password:
                        return render_template('edit.html', error='Passwords do not match')
                    else:
                        hash = password + app.secret_key
                        hash = hashlib.sha1(hash.encode())
                        password = hash.hexdigest()
                        cursor.execute('UPDATE accounts SET password = %s WHERE id = %s', (password, session['id']))
            
            if 'birthday_month' in request.form and 'birthday_day' in request.form and 'birthday_year' in request.form:
                birthday_month = request.form['birthday_month']
                birthday_day = request.form['birthday_day']
                birthday_year = request.form['birthday_year']
                if birthday_month and birthday_day and birthday_year:
                    enc_birthday_month = NTRU2.encrypt("test", birthday_month)
                    enc_birthday_day = NTRU2.encrypt("test", birthday_day)
                    enc_birthday_year = NTRU2.encrypt("test", birthday_year)
                    cursor.execute('UPDATE accounts SET birthday_month = %s, birthday_day = %s, birthday_year = %s WHERE id = %s', (enc_birthday_month, enc_birthday_day, enc_birthday_year, session['id']))
            
            if 'house_number' in request.form and 'street' in request.form and 'barangay' in request.form and 'city' in request.form and 'province' in request.form:
                house_number = request.form['house_number']
                street = request.form['street']
                barangay = request.form['barangay']
                city = request.form['city']
                province = request.form['province']

                enc_house_number = NTRU2.encrypt("test", house_number)
                enc_street = NTRU2.encrypt("test", street)
                enc_barangay = NTRU2.encrypt("test", barangay)
                enc_city = NTRU2.encrypt("test", city)
                enc_province = NTRU2.encrypt("test", province)

                if house_number and street and barangay and city and province:
                    cursor.execute('UPDATE accounts SET house_number = %s, street = %s, barangay = %s, city = %s, province = %s WHERE id = %s', (enc_house_number, enc_street, enc_barangay, enc_city, enc_province, session['id']))
            
            if 'pcn' in request.form:
                pcn = request.form['pcn']
                if pcn:
                    enc_pcn = NTRU2.encrypt("test", pcn)
                    cursor.execute('UPDATE accounts SET PCN = %s WHERE id = %s', (enc_pcn, session['id']))

            if 'sex' in request.form:
                sex = request.form['sex']
                if sex:
                    enc_sex = NTRU2.encrypt("test", sex)
                    cursor.execute('UPDATE accounts SET sex = %s WHERE id = %s', (enc_sex, session['id']))

            if 'blood_type' in request.form:
                blood_type = request.form['blood_type']
                if blood_type:
                    enc_blood_type = NTRU2.encrypt("test", blood_type)
                    cursor.execute('UPDATE accounts SET blood_type = %s WHERE id = %s', (enc_blood_type, session['id']))

            if 'marital_status' in request.form:
                marital_status = request.form['marital_status']
                if marital_status:
                    enc_marital_status = NTRU2.encrypt("test", marital_status)
                    cursor.execute('UPDATE accounts SET marital_status = %s WHERE id = %s', (enc_marital_status, session['id']))

            if 'place_of_birth' in request.form:
                place_of_birth = request.form['place_of_birth']
                if place_of_birth:
                    enc_place_of_birth = NTRU2.encrypt("test", place_of_birth)
                    cursor.execute('UPDATE accounts SET place_of_birth = %s WHERE id = %s', (enc_place_of_birth, session['id']))
            
            mysql.connection.commit()
            return redirect(url_for('profile'))
        return render_template('edit.html', account=account)
    return redirect(url_for('login'))

@app.route('/enc_profile')
def enc_profile():
    # Check if the user is logged in
    
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()

        account['email'] = account['email']
        account['first_name'] =account['first_name']
        account['middle_name'] = account['middle_name']   
        account['last_name'] = account['last_name']
        account['birthday_month'] = account['birthday_month']
        account['birthday_day'] = account['birthday_day']
        account['birthday_year'] = account['birthday_year']


        if account['PCN'] is not None:
            account['PCN'] = account['PCN']
        else:
            account['PCN'] = None

        if account['house_number'] is not None:
            account['house_number'] = account['house_number']
        else:
            account['house_number'] = None

        if account['street'] is not None:
            account['street'] = account['street']
        else:
            account['street'] = None

        if account['barangay'] is not None:
            account['barangay'] = account['barangay']
        else:
            account['barangay'] = None

        if account['city'] is not None:
            account['city'] = account['city']
        else:
            account['city'] = None

        if account['province'] is not None:
            account['province'] = account['province']
        else:
            account['province'] = None

        if account['sex'] is not None:
            account['sex'] = account['sex']
        else:
            account['sex'] = None

        if account['blood_type'] is not None:
            account['blood_type'] = account['blood_type']
        else:
            account['blood_type'] = None

        if account['marital_status'] is not None:
            account['marital_status'] = account['marital_status']
        else:
            account['marital_status'] = None

        if account['place_of_birth'] is not None:
            account['place_of_birth'] = account['place_of_birth']
        else:
            account['place_of_birth'] = None
            
          
        # Show the profile page with account info
        return render_template('enc_profile.html', account=account)
    # User is not logged in redirect to login page
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)