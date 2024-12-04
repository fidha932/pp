from flask import Flask,render_template,request,session,redirect,url_for,jsonify
from dbconnection.datamanipulation import *
from datetime import timedelta
import datetime
app=Flask(__name__)

app.secret_key='supersecretkey'
app.permanent_session_lifetime=timedelta(minutes=5)

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/register")
def register():
    return render_template('register.html')

@app.route("/reg",methods=['POST'])
def reg():
    name=request.form['name']
    age=request.form['age']
    address=request.form['address']
    gender=request.form['gender']
    country=request.form['country'] 
    username=request.form['username'] 
    password=request.form['password'] 
    m=sql_edit_insert('INSERT INTO register VALUES(NULL,?,?,?,?,?,?,?)',(name,age,address,gender,country,username,password))
    return redirect(url_for('login'))

@app.route("/login")
def login():
    if 'id' in session:
        return redirect(url_for('log'))
    else:
        return render_template('login.html')

@app.route('/handlelogin',methods=['POST'])
def handlelogin():
    username=request.form['username']
    password=request.form['password']
    m=sql_query2('SELECT * FROM register WHERE username=? and password=?',(username,password))
    if len(m)>0:
        session['userid']=m[0][0]
        print(session['userid'])
        return redirect(url_for('log'))
    else:
        return redirect(url_for('login'))
    
@app.route("/log")
def log():
        return render_template('log.html')
    
@app.route('/logout')
def logout():
    session.clear
    return redirect(url_for('login'))

@app.route('/checkusername')
def checkusername():
    username=request.args.get('user')
    user=sql_query2('SELECT * FROM register WHERE username=?',[username])
    if len(user)>0:
        msg="exist"
    else:
        msg="notexist"
    return jsonify({'valid':msg})

@app.route('/form')
def form():
    return render_template('form.html',uid=session['userid'])

@app.route('/formaction',methods=['POST'])
def formaction():
    userid=request.form['senderid']
    receivername=request.form['receivername']
    m=sql_query2('SELECT * FROM register WHERE username=?',[receivername])
    subject=request.form['subject']
    message=request.form['message']
    receiverid=m[0][0]
    date=datetime.date.today()
    time=datetime.datetime.now().strftime('%H:%M')
    m1=sql_edit_insert('INSERT INTO message VALUES(NULL,?,?,?,?,?,?,?)',(userid,receiverid,subject,message,date,time,'pending'))
    if m1>0:
        msg='send'
    else:
        msg='not send'
    return render_template('form.html',msg=msg)
    
@app.route('/view')
def view():
    v=sql_query2('select register.username,message.* from register inner join message on register.id=message.receiverid where userid=?',[session['userid']])      
    return render_template('view.html',a=v)

@app.route('/delete')
def delete():
    m=request.args.get('uid')
    m1=sql_query2('select * from message where id=?',[m])
    status=m1[0][7]
    if(status=='deleted by receiver'):
        r=sql_edit_insert('delete from message where id=?',[m])
        return redirect(url_for('view'))
    else:
        u=sql_edit_insert('update message set status=? where id=?',('deleted by sender',m))
        return redirect(url_for('view'))

@app.route('/receivermsg')
def receivermsg():
    i=sql_query2('select register.username,message.* from message inner join register on register.id=message.userid where receiverid=?',[session['userid']])
    return render_template('inbox.html',a=i)

@app.route('/trash',methods=['POST'])
def trash():
    date=datetime.date.today()
    time=datetime.datetime.now().strftime('%H:%M')
    check=request.form.getlist('checkbox')
    for mid in check:
        trash=sql_edit_insert('insert into trash values(NULL,?,?,?,?)',(mid,session['userid'],date,time))
    return redirect(url_for('receivermsg'))

@app.route('/trashview')
def trashview():
    t=sql_query2('select register.username,trash.date,trash.time,message.* from(register inner join message on register.id=message.userid)inner join  trash on message.id=trash.msgid where trash.userid=?',[session['userid']])
    return render_template('trash.html',a=t)

@app.route('/deletetrash')
def deletetrash():
    m=request.args.get('uid')
    t=sql_edit_insert('delete from trash where msgid=?',[m])
    m1=sql_query2('select * from message where id=?',[m])
    status=m1[0][7]
    if(status=='deleted by receiver'):
        r=sql_edit_insert('delete from message where receiverid=?',[session['userid']])
        return redirect(url_for('trashview'))
    else:
        u=sql_edit_insert('update message set status=? where id=?',('deleted by receiver',m))
        return redirect(url_for('trashview'))
    
@app.route('/forward')
def forward():
    m=request.args.get('uid')
    sender=session['userid']
    m1=sql_query2('select * from message where id=?',[m])
    return render_template('forward.html',a=m1,uid=sender)

@app.route('/forwardaction',methods=['post'])
def forwardaction():
    sender=request.form['senderid']
    receivername=request.form['receivername']
    m1=sql_query2('SELECT * FROM register WHERE username=?',[receivername])
    subject=request.form['subject']
    message=request.form['message']
    date=datetime.date.today()
    time=datetime.datetime.now().strftime('%H:%M')
    receiverid=m1[0][0]
    m2=sql_edit_insert('INSERT INTO message VALUES(NULL,?,?,?,?,?,?,?)',(sender,receiverid,subject,message,date,time,'pending'))
    if m2>0:
        msg='send'
    else:
        msg='not send'
    return redirect(url_for('view'))

@app.route('/replay')
def replay():
    m=request.args.get('uid')
    data=sql_query2('select register.username,message.userid from register inner join message on register.id=message.userid where message.id=?',[m])
    return render_template('replay.html',a=data)

@app.route('/replayaction',methods=['post'])
def replayaction():
    sender=session['userid']
    receivername=request.form['receivername']
    subject=request.form['subject']
    message=request.form['message']
    date=datetime.date.today()
    time=datetime.datetime.now().strftime('%H:%M')
    m=sql_query2('select * from register where username=?',[receivername])
    receiverid=m[0][0]
    m1=sql_edit_insert('INSERT INTO message VALUES(NULL,?,?,?,?,?,?,?)',(sender,receiverid,subject,message,date,time,'pending'))
    if m1>0:
        msg='send'
    else:
        msg='not send'
    return render_template('replay.html')

@app.route('/update')
def update():
    userid=session['userid']
    m=sql_query2('select * from register where id=?',[userid])
    return render_template('update.html',a=m)

@app.route('/updateaction',methods=['POST'])
def updateaction():
    name=request.form['name']
    age=request.form['age']
    address=request.form['address']
    gender=request.form['gender']
    country=request.form['country'] 
    username=request.form['username'] 
    password=request.form['password']
    id=request.form['id']
    m=sql_edit_insert('update register set name=?,age=?,address=?,gender=?,country=?,username=?,password=? where id=?',[name,age,address,gender,country,username,password,id]) 
    return render_template('index.html',a=m)
    
if __name__ =='__main__':
    app.run(debug=True)