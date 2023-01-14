import io
import random
import time

import matplotlib.pyplot as plt
import pypyodbc
from flask import Response, flash, redirect, render_template, request
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

import db_connection as con
from app import app
from record_tables import record_results
from user_tables import user_results


@app.route('/new_user')
def add_user_view():
	return render_template('add.html')
	
@app.route('/add', methods=['POST'])
def add_user():
	conn = None
	cursor = None
	try:
		_id = request.form['inputId']		
		_name = request.form['inputName']
		_sex = request.form['SelectSex']
		_password = request.form['inputPassword']
		_phone_number = request.form['inputPhoneNumber']
		_birth = request.form['inputBirthday']
		_number = request.form['inputAccountNumber']
		_balance = request.form['inputMoney']

		if _id and _name and _sex and _password and _phone_number and _birth and _number and request.method == 'POST':
			conn = con.getConnection()
			#users
			cursor = conn.cursor()
			sql = "INSERT INTO users(id, name , sex, birth, phone_number) VALUES(?, ?, ?, ?, ?)"
			cursor.execute(sql, [_id,_name,_sex,_birth,_phone_number])
			cursor = None

			#accounts
			cursor = conn.cursor()
			sql = 'INSERT INTO accounts(id,number,password,balance) VALUES(?,?,?,?)'
			cursor.execute(sql,[_id,_number,_password,_balance])
			cursor = None

			#cards
			cursor = conn.cursor()
			sql = 'INSERT INTO cards(number,card_id) VALUES(?,?)'
			cursor.execute(sql,[_number,'1'])
			sql = 'INSERT INTO cards(number,card_id) VALUES(?,?)'
			cursor.execute(sql,[_number,'2'])		
			cursor = None			

			#records
			cursor = conn.cursor()
			localtime = time.asctime(time.localtime(time.time()))
			sql = 'INSERT INTO records(number,card,time,abstract,amount,balance_before,balance_after) VALUES(?,?,?,?,?,?,?)'
			cursor.execute(sql,[_number,'1',str(localtime),'开户',_balance,0,_balance])
			conn.commit()

			return redirect('/')
		else:
			return 'Error while adding user'

	except Exception:
		return 'error'
	finally:
		conn.close()
		
@app.route('/')
def users():
	conn = None
	cursor = None
	try:
		conn = con.getConnection()
		cursor = conn.cursor()
		cursor.execute("SELECT * FROM users")
		rows = cursor.fetchall()
		table = user_results(rows)
		table.border = True
		return render_template('users.html', table=table)
	except Exception:
		return 'error'
	finally:
		conn.close()

@app.route('/edit/<int:id>')
def edit_view(id):
	conn = None
	cursor = None
	try:
		conn = con.getConnection()
		cursor = conn.cursor()
		cursor.execute("SELECT * FROM accounts WHERE id = ?", [id])
		row = cursor.fetchone()
		if row:
			return render_template('edit.html', row=row)
		else:
			return 'Error loading #{id}'.format(id=id)
	except Exception:
		return 'error'
	finally:
		conn.close()

@app.route('/update', methods=['POST'])
def update_user():
	conn = None
	cursor = None
	try:		
		_id = request.form['inputId']
		_number = request.form['inputAccountNumber']
		_cardid = request.form['inputCardID']
		_password = request.form['inputPassword']
		_action = request.form['inputAction']
		_money = request.form['inputMoney']
		_other_number  = request.form['inputOtherAccountNumber']

		#获取密码和当前余额
		conn = con.getConnection()
		cursor = conn.cursor()
		cursor.execute('SELECT password,balance FROM accounts WHERE id = ?',[_id])
		row = cursor.fetchone()
		pw = row[0]
		bl = row[1]
		cursor = None

		if request.method == 'POST' and pw == _password:
			if _action == '存款':
				current_balance = float(bl) + float(_money) 

				#更新账户余额
				sql = "UPDATE accounts SET balance = ? WHERE id = ?"
				cursor = conn.cursor()
				cursor.execute(sql, [current_balance,_id])
				cursor = None

				#更新交易历史
				localtime = time.asctime(time.localtime(time.time()))
				sql = "INSERT INTO records(number,card,time,abstract,amount,balance_before,balance_after) VALUES (?,?,?,?,?,?,?)"
				cursor = conn.cursor()
				cursor.execute(sql,[_number,_cardid,str(localtime),'存款',_money,bl,current_balance])

				conn.commit()
				flash('存款成功')
			elif _action == '取款':
				current_balance = float(bl) - float(_money) 
				if current_balance < 0:
					return '账户余额不足'
				#更新账户余额
				sql = "UPDATE accounts SET balance = ? WHERE id = ?"
				cursor = conn.cursor()
				cursor.execute(sql, [current_balance,_id])
				cursor = None
				
				#更新交易历史
				localtime = time.asctime(time.localtime(time.time()))
				sql = "INSERT INTO records(number,card,time,abstract,amount,balance_before,balance_after) VALUES (?,?,?,?,?,?,?)"
				cursor = conn.cursor()
				cursor.execute(sql,[_number,_cardid,str(localtime),'取款',_money,bl,current_balance])
				conn.commit()
				flash('取款成功')
			elif _action ==  '转款':
				#查询对方账户余额
				cursor = conn.cursor()
				sql = 'SELECT balance FROM accounts WHERE number = ?'
				cursor.execute(sql,[_other_number])
				row = cursor.fetchone()
				bl2 = row[0]
				cursor = None

				#更新转出账户余额
				current_balance1 = float(bl) - float(_money) 
				if current_balance1 < 0:
					return '账户余额不足'
				sql = "UPDATE accounts SET balance = ? WHERE id = ?"
				cursor = conn.cursor()
				cursor.execute(sql, [current_balance1,_id])
				cursor = None

				#更新转出交易历史
				localtime = time.asctime(time.localtime(time.time()))
				sql = "INSERT INTO records(number,card,time,abstract,other_number,amount,balance_before,balance_after) VALUES (?,?,?,?,?,?,?,?)"
				cursor = conn.cursor()
				cursor.execute(sql,[_number,_cardid,str(localtime),'转出',_other_number,_money,bl,current_balance1])
				cursor = None

				#更新转入账户余额
				current_balance2 = float(bl2) + float(_money)
				sql = "UPDATE accounts SET balance = ? WHERE number = ?"
				cursor = conn.cursor()
				cursor.execute(sql, [current_balance2,_other_number])
				cursor = None

				#更新转入交易历史
				localtime = time.asctime(time.localtime(time.time()))
				sql = "INSERT INTO records(number,card,time,abstract,other_number,amount,balance_before,balance_after) VALUES (?,?,?,?,?,?,?,?)"
				cursor = conn.cursor()
				cursor.execute(sql,[_other_number,'1',str(localtime),'转入',_number,_money,bl2,current_balance2])

				conn.commit()
				flash('转款成功')
			else:
				return 'WrongAction'
			return redirect('/')
		else:
			return 'Please Check your Password'
	#except Exception:
		#return 'error'
	finally:
		conn.close()
		
@app.route('/delete/<int:id>')
def delete_user(id):
	conn = None
	cursor = None
	try:
		conn = con.getConnection()
		cursor = conn.cursor()
		cursor.execute("SELECT * FROM accounts WHERE id = ?", [id])
		row = cursor.fetchone()
		if row:
			return render_template('del.html', row=row)
		else:
			return 'Error loading #{id}'.format(id=id)
	except Exception:
		return 'error'
	finally:
		conn.close()

@app.route('/check_delete',methods=['POST'])
def check_delete():
	conn = None
	cursor = None
	try :
		_id = request.form['inputId']
		_pw = request.form['inputPassword']

		conn = con.getConnection()
		cursor = conn.cursor()
		cursor.execute('SELECT password FROM accounts WHERE id = ?',[_id])
		row = cursor.fetchone()
		pw = row[0]
		cursor = None

		if pw == _pw:
			cursor = conn.cursor()
			cursor.execute('SELECT number,balance FROM accounts WHERE id = ?',[_id])
			row = cursor.fetchone()
			_number = row[0]
			_balance = row[1]
			cursor = None

			if _balance > 0:
				return '请先取出您的存款'

			#users
			cursor = conn.cursor()
			cursor.execute("DELETE FROM users WHERE id = ?", [_id])
			cursor = None

			#accounts
			cursor = conn.cursor()
			cursor.execute("DELETE FROM accounts WHERE id = ?", [_id])
			cursor = None

			#cards
			cursor = conn.cursor()
			cursor.execute("DELETE FROM cards WHERE number = ?", [_number])
			cursor = None	

			#records
			cursor = conn.cursor()
			localtime = time.asctime(time.localtime(time.time()))
			sql = 'INSERT INTO records(number,card,time,abstract) VALUES(?,?,?,?)'
			cursor.execute(sql,[_number,'1',str(localtime),'销户'])

			conn.commit()
			flash('销户成功')
			return redirect('/')
		else:
			return 'WrongPassword'
	except Exception:
		return 'error'
	finally:
		conn.close()

@app.route('/query/<int:id>')
def query(id):
	conn = None
	cursor = None
	try:
		conn = con.getConnection()
		cursor = conn.cursor()
		cursor.execute("SELECT * FROM accounts WHERE id = ?", [id])
		row = cursor.fetchone()
		if row:
			return render_template('query.html', row=row)
		else:
			return 'Error loading #{id}'.format(id=id)
	except Exception:
		return 'error'
	finally:
		conn.close()

@app.route('/check_query',methods=['POST'])
def check_query():
	conn = None
	cursor = None
	try:
		_id = request.form['inputId']
		_pw = request.form['inputPassword']

		conn = con.getConnection()
		cursor = conn.cursor()
		cursor.execute('SELECT number,password FROM accounts WHERE id = ?',[_id])
		row = cursor.fetchone()
		nb = row[0]
		pw = row[1]

		sql = "SELECT SUM(amount) FROM records WHERE abstract = '转出' and number = ?"
		cursor.execute(sql,[nb])
		row = cursor.fetchone()
		out_value = row[0]

		sql = "SELECT SUM(amount) FROM records WHERE abstract = '转入' and number = ?"
		cursor.execute(sql,[nb])
		row = cursor.fetchone()
		in_value = row[0]

		if _pw == pw:
			cursor = conn.cursor()
			cursor.execute("SELECT * FROM records WHERE number = ?",[nb])
			rows = cursor.fetchall()
			table = record_results(rows)
			table.border = True
			return render_template('query_show.html', table=table, number=nb, inVal=in_value, outVal=out_value)
		else:
			return 'WrongPassword'
	except Exception:
		return 'error'
	finally:
		conn.close()

@app.route("/balances-<int:number>.png")
def plot_png(number): 
	conn = None
	cursor = None

	conn = con.getConnection()
	cursor = conn.cursor()

	time_list = []
	balance_list = []
	sql = 'SELECT time,balance_after FROM records WHERE number = ?'
	with cursor.execute(sql,[number]):
		row = cursor.fetchone()
		while row:
			time_list.append(row[0])
			balance_list.append(row[1])
			row = cursor.fetchone()

	fig = Figure()
	axis = fig.add_subplot(1, 1, 1)
	axis.plot(time_list,balance_list)
	axis.set_xlabel('operation number')
	axis.set_ylabel('balance_after')
	axis.set_title('operation records')
	output = io.BytesIO()
	FigureCanvasAgg(fig).print_png(output)
	return Response(output.getvalue(), mimetype="image/png")

@app.route('/query_user')
def query_user_view():
	conn = None
	cursor = None
	conn = con.getConnection()
	cursor = conn.cursor()

	cursor.execute("SELECT * FROM records")
	rows = cursor.fetchall()
	table = record_results(rows)
	table.border = True

	sql = "SELECT name FROM users WHERE id = (SELECT id FROM accounts WHERE balance = (SELECT MAX(balance) FROM accounts))"
	cursor.execute(sql)
	row = cursor.fetchone()
	name = row[0]

	sql = "SELECT SUM(amount) FROM records WHERE abstract in ('开户','存款','取款','转入')"
	cursor.execute(sql)
	row = cursor.fetchone()
	amount = row[0]

	return render_template('query_user.html',table=table,name=name,amount=amount)

@app.route("/number-of-users.png")
def plot_png_users(): 
	conn = None
	cursor = None

	conn = con.getConnection()
	cursor = conn.cursor()

	num = 0
	number_list = []
	sql = "SELECT abstract FROM records WHERE abstract in ('开户','销户')"
	with cursor.execute(sql):
		row = cursor.fetchone()
		while row:
			abstract = row[0].strip()
			if abstract == '开户':
				num = num + 1
				number_list.append(num)
			elif abstract == '销户':
				num = num - 1
				number_list.append(num)
			row = cursor.fetchone()

	fig = Figure()
	axis = fig.add_subplot(1, 1, 1)
	axis.plot(number_list)
	axis.set_xticks(range(1,len(number_list)))
	axis.set_yticks(number_list)
	axis.set_ylabel('number_of_users')
	axis.set_title('the variation of number of users')
	output = io.BytesIO()
	FigureCanvasAgg(fig).print_png(output)
	return Response(output.getvalue(), mimetype="image/png")

if __name__ == "__main__":
    app.run()