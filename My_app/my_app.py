from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from sendemail import sendmail
import smtplib


app = Flask(__name__)

app.secret_key = 'a'

app.config['MYSQL_HOST'] = 'remotemysql.com'
app.config['MYSQL_USER'] = 'DB_username'
app.config['MYSQL_PASSWORD'] = 'DB_password'
app.config['MYSQL_DB'] = 'DB_name'

mysql = MySQL(app)

@app.route('/')
def homepg():
    return render_template('home.html')

@app.route('/login',methods =['GET', 'POST'])
def login():
    global userid
    msg = ''
    
    if (request.method == 'POST'):
        aadharnum = request.form['aadhar']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE aadhar = % s AND password = % s', (aadharnum, password ),)
        account = cursor.fetchone()
        #print (account)
        if account:
            session['loggedin'] = True
            session['aadhar'] = account[2]
            #fname =  account[0]
            #session['aadhar'] = account[1]
            msg = 'Logged in successfully !'
            return render_template('dashboard.html', msg = msg)
        
        else:
            cursor.execute('SELECT * FROM users WHERE aadhar = % s', (aadharnum, ))
            account1 = cursor.fetchone()
            
            if (account1):
                msg = 'Incorrect password !!'
        
            else:
                msg = 'User is not registered !! Kindly register and then login.'
            
        #elif ((aadharnum == account[0]) and (password != account[1])):
           #msg = 'Incorrect password !'
            
            
    return render_template('login.html', msg = msg)


@app.route('/forgotpwd', methods =['GET', 'POST'])
def forgotpwd():
    msg = ''
    if (request.method == 'POST'):
        
        aadharnum = request.form['aadhar']
        
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE aadhar = % s', (aadharnum, ))
        account = cursor.fetchone()
        #print(account)
        if account:
            password = request.form['password']
            cursor.execute('UPDATE users SET password = %s WHERE aadhar = %s', (password, aadharnum),)
            msg = "Password changed. Kindly login."

        else:
            msg = "AADHAR number is not enrolled !! Kindly register."
        
        mysql.connection.commit()

    #elif request.method == 'POST':
        #msg = 'Please fill out the form !'
    
    return render_template('forgotpwd.html', msg = msg)


@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if (request.method == 'POST'):
        fname = request.form['fname']
        lname = request.form['lname']
        aadharnum = request.form['aadhar']
        email = request.form['email']
        password = request.form['password']
        
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE aadhar = % s', (aadharnum, ))
        account = cursor.fetchone()
        #print(account)
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
#        elif not re.match(r'[A-Za-z0-9]+', username):
            #msg = 'name must contain only characters and numbers !'
        else:
            cursor.execute('INSERT INTO users VALUES (% s, % s, % s, % s, % s)', (fname,lname,aadharnum, email,password))
            mysql.connection.commit()
            msg = 'You have successfully registered !'
            TEXT = "Hello "+fname +" "+lname + ",\n\n"+ """Thanks for registering at RetInvC. """ 
            msg  = '{}: {}'.format("Retail Inventory Management System", TEXT)
            #sendmail(TEXT,email)
            #sendgridmail(email,TEXT)
    #elif request.method == 'POST':
        #msg = 'Please fill out the form !'
    
    return render_template('register.html', msg = msg)


@app.route('/dashboard')
def dashb():
    return render_template('dashboard.html')


@app.route('/request',methods =['GET', 'POST'])
def req_inven():
     msg = ''
     if request.method == 'POST' :
         
         #aadharnum = request.form['aadhar']
         raw_grocer = request.form['raw_groceries']        
         diff_oils= request.form['different_oils']
         package_food = request.form['packaged_food']
         diary_prod = request.form['diary_products']
         biscuits = request.form['biscuits']
         
         #req = request.form['s']
         cursor = mysql.connection.cursor()
         cursor.execute('SELECT * FROM inven WHERE aadhar = % s', (session['aadhar'], ))
         account = cursor.fetchone()
         #print(account)     
         
         cursor = mysql.connection.cursor()
         
         if not account:
             cursor.execute('INSERT INTO inven VALUES (% s, % s, % s, % s,% s, % s)', (session['aadhar'], raw_grocer, diff_oils, package_food, diary_prod, biscuits),)
         else:
             #aadharnum += account[1]
             raw_grocer = str(int(raw_grocer)+account[1])
             diff_oils = str(int(diff_oils)+account[2])
             package_food = str(int(package_food)+account[3])
             diary_prod = str(int(diary_prod)+account[4])
             biscuits = str(int(biscuits)+account[5])
             
             cursor.execute('UPDATE inven SET raw_groceries = % s, different_oils = % s, packaged_food = % s, diary_products = % s, biscuits = % s WHERE aadhar = % s', (raw_grocer, diff_oils, package_food, diary_prod, biscuits, session['aadhar']))
         
         mysql.connection.commit()
         
         msg = 'You have successfully placed your inventory request.'
         session['loggedin'] = True
      
     #elif request.method == 'POST':
         #msg = 'Please fill out the form !'
     return render_template('request.html', msg = msg)


@app.route('/display')
def display():
    #print(session["aadharnum"],session['id'])
    
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM inven WHERE aadhar = % s', (session['aadhar'],))
    account = cursor.fetchone()
    
    cursor1 = mysql.connection.cursor()
    cursor1.execute('SELECT * FROM users WHERE aadhar = % s', (session['aadhar'],))
    account1 = cursor1.fetchone()
    
    #print("item1:",account1[1])
    #print("item2:",account1[2])
    #print("item3:",account1[3])
    #print("item4:",account1[4])
    #print("item5:",account1[5])
    
    if not account:
        #print("in if part...")
        #msg = 'Inventory details for '+account1[0]+" bearing AADHAR: "+ account1[2]+" not found !!"
        return render_template('dashboard.html', msg = "0")
        #return render_template('display.html', msg = msg, account = account)
    else:
        #print("in else part...")
        msg = 'Inventory details for '+account1[0]+" having AADHAR: "+ account1[2]+" is given below."
        hellomsg = "Hello "+account1[0]+", you've 0 qty of following items : \n\n"
        endmesg = "\n Please refill your stock."
        dum = []
        
        for i in range(1,6):
            #print("Value is:", account[i])
            if ((not account[i]) or (account[i] == 0)):
                if (i == 1):
                    #TEXT = "Hello "+account1[0]+", you've 0 qty of " +"raw_groceries"+". Please refill your stock."
                    TEXT = "raw_groceries"
                    dum.append(TEXT)
                elif (i == 2):
                    #TEXT = "Hello "+account1[0]+", you've 0 qty of " +"different_oils"+". Please refill your stock."
                    TEXT = "different_oils"
                    dum.append(TEXT)
                elif (i == 3):
                    #TEXT = "Hello "+account1[0]+", you've 0 qty of " +"packaged_food"+". Please refill your stock."
                    TEXT = "packaged_food"
                    dum.append(TEXT)
                elif (i == 4):
                    #TEXT = "Hello "+account1[0]+", you've 0 qty of " +"diary_products"+". Please refill your stock."  
                    TEXT = "diary_products"
                    dum.append(TEXT)  
                elif (i == 5):
                    #TEXT = "Hello "+account1[0]+", you've 0 qty of " +"biscuits"+". Please refill your stock."
                    TEXT = "biscuits"
                    dum.append(TEXT)
                    
                #sendmail(TEXT,"agupta281091@gmail.com")
        if (len(dum) > 0):        
            #sendmail(finalMessage(hellomsg, endmesg, dum),"agupta281091@gmail.com")
            sendmail(finalMessage(hellomsg, endmesg, dum),account1[3])

        return render_template('display.html',msg = msg, account = account)
    

def finalMessage(hellomsg, endmesg, dum):
    finalMesg = hellomsg
    for i in range(len(dum)):
        finalMesg += str(i+1) + ". " + dum[i] + "\n"
    
    finalMesg += endmesg
    
    return finalMesg
    


@app.route('/logout')

def logout():
   session.pop('loggedin', None)
   #session.pop('id', None)
   session.pop('aadharnum', None)
   return render_template('home.html')


    
if __name__ == '__main__':
    #app.run()
    app.run(host='0.0.0.0', port = 8080)
    #app.run(host='0.0.0.0',debug = True,port = 8080)

