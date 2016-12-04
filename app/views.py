#views.py
from app import app
from flask import render_template, request
import mysql.connector
from mysql.connector import errorcode

#Render Staff Options
@app.route('/')
def index():
	return render_template("index.html")
@app.route('/backend')
def staff():
	return render_template("staff.html")

@app.route('/movieoptions')
def movieops():
	return render_template("movieoptions.html")

@app.route('/genreoptions')
def genreops():
	return render_template("genreoptions.html")

@app.route('/roomoptions')
def roomops():
	return render_template("roomoptions.html")

@app.route('/showoptions')
def showops():
	return render_template("showoptions.html")
@app.route('/custoptions')
def custops():
	return render_template("customeroptions.html")
@app.route('/attendoptions')
def attops():
	return render_template("attendoptions.html")

#ATTENDS
#List all attends
@app.route("/allattends", methods=['GET'])    
def allAttends():
	cnx = mysql.connector.connect(user='root', host='127.0.0.1', database='MovieTheatre')
	cursor = cnx.cursor()  
	cursor.execute("select FirstName, LastName, attendmovieshowing.idShowing as ShowingID, attendmovieshowing.showingDate as ShowingDate, attendmovieshowing.idMovie as MovieID, attendmovieshowing.MovieName as MovieName, attendmovieshowing.Rating as Rating from Customer join (select Attend.Rating, Attend.Customer_idCustomer as custID, movieshowing.* from Attend join (select idShowing, DATE_FORMAT(ShowingDateTime,'%b %d %Y %h:%i %p') as showingDate, idMovie, MovieName from Showing join Movie on Showing.Movie_idMovie = Movie.idMovie) as movieshowing on Attend.Showing_idShowing = movieshowing.idShowing) as attendmovieshowing on Customer.idCustomer = attendmovieshowing.custID;")
	output = cursor.fetchall()
	cursor.close()
	cnx.close()
	return render_template("attendoptions.html", output=output)


#MOVIES
#List all movies and attributes alphabetically 
@app.route("/allmov", methods=['GET'])    
def allMov():
	cnx = mysql.connector.connect(user='root', host='127.0.0.1', database='MovieTheatre')
	cursor = cnx.cursor()  
	cursor.execute("select * from Movie ORDER BY MovieName")
	output = cursor.fetchall()
	cursor.close()
	cnx.close()
	return render_template("allmov.html", movies=output)

#Add a movie
@app.route("/addmov", methods=['GET','POST'])    
def addMov():
	cnx = mysql.connector.connect(user='root', host='127.0.0.1', database='MovieTheatre')
	cursor = cnx.cursor()
	try:
		movname = request.form['moviename']
		movyear = request.form['movieyear']
		cursor.execute("INSERT INTO Movie(MovieName,MovieYear) VALUES (%s,%s)",(movname,movyear))
		message = "Added Movie"
	except Exception as e:
	   message = str(e)
	#commit the change
	cnx.commit()
	cursor.execute("select * from Movie")  
	output = cursor.fetchall() 
	cursor.close()
	cnx.close()
	return render_template("allmov.html", movies=output, message = message)

#Delete a movie: ID or movie name and year required.
@app.route("/delmov", methods=['GET','POST'])    
def delMov():
	cnx = mysql.connector.connect(user='root', host='127.0.0.1', database='MovieTheatre')
	cursor = cnx.cursor()
	try:
		movid = request.form['movieID']
		movname = request.form['moviename']
		movyear = request.form['movieyear']
		if movid != "":
			cursor.execute("DELETE FROM Movie WHERE idMovie = '%s'"%(movid))
			message = "Deleted Movie"
			#Cannot delete a row with just movie name and no ID or year, in case that there are movies with the same name
			#but produced in different years
		elif movid == "" and movname != "" and movyear != "":
			cursor.execute("DELETE FROM Movie WHERE MovieName = '%s' AND MovieYear = '%s'"%(movname,movyear))
			message = "Deleted Movie"
		else:
			message = "Please enter movie ID, or movie name and year to delete a movie. Just entering the name or just the year is not enough!"
	except Exception as e:
	   message = str(e)
	#commit the change
	cnx.commit()
	cursor.execute("select * from Movie")  
	output = cursor.fetchall() 
	cursor.close()
	cnx.close()
	return render_template("allmov.html", movies=output, message = message)

#GENRES
#Modify movie: Add a genre.
@app.route("/addgen", methods=['GET','POST'])    
def addGen():
	cnx = mysql.connector.connect(user='root', host='127.0.0.1', database='MovieTheatre')
	cursor = cnx.cursor()
	try:
		movid = request.form['movieID']
		movname = request.form['moviename']
		movyear = request.form['movieyear']
		genre = request.form['genre']
		print(movid,movname,movyear,genre)
		if movid != "":
			cursor.execute("INSERT INTO Genre(Genre,Movie_idMovie) VALUES('%s','%s') ON DUPLICATE KEY UPDATE Movie_idMovie = Movie_idMovie"%(genre,movid))
			message = ("Added genre: %s to Movie ID %s" %(genre,movid))
			#Cannot update a movie with just movie name and no ID or year, in case that there are movies with the same name
			#but produced in different years
		elif movid == "" and movname != "" and movyear != "":
			try:
				cursor.execute("SELECT idMovie from Movie WHERE MovieName = '%s' AND MovieYear = %s"%(movname,movyear))
				movidfound = cursor.fetchone()[0]
				cursor.execute("INSERT INTO Genre(Genre,Movie_idMovie) VALUES('%s',%s) ON DUPLICATE KEY UPDATE Movie_idMovie = Movie_idMovie"%(genre,movidfound))
				message = ("Added genre %s to movie %s with movie ID %s " %(genre,movname,movidfound))
			except Exception as MovieDoesNotExist:
				message = ("Movie Does Not Exist")
		else:
			message = ("Please enter movie ID, or movie name and year to modify a movie. Just entering the name is not enough!")
	except Exception as e:
	   message = str(e)
	#commit the change
	cnx.commit()
	cursor.execute("select idMovie, MovieName, Genre from Genre inner join Movie on Movie_idMovie = idMovie order by idMovie")
	output = cursor.fetchall() 
	cursor.close()
	cnx.close()
	return render_template("allgen.html", table=output, message = message)

#Modify Movie: Delete Genre
@app.route("/delgen", methods=['GET','POST'])    
def delGen():
	cnx = mysql.connector.connect(user='root', host='127.0.0.1', database='MovieTheatre')
	cursor = cnx.cursor()
	try:
		movid = request.form['movieID']
		movname = request.form['moviename']
		movyear = request.form['movieyear']
		genre = request.form['genre']
		if movid != "":
			cursor.execute("DELETE FROM Genre WHERE Genre = '%s' AND Movie_idMovie = '%s'"%(genre,movid))
			message = ("Deleted genre %s from Movie ID %s" %(genre,movid))
			#Cannot update a movie with just movie name and no ID or year, in case that there are movies with the same name
			#but produced in different years
		elif movid == "" and movname != "" and movyear != "":
			try:
				cursor.execute("SELECT idMovie from Movie WHERE MovieName = '%s' AND MovieYear = %s"%(movname,movyear))
				movidfound = cursor.fetchone()[0]
			except Exception as MovieDoesNotExist:
				return ("Movie Does Not Exist")
			cursor.execute("DELETE FROM Genre WHERE Genre = '%s' AND Movie_idMovie = '%s'"%(genre,movidfound))
			message = ("Deleted genre %s from Movie ID %s" %(genre,movidfound))
		else:
			message = ("Please enter movie ID, or movie name and year to modify a movie. Just entering the name is not enough!")
	except Exception as e:
		message = str(e)
	#commit the change
	cnx.commit()
	cursor.execute("select idMovie, MovieName, Genre from Genre inner join Movie on Movie_idMovie = idMovie order by idMovie")
	output = cursor.fetchall() 
	cursor.close()
	cnx.close()
	return render_template("allgen.html", table=output, message = message)


#List all genres, and the movie it is for sorted alphabetically by genre.
@app.route("/allgen", methods=['GET'])    
def allGen():
	cnx = mysql.connector.connect(user='root', host='127.0.0.1', database='MovieTheatre')
	cursor = cnx.cursor()  
	cursor.execute("select idMovie, MovieName, Genre from Genre inner join Movie on Movie_idMovie = idMovie order by Genre")
	output = cursor.fetchall()
	cursor.close()
	cnx.close()
	return render_template("allgen.html", table=output)

#ROOMS
#List rooms.
@app.route("/allrooms", methods=['GET'])    
def allRooms():
	cnx = mysql.connector.connect(user='root', host='127.0.0.1', database='MovieTheatre')
	cursor = cnx.cursor()  
	cursor.execute("select * from TheatreRoom")
	output = cursor.fetchall()
	cursor.close()
	cnx.close()
	return render_template("allrooms.html", table=output)

#Add a room
@app.route("/addroom", methods=['GET','POST'])    
def addRoom():
	cnx = mysql.connector.connect(user='root', host='127.0.0.1', database='MovieTheatre')
	cursor = cnx.cursor()
	try:
		roomnum = request.form['roomnum']
		cap = request.form['cap']
		cursor.execute ("SELECT RoomNumber from TheatreRoom where RoomNumber = %s" %(roomnum))
		exists = cursor.fetchone()
		if exists != None:
			message = "Room already exists"
		else:
			try:
				cursor.execute("INSERT INTO TheatreRoom VALUES (%s,%s)",(roomnum,cap))
				message = ("Room #%s with Capacity %s has been added." %(roomnum,cap))
			except Exception as valueswrong:
				message = "Please enter Room Number and Capacity!"
	except Exception as e:
	   message = str(e)
	#commit the change
	cnx.commit()
	cursor.execute("select * from TheatreRoom")  
	output = cursor.fetchall() 
	cursor.close()
	cnx.close()
	return render_template("allrooms.html", table=output, message = message)

@app.route("/delroom", methods=['GET','POST'])    
def delRoom():
	cnx = mysql.connector.connect(user='root', host='127.0.0.1', database='MovieTheatre')
	cursor = cnx.cursor()
	try:
		roomnum = request.form['roomnum']
		cursor.execute ("SELECT RoomNumber from TheatreRoom where RoomNumber = %s" %(roomnum))
		exists = cursor.fetchone()
		print(exists)
		if exists != None:
			try:
				cursor.execute("DELETE FROM TheatreRoom WHERE RoomNumber = %s" %(roomnum))
				message = ("Room number %s has been deleted." %(roomnum))
			except Exception as valueswrong:
				message = "Please enter Room Number as an integer"
		else:
			message = "Room does not exist"
	except Exception as e:
	   return(str(e))
	#commit the change
	cnx.commit()
	cursor.execute("select * from TheatreRoom")  
	output = cursor.fetchall() 
	cursor.close()
	cnx.close()
	return render_template("allrooms.html", table=output, message = message)

#Change Room Capacity
@app.route("/chroomcap", methods=['GET','POST'])    
def chRoomCap():
	cnx = mysql.connector.connect(user='root', host='127.0.0.1', database='MovieTheatre')
	cursor = cnx.cursor()
	try:
		roomnum = request.form['roomnum']
		newcap = request.form['cap']
		cursor.execute ("SELECT RoomNumber FROM TheatreRoom WHERE RoomNumber = %s" %(roomnum))
		exists = cursor.fetchone()
		if exists != None:
			try:
				cursor.execute("UPDATE TheatreRoom SET Capacity = %s WHERE RoomNumber = %s" %(newcap,roomnum))
				message = ("Room number %s's capacity has been changed to: %s" %(roomnum,newcap))
			except Exception as valueswrong:
				message = ("Please enter Room Number and Capacity as integers")
		else:
			message = ("Room does not exist")
	except Exception as e:
	   message = str(e)
	#commit the change
	cnx.commit()
	cursor.execute("select * from TheatreRoom")  
	output = cursor.fetchall() 
	cursor.close()
	cnx.close()
	return render_template("allrooms.html", table=output, message = message)

#Change Room Number
@app.route("/chroomnum", methods=['GET','POST'])    
def chRoomNum():
	cnx = mysql.connector.connect(user='root', host='127.0.0.1', database='MovieTheatre')
	cursor = cnx.cursor()
	try:
		roomnum = request.form['roomnum']
		newroom = request.form['newroomnum']
		cursor.execute ("SELECT RoomNumber FROM TheatreRoom WHERE RoomNumber = %s" %(roomnum))
		exists = cursor.fetchone()
		print(exists)
		if exists != None:
			try:
				cursor.execute("UPDATE TheatreRoom SET RoomNumber = %s WHERE RoomNumber = %s" %(newroom,roomnum))
				message = ("Room number %s has been changed to Room Number %s" %(roomnum,newnum))
			except Exception as valueswrong:
				message = ("Please enter Room Numbers as integers")
		else:
			message = ("Room does not exist")
	except Exception as e:
	   message = str(e)
	#commit the change
	cnx.commit()
	cursor.execute("select * from TheatreRoom")  
	output = cursor.fetchall() 
	cursor.close()
	cnx.close()
	return render_template("allrooms.html", table=output, message = message)

#SHOWINGS
#List showings.
@app.route("/allshows", methods=['GET'])    
def allShows():
	cnx = mysql.connector.connect(user='root', host='127.0.0.1', database='MovieTheatre')
	cursor = cnx.cursor()  
	cursor.execute("select idShowing, DATE_FORMAT(ShowingDateTime,'%b %d %Y %h:%i %p'), Movie_idMovie, TheatreRoom_RoomNumber, TicketPrice from Showing order by ShowingDateTime")
	output = cursor.fetchall()
	cursor.close()
	cnx.close()
	return render_template("allshows.html", table=output)
	return str(output)

#Add a show
@app.route("/addshow", methods=['GET','POST'])    
def addShow():
	cnx = mysql.connector.connect(user='root', host='127.0.0.1', database='MovieTheatre')
	cursor = cnx.cursor(buffered=True)
	try:
		showdate = request.form['showdate']
		movid = request.form['movid']
		roomnum = request.form['roomnum']
		price = request.form['price']
		#check movie exists
		cursor.execute ("SELECT idMovie from Movie where idMovie = %s" %(movid))
		movieexist = cursor.fetchone()
		#check room exists
		cursor.execute ("SELECT RoomNumber from TheatreRoom where RoomNumber = %s" %(roomnum))
		roomexist = cursor.fetchone()
		#check no showing in the same room at same time
		cursor.execute ("SELECT ShowingDateTime, TheatreRoom_RoomNumber from Showing where ShowingDateTime = '%s' and TheatreRoom_RoomNumber = %s" %(showdate, roomnum))
		roomdup = cursor.fetchone()
		if movieexist == None:
			message = ("Movie ID isn't in the database")
		elif roomexist == None:
			message = ("Room does not exist")
		elif roomdup != None:
			message = ("There is another showing in the same room at the same time")
		else:
			try:
				cursor.execute("INSERT INTO Showing(ShowingDateTime,Movie_idMovie,TheatreRoom_RoomNumber,TicketPrice) VALUES (%s,%s,%s,%s)",(showdate,movid,roomnum,price))
				message = ("The show has been added.")
			except Exception as valueswrong:
				message = str(valueswrong)
	except Exception as e:
		message = str(e)
	   # return(str(e))
	#commit the change
	cnx.commit()
	cursor.execute("select * from Showing")  
	output = cursor.fetchall() 
	cursor.close()
	cnx.close()
	return render_template("allshows.html", table=output, message = message)

#Delete a show
@app.route("/delshow", methods=['GET','POST'])    
def delShow():
	cnx = mysql.connector.connect(user='root', host='127.0.0.1', database='MovieTheatre')
	cursor = cnx.cursor()
	try:
		showID = request.form['showID']
		cursor.execute ("SELECT idShowing from Showing where idShowing = %s" %(showID))
		exists = cursor.fetchone()
		if exists != None:
			try:
				cursor.execute("DELETE FROM Showing WHERE idShowing = %s" %(showID))
				message = ("Showing with ID %s has been deleted." %(showID))
			except Exception as valueswrong:
				message = ("Please enter showing ID as an integer")
		else:
			message = ("Showing ID does not exist")
	except Exception as e:
	   return(str(e))
	#commit the change
	cnx.commit()
	cursor.execute("select * from Showing")  
	output = cursor.fetchall() 
	cursor.close()
	cnx.close()
	return render_template("allshows.html", table=output, message = message)

#Modify Show
#Mod show movie
@app.route("/modifyshowmovie", methods=['GET','POST'])    
def modifyShowMovie():
	cnx = mysql.connector.connect(user='root', host='127.0.0.1', database='MovieTheatre')
	cursor = cnx.cursor(buffered=True)
	try:
		showingID = request.form['showID']
		movID = request.form['newMovID']

		#check showing ID exists
		cursor.execute ("SELECT idShowing from Showing where idShowing = %s" %(showingID))
		showexist = cursor.fetchone()
		#check movie ID exists
		cursor.execute ("SELECT idMovie from Movie where idMovie = %s" %(movID))
		movexist = cursor.fetchone()
		if showexist == None:
			message = ("This showing ID: %s does not exist." %(showingID))
		elif movexist == None:
			message = ("The Movie ID: %s entered is not in the database." %(movID))
		else:
			cursor.execute("UPDATE Showing SET Movie_idMovie = '%s' where idShowing = %s" %(movID,showingID))
			message  = ("The Showing ID %s has had its Movie updated to Movie ID: %s" %(showingID,movID))
	except Exception as e:
		message = str(e)
	   # return(str(e))
	#commit the change
	cnx.commit()
	cursor.execute("select * from Showing")  
	output = cursor.fetchall() 
	cursor.close()
	cnx.close()
	return render_template("allshows.html", table=output, message = message)

#Mod show time
@app.route("/modifyshowtime", methods=['GET','POST'])    
def modifyShowTime():
	cnx = mysql.connector.connect(user='root', host='127.0.0.1', database='MovieTheatre')
	cursor = cnx.cursor(buffered=True)
	try:
		showingID = request.form['showID']
		showDate = request.form['newDateTime']
		

		#check showing ID exists
		cursor.execute ("SELECT idShowing from Showing where idShowing = %s" %(showingID))
		showexist = cursor.fetchone()
		#check no other showing in the room at the new time
		#get this room first
		cursor.execute("SELECT TheatreRoom_RoomNumber from Showing where idShowing = %s" %(showingID))
		thisRoom = cursor.fetchone()[0]
		#check this room + new time if there's a showing.
		cursor.execute("SELECT idShowing from Showing where ShowingDateTime = '%s' and TheatreRoom_RoomNumber = %s" %(showDate,thisRoom))
		timeConflict = cursor.fetchone()[0]

		if showexist == None:
			message = ("This showing ID: %s does not exist." %(showingID))
		elif timeConflict != None:
			message = ("There's another showing (showing ID %s) in this room at the new time." %(timeConflict))
		else:
			cursor.execute("UPDATE Showing SET ShowingDateTime = '%s' where idShowing = %s" %(showDate,showingID))
			message  = ("The Showing ID %s has had its showing time updated to: %s" %(showingID,showDate))
	except Exception as e:
		message = str(e)
	   # return(str(e))
	#commit the change
	cnx.commit()
	cursor.execute("select * from Showing")  
	output = cursor.fetchall() 
	cursor.close()
	cnx.close()
	return render_template("allshows.html", table=output, message = message)

#Mod show room
@app.route("/modifyshowroom", methods=['GET','POST'])    
def modifyShowRoom():
	cnx = mysql.connector.connect(user='root', host='127.0.0.1', database='MovieTheatre')
	cursor = cnx.cursor(buffered=True)
	try:
		showingID = request.form['showID']
		room = request.form['newRoom']
		#check showing ID exists
		cursor.execute ("SELECT idShowing from Showing where idShowing = %s" %(showingID))
		showexist = cursor.fetchone()
		#check entered room exists
		cursor.execute ("SELECT RoomNumber from Theatreroom where RoomNumber = %s" %(room))
		roomexist = cursor.fetchone()
		#check that theres no other showing in the new room at this time.
		#get this date time first.
		cursor.execute("SELECT ShowingDateTime from Showing where idShowing = %s" %(showingID))
		currentDateTime = cursor.fetchone()[0]
		cursor.execute("SELECT idShowing from Showing where ShowingDateTime = '%s' and TheatreRoom_RoomNumber = %s" %(currentDateTime,room))
		conflictShowing = cursor.fetchone()

		if showexist == None:
			message = ("This showing ID: %s does not exist." %(showingID))
		elif roomexist == None:
			message = ("The room number: %s does not exist." %(room))
		elif conflictShowing != None:
			message = ("The showing ID %s has a showing in that room at this time, there is a conflict." %(conflictShowing))
		else:
			cursor.execute("UPDATE Showing SET TheatreRoom_RoomNumber = '%s' where idShowing = %s" %(room,showingID))
			message  = ("The Showing ID %s has had its showing room updated to: %s" %(showingID,room))
	except Exception as e:
		message = str(e)
	   # return(str(e))
	#commit the change
	cnx.commit()
	cursor.execute("select * from Showing")  
	output = cursor.fetchall() 
	cursor.close()
	cnx.close()
	return render_template("allshows.html", table=output, message = message)

#Mod show price
@app.route("/modifyshowprice", methods=['GET','POST'])    
def modifyShowPrice():
	cnx = mysql.connector.connect(user='root', host='127.0.0.1', database='MovieTheatre')
	cursor = cnx.cursor(buffered=True)
	try:
		showingID = request.form['showID']
		price = request.form['newPrice']
		#check showing ID exists
		cursor.execute ("SELECT idShowing from Showing where idShowing = %s" %(showingID))
		showexist = cursor.fetchone()
		if showexist == None:
			message = ("This showing ID: %s does not exist." %(showingID))
		else:
			cursor.execute("UPDATE Showing SET TicketPrice = '%s' where idShowing = %s" %(price,showingID))
			message  = ("The Showing ID %s has had its price updated to: $%s" %(showingID,price))
	except Exception as e:
		message = str(e)
	   # return(str(e))
	#commit the change
	cnx.commit()
	cursor.execute("select * from Showing")  
	output = cursor.fetchall() 
	cursor.close()
	cnx.close()
	return render_template("allshows.html", table=output, message = message)

#CUSTOMERS
#List customers.
@app.route("/allcustomers", methods=['GET'])    
def allCustomers():
	cnx = mysql.connector.connect(user='root', host='127.0.0.1', database='MovieTheatre')
	cursor = cnx.cursor()  
	cursor.execute("select idCustomer, FirstName, LastName, EmailAddress, CAST(Sex AS CHAR) from Customer order by LastName")
	output = cursor.fetchall()
	cursor.close()
	cnx.close()
	return render_template("allcustomers.html", table=output)
	return str(output)

#Add Customer
@app.route("/addcustomers", methods=['POST','GET'])    
def addCustomers():
	cnx = mysql.connector.connect(user='root', host='127.0.0.1', database='MovieTheatre')
	cursor = cnx.cursor() 
	try:
		fname = request.form['fname']
		lname = request.form['lname']
		email = request.form['email']
		sex = request.form['sex']
	
		cursor.execute ("SELECT FirstName, LastName from Customer where LastName = '%s' and FirstName = '%s'"%(lname,fname))
		exists = cursor.fetchone()
		if exists != None:
			message = "This customer already exists"
		else:
			try:
				cursor.execute("INSERT INTO Customer(FirstName,LastName,EmailAddress,Sex) VALUES (%s,%s,%s,%s)",(fname,lname,email,sex))
				message = "The customer was added."
			except Exception as valueswrong:
				message = str(valueswrong)
				#return(str(valueswrong))
	except Exception as e:
	   #return(str(e))
	   message = str(e)
	#commit the change
	cnx.commit()
	cursor.execute("select idCustomer, FirstName, LastName, EmailAddress, CAST(Sex AS CHAR) from Customer order by idCustomer")
	output = cursor.fetchall() 
	cursor.close()
	cnx.close()
	return render_template("allcustomers.html", table=output, message = message)


#Delete
@app.route("/delcustomers", methods=['POST','GET'])    
def delCustomers():
	cnx = mysql.connector.connect(user='root', host='127.0.0.1', database='MovieTheatre')
	cursor = cnx.cursor() 
	try:
		custID = request.form['custID']
		fname = request.form['fname']
		lname = request.form['lname']

		if fname != "" and lname != "" and custID != '"':
			cursor.execute ("SELECT idCustomer, FirstName, LastName from Customer where LastName = '%s' and FirstName = '%s' and idCustomer = '%s'"%(lname,fname,custID))
			exists = cursor.fetchone()

		if exists == None:
			message = "The customer doesn't exist"
		else:
			try:
				cursor.execute("DELETE FROM Customer WHERE idCustomer = %s" %(custID))
				message = "The customer was deleted"
			except Exception as valueswrong:
				cursor.execute("DELETE FROM Attend WHERE Customer_IDCustomer = %s" %(custID))
				cursor.execute("DELETE FROM Customer WHERE idCustomer = %s" %(custID))
				message = "Customer was also deleted from Attend table due to foreign key constraint."
				#return("Customer was also deleted from Attend table due to foreign key constraint.");
	except Exception as e:
	   message = str(e)
	#commit the change
	cnx.commit()
	cursor.execute("select idCustomer, FirstName, LastName, EmailAddress, CAST(Sex AS CHAR) from Customer order by idCustomer")
	output = cursor.fetchall() 
	cursor.close()
	cnx.close()
	return render_template("allcustomers.html", table=output, message=message)

#Mod Name
@app.route("/modifyname", methods=['POST','GET'])    
def modifyName():
	cnx = mysql.connector.connect(user='root', host='127.0.0.1', database='MovieTheatre')
	cursor = cnx.cursor() 
	try:
		custID = request.form['custID']
		fname = request.form['newFirstName']
		lname = request.form['newLastName']

		if fname == "" and lname != "":
			cursor.execute("UPDATE Customer SET LastName = '%s' WHERE idCustomer = %s" %(lname,custID))
			message = "Customer's last name was updated"
		elif fname != "" and lname == "":
			cursor.execute("UPDATE Customer SET FirstName = '%s' WHERE idCustomer = %s" %(fname,custID))		
			message = "Customer's first name was updated"	
		elif fname != "" and lname !="":
			cursor.execute("UPDATE Customer SET FirstName = '%s', LastName = '%s' WHERE idCustomer = %s" %(fname,lname,custID))
			message = "Customers first and last name was updated"		
	except Exception as e:
	   message = str(e)
	#commit the change
	cnx.commit()
	cursor.execute("select idCustomer, FirstName, LastName, EmailAddress, CAST(Sex AS CHAR) from Customer order by idCustomer")
	output = cursor.fetchall() 
	cursor.close()
	cnx.close()
	return render_template("allcustomers.html", table=output, message=message)

#Mod Email
@app.route("/modifyemail", methods=['POST','GET'])    
def modifyEmail():
	cnx = mysql.connector.connect(user='root', host='127.0.0.1', database='MovieTheatre')
	cursor = cnx.cursor() 
	try:
		custID = request.form['custID']
		email = request.form['newEmail']

		cursor.execute("UPDATE Customer SET EmailAddress = '%s' WHERE idCustomer = %s" %(email,custID))
		message = "Customer's email was updated"

	except Exception as e:
	   message = str(e)
	#commit the change
	cnx.commit()
	cursor.execute("select idCustomer, FirstName, LastName, EmailAddress, CAST(Sex AS CHAR) from Customer order by idCustomer")
	output = cursor.fetchall() 
	cursor.close()
	cnx.close()
	return render_template("allcustomers.html", table=output, message=message)

#Mod Sex
@app.route("/modifysex", methods=['POST','GET'])    
def modifySex():
	cnx = mysql.connector.connect(user='root', host='127.0.0.1', database='MovieTheatre')
	cursor = cnx.cursor() 
	try:
		custID = request.form['custID']
		sex = request.form['newSex']

		cursor.execute("UPDATE Customer SET Sex = '%s' WHERE idCustomer = %s" %(sex,custID))
		message = "Customer's sex was updated"
		
	except Exception as e:
	   message = str(e)
	#commit the change
	cnx.commit()
	cursor.execute("select idCustomer, FirstName, LastName, EmailAddress, CAST(Sex AS CHAR) from Customer order by idCustomer")
	output = cursor.fetchall() 
	cursor.close()
	cnx.close()
	return render_template("allcustomers.html", table=output, message=message)

#RENDER CUSTOMER OPTIONS
@app.route('/customer')
def customer():
	return render_template("customer.html")

@app.route('/searchoptions')
def search():
	return render_template("searchoptions.html")

@app.route('/rateShowing')
def rate():
	cnx = mysql.connector.connect(user='root', host='127.0.0.1', database='MovieTheatre')
	cursor = cnx.cursor() 

	cursor.execute("SELECT FirstName, LastName, idCustomer FROM Customer")
	customers = cursor.fetchall()
	cursor.execute("SELECT idShowing from Showing")
	showings = cursor.fetchall()
	return render_template("rateshow.html", customers = customers, showings = showings)

@app.route('/addRating', methods=['POST','GET'])
def addRating():
	cnx = mysql.connector.connect(user='root', host='127.0.0.1', database='MovieTheatre')
	cursor = cnx.cursor() 

	custID = request.form['customers']
	showingID = request.form['showings']
	rating = request.form['rating']

	#check customer attended this showing.
	cursor.execute("SELECT Customer_idCustomer from Attend where Customer_idCustomer = %s AND Showing_idShowing = %s" %(custID,showingID))
	check = cursor.fetchone()
	if check != None:
		cursor.execute("UPDATE Attend SET Rating = %s WHERE Customer_idCustomer = %s and Showing_idShowing = %s" %(rating,custID,showingID))
		message = ("The rating of %s stars has been added to your viewing of showing ID %s" %(rating,showingID))
	else:
		message = ("You did not attend that showing, so you cannot rate it.")
	cnx.commit()
	cursor.close()
	cnx.close()
	return render_template("customerview.html", message = message)

@app.route('/attendshow')
def attendshow():
	cnx = mysql.connector.connect(user='root', host='127.0.0.1', database='MovieTheatre')
	cursor = cnx.cursor() 

	cursor.execute("SELECT FirstName, LastName, idCustomer FROM Customer")
	customers = cursor.fetchall()
	cursor.execute("SELECT idShowing from Showing")
	showings = cursor.fetchall()
	return render_template("attendshow.html", customers = customers, showings = showings)


@app.route('/addCustToShow', methods=['POST','GET'])
def addtoShow():
	cnx = mysql.connector.connect(user='root', host='127.0.0.1', database='MovieTheatre')
	cursor = cnx.cursor() 

	custID = request.form['customers']
	showingID = request.form['showings']
	print(custID)
	print(showingID)
	
	cursor.execute("INSERT IGNORE INTO Attend(Customer_idCustomer,Showing_idShowing) VALUES(%s,%s)" %(custID,showingID))
	message = ("You have been added to the attend table.")
	cnx.commit()
	cursor.close()
	cnx.close()
	return render_template("customerview.html", message = message)

@app.route('/seeProfile')
def see():
	cnx = mysql.connector.connect(user='root', host='127.0.0.1', database='MovieTheatre')
	cursor = cnx.cursor() 

	cursor.execute("SELECT FirstName, LastName, idCustomer FROM Customer")
	customers = cursor.fetchall()
	return render_template("seeprofile.html", customers = customers)

@app.route('/seeProfileInfo', methods=['POST','GET'])
def seeProfileInfo():
	cnx = mysql.connector.connect(user='root', host='127.0.0.1', database='MovieTheatre')
	cursor = cnx.cursor() 

	custID = request.form['customers']
	
	cursor.execute("SELECT idCustomer, FirstName, LastName, EmailAddress, CAST(Sex as CHAR) FROM Customer where idCustomer = %s" %(custID))
	profile = cursor.fetchall()
	cnx.commit()
	cursor.close()
	cnx.close()
	return render_template("customerview.html", profile = profile)

@app.route('/seeRatings')
def seeRatings():
	cnx = mysql.connector.connect(user='root', host='127.0.0.1', database='MovieTheatre')
	cursor = cnx.cursor() 

	cursor.execute("SELECT FirstName, LastName, idCustomer FROM Customer")
	customers = cursor.fetchall()
	return render_template("seeratings.html", customers = customers)

@app.route('/seeRatingsInfo', methods=['POST','GET'])
def seeRatingsInfo():
	cnx = mysql.connector.connect(user='root', host='127.0.0.1', database='MovieTheatre')
	cursor = cnx.cursor() 

	custID = request.form['customers']
	
	cursor.execute("select Attend.Customer_idCustomer as CustomerId, movieshowing.MovieName, Attend.Rating from Attend join (select Showing.idShowing as idShowing, Movie.idMovie, Movie.MovieName from Showing join Movie on Showing.Movie_idMovie = Movie.idMovie) as movieshowing on Attend.Showing_idShowing = movieshowing.idShowing where Attend.Customer_idCustomer = %s" %(custID))
	profileRating = cursor.fetchall()
	cnx.commit()
	cursor.close()
	cnx.close()
	return render_template("customerview.html", profileRating = profileRating)



#SEARCH OPTIONS
#Search by Genre
# @app.route("/searchbygen", methods=['GET','POST'])    
# def searchByGen():
# 	cnx = mysql.connector.connect(user='root', host='127.0.0.1', database='MovieTheatre')
# 	cursor = cnx.cursor()
	
# 	genre = request.form['genre']

# 	if movid != "":
# 		cursor.execute("INSERT INTO Genre(Genre,Movie_idMovie) VALUES('%s','%s') ON DUPLICATE KEY UPDATE Movie_idMovie = Movie_idMovie"%(genre,movid))
# 		message = ("Added genre: %s to Movie ID %s" %(genre,movid))
# 		#Cannot update a movie with just movie name and no ID or year, in case that there are movies with the same name
# 		#but produced in different years
# 	elif movid == "" and movname != "" and movyear != "":
# 		try:
# 			cursor.execute("SELECT idMovie from Movie WHERE MovieName = '%s' AND MovieYear = %s"%(movname,movyear))
# 			movidfound = cursor.fetchone()[0]
# 			cursor.execute("INSERT INTO Genre(Genre,Movie_idMovie) VALUES('%s',%s) ON DUPLICATE KEY UPDATE Movie_idMovie = Movie_idMovie"%(genre,movidfound))
# 			message = ("Added genre %s to movie %s with movie ID %s " %(genre,movname,movidfound))
# 		except Exception as MovieDoesNotExist:
# 			message = ("Movie Does Not Exist")
# 	else:
# 		message = ("Please enter movie ID, or movie name and year to modify a movie. Just entering the name is not enough!")

# 	#commit the change
# 	cnx.commit()
# 	cursor.execute("select idMovie, MovieName, Genre from Genre inner join Movie on Movie_idMovie = idMovie order by idMovie")
# 	output = cursor.fetchall() 
# 	cursor.close()
# 	cnx.close()
# 	return render_template("allgen.html", table=output, message = message)



