#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors
import datetime

#Initialize the app from Flask
app = Flask(__name__)

#Configure MySQL
conn = pymysql.connect(host='localhost',
                       port = 8889,
                       user='root',
                       password='root',
                       db='finstagram',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

#Define a route to hello function
@app.route('/')
def hello():
    return render_template('index.html')

#Define route for login
@app.route('/login')
def login():
    return render_template('login.html')

#Define route for register
@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/home')
def home():

    user = session['username']
    cursor = conn.cursor();


    query = 'SELECT DISTINCT photoID, photoPoster FROM Photo WHERE photoPoster = %s OR (photoID, photoPoster) IN(SELECT photoID, photoPoster FROM (Photo AS P JOIN Follow AS F ON (F.username_followed=P.photoPoster)) WHERE followstatus=TRUE AND P.allFollowers=True AND F.username_follower = %s)OR (photoID, photoPoster) IN (SELECT photoID, photoPoster FROM SharedWith JOIN BelongTo ON (SharedWith.groupOwner= BelongTo.owner_username AND SharedWith.groupName=BelongTo.groupName) WHERE SharedWith.photoID = photoID AND BelongTo.member_username = %s)'
    
    cursor.execute(query, (user, user, user))
    data = cursor.fetchall()
    cursor.close()
    return render_template('home.html', username=user, posts=data)


@app.route('/post', methods=['GET', 'POST'])
def post():
    username = session['username']
    cursor = conn.cursor();

    filepath = request.form['filepath']
    caption = request.form['caption']
    isAllFollowers = request.form['isAllFollowers']
    if (isAllFollowers == 'true'):
        isAllFollowers = True
    else:
        isAllFollowers = False

    query = 'INSERT INTO photo (filepath, caption, allFollowers, photoPoster, postingdate) VALUES(%s, %s, %s, %s, %s)'
    cursor.execute(query, (filepath, caption, isAllFollowers, username, datetime.datetime.now()))
    conn.commit()
    cursor.close()
    return redirect(url_for('home'))

@app.route('/edit/<int:currPhotoID>', methods=['GET', 'POST'])
def edit(currPhotoID):
    cursor = conn.cursor();
    filepath = request.form['filepath']
    caption = request.form['caption']
    isAllFollowers = request.form['isAllFollowers']
    if (isAllFollowers == 'true'):
        isAllFollowers = True
    else:
        isAllFollowers = False
    
    query = 'UPDATE Photo SET filepath=%s AND caption=%s AND allFollowers=%s WHERE photoID=%s)'
    cursor.execute(query, (filepath, caption, isAllFollowers, currPhotoID))
    conn.commit()
    cursor.close()
    return redirect(url_for('home'))

@app.route('/follow', methods = ['GET','POST'])
def follow():
    username = session['username']
    cursor = conn.cursor();

    followed = request.form['followed']
    query = 'SELECT * FROM Person where username =%s'
    cursor.execute(query, (followed))   
    data = cursor.fetchone()

    # Put in a wrong username that doesnt exist
    error = None
    if(data is None):
        error = "Invalid Username"
        return render_template('search_to_follow.html', error=error)

    # check to see if the person they want to follow is themselves
    if(followed.lower() == username.lower()):
        error = 'Invlaid Follow Request'
        return render_template('search_to_follow.html', error=error)
    query = 'SELECT * FROM Follow WHERE username_followed=%s AND username_follower =%s'
    cursor.execute(query, (followed,username))
    data = cursor.fetchone()

    # the follow request already exists 
    if(data):
        error = 'Invalid Follow Request'
        return render_template('search_to_follow.html', error=error)


    query = 'INSERT INTO Follow (username_followed,username_follower, followstatus) VALUES(%s, %s, %s)'
    cursor.execute(query, (followed,username,False))
     
    conn.commit()
    cursor.close()
    return redirect(url_for('home'))
   


@app.route('/search_to_follow')
def search_to_follow():
    return render_template('search_to_follow.html')



@app.route('/manage_follow_requests')
def manage_follow_requests():
    user = session['username']
    cursor = conn.cursor();
    query = 'SELECT * FROM Follow WHERE username_followed = %s AND followstatus=FALSE'
    cursor.execute(query, (user))
    data = cursor.fetchall()
    cursor.close()
    return render_template('manage_follow_requests.html', pending=data)

@app.route('/accept_follower/<string:follower>', methods = ['GET', 'POST'])
def accept_follower(follower):
    user = session['username']
    cursor = conn.cursor();
    query = 'UPDATE Follow SET followstatus = TRUE WHERE username_followed = %s AND username_follower = %s'
    cursor.execute(query, (user, follower))
    conn.commit()
    cursor.close()
    return manage_follow_requests()

@app.route('/reject_follower/<string:follower>', methods = ['GET', 'POST'])
def reject_follower(follower):
    user = session['username']
    cursor = conn.cursor();
    query = 'DELETE FROM Follow WHERE username_followed = %s AND username_follower = %s'
    cursor.execute(query, (user, follower))
    conn.commit()
    cursor.close()

    return manage_follow_requests()


@app.route('/show_photo/<int:currPhotoID>', methods=["GET"])
def show_photo(currPhotoID):
    cursor = conn.cursor()
    user = session['username']
    # currPost = request.args['photoID']
    query = 'SELECT * FROM photo JOIN Person ON(username=photoPoster)  WHERE photoID=%s'
    cursor.execute(query, (currPhotoID))
    data = cursor.fetchone()

    query = 'SELECT * FROM Tagged NATURAL JOIN Person WHERE photoID=%s AND tagstatus=TRUE'
    cursor.execute(query, (currPhotoID))
    taggees = cursor.fetchone()

    query = 'SELECT * FROM Likes NATURAL JOIN Person WHERE photoID=%s'
    cursor.execute(query, (currPhotoID))
    likes = cursor.fetchone()

    query = 'SELECT * FROM photo JOIN Person ON(username=photoPoster)  WHERE photoID=%s AND username=%s'
    cursor.execute(query, (currPhotoID, user))
    owner = cursor.fetchone()

    cursor.close()
    return render_template('show_photo.html', post=data, tagged=taggees, likees=likes, owner=owner)

@app.route('/edit_post/<int:currPhotoID>')
def edit_post(currPhotoID):
    cursor = conn.cursor()
    query = 'SELECT * FROM Photo WHERE photoID=%s'
    cursor.execute(query, (currPhotoID))
    data = cursor.fetchone()
    return render_template('edit_post.html', post=data)

@app.route('/search_by_poster')
def search_by_poster():
    return render_template('search_by_poster.html')


@app.route('/search', methods = ['GET','POST'])
def search():
    user = session['username']
    cursor = conn.cursor();
    photoPoster = request.form['photoPoster']

### need to make it that 
    query = 'SELECT DISTINCT photoID, photoPoster FROM Photo WHERE photoPoster = %s OR (photoID, photoPoster) IN(SELECT photoID, photoPoster FROM (Photo AS P JOIN Follow AS F ON (F.username_followed=P.photoPoster)) WHERE followstatus=TRUE AND P.allFollowers=True AND F.username_follower = %s)OR (photoID, photoPoster) IN (SELECT photoID, photoPoster FROM SharedWith JOIN BelongTo ON (SharedWith.groupOwner= BelongTo.owner_username AND SharedWith.groupName=BelongTo.groupName) WHERE SharedWith.photoID = photoID AND BelongTo.member_username = %s)'
    cursor.execute(query, (photoPoster,photoPoster,photoPoster))
    data = cursor.fetchall()
    
    # query = 'SELECT * FROM Photo where photoPoster =%s'

    #when i chnaged something then the invlaid username error doesnt
    # popo up anymore and it just lets it happen
    # Have to fix the second if statement to see if you dont follow the person
    error = None
    if(data is None):
        error = "Invalid Username"
        return render_template('search_by_poster.html', error=error)
    query = 'SELECT * FROM Follow where username_followed = %s and username_follower =%s'
    cursor.execute(query, (photoPoster,user))
    isFollowed = cursor.fetchall()

    if(isFollowed is None):
        error = "You are not following this person"
        return render_template('search_by_poster.html', error=error)


    cursor.close()
    return render_template('search_by_poster.html', username = photoPoster, posts=data, error=error)















#Authenticates the login
@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
    #grabs information from the forms
    username = request.form['username']
    password = request.form['password']

    #cursor used to send queries
    cursor = conn.cursor()
    #executes query
    query = 'SELECT * FROM Person WHERE username = %s and password = %s'
    cursor.execute(query, (username, password))
    #stores the results in a variable
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row
    cursor.close()
    error = None
    if(data):
        #creates a session for the the user
        #session is a built in
        session['username'] = username
        return redirect(url_for('home'))
    else:
        #returns an error message to the html page
        error = 'Invalid login or username'
        return render_template('login.html', error=error)

#Authenticates the register
@app.route('/registerAuth', methods=['GET', 'POST'])
def registerAuth():
    #grabs information from the forms
    username = request.form['username']
    password = request.form['password']
    firstName = request.form['firstName']
    lastName = request.form['lastName']
    bio = request.form['bio']

    #cursor used to send queries
    cursor = conn.cursor()
    #executes query
    query = 'SELECT * FROM Person WHERE username = %s'
    cursor.execute(query, (username))
    #stores the results in a variable
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row
    error = None
    if(data):
        #If the previous query returns data, then user exists
        error = "This user already exists"
        return render_template('register.html', error = error)
    else:
        ins = 'INSERT INTO Person VALUES(%s, %s, %s, %s, %s)'
        cursor.execute(ins, (username, password, firstName, lastName, bio))
        conn.commit()
        cursor.close()
        return render_template('index.html')

        
@app.route('/logout')
def logout():
    session.pop('username')
    return redirect('/')




# @app.route('/select_blogger')
# def select_blogger():
#     #check that user is logged in
#     #username = session['username']
#     #should throw exception if username not found
    
#     cursor = conn.cursor();
#     query = 'SELECT DISTINCT username FROM blog'
#     cursor.execute(query)
#     data = cursor.fetchall()
#     cursor.close()
#     return render_template('select_blogger.html', user_list=data)

# @app.route('/show_posts', methods=["GET", "POST"])
# def show_posts():
#     poster = request.args['poster']
#     cursor = conn.cursor();
#     query = 'SELECT ts, blog_post FROM blog WHERE username = %s ORDER BY ts DESC'
#     cursor.execute(query, poster)
#     data = cursor.fetchall()
#     cursor.close()
#     return render_template('show_posts.html', poster_name=poster, posts=data)

        
app.secret_key = 'some key that you will never guess'
#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
    app.run('127.0.0.1', 5000, debug = True)
