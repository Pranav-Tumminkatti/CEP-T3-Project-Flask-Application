#import necessary modules
import flask, json, os, datetime
from flask import render_template, request, Flask, url_for, redirect
from werkzeug.exceptions import abort
from datetime import date

app = flask.Flask(__name__)
global logged_in, newsletter_subs, user_info    #define all global variables
logged_in = False
newsletter_subs = []
user_info = None

@app.route("/", methods=['GET','POST'])
def root():
    return render_template('home.html', l_in = logged_in)   #the logged_in bool is pushed to every html template because the items in the navbar change depending on weather a user is logged in or not


@app.route("/ssr", methods=['GET','POST'])    #ssr --> show subscription results
def ssr():
  if logged_in == True:       #check if the user is logged in
    newsletter_subs.append(request.form['entry'])     #subscription emails are stored locally so the list gets reset when you restart the server
    return render_template('ssr.html', form=newsletter_subs, l_in = logged_in)    #only a logged in user can view the subscription results data. Alternatively, this can be assigned to an admin account
  else:                                                                     
    return redirect(url_for('about_us', l_in = logged_in))  
  

@app.route("/about_us", methods=['GET','POST'])     #route to the 'about us' page
def about_us():
    return render_template('about_us.html', l_in = logged_in)
  
#the name is 'your blogs' but think of it as a universal 'Blogs' page. I changed plans midway so I couldn't change the route name
@app.route("/your_blogs", methods=['GET', 'POST'])  #display all blogs on the 'Blogs' page. The name says 'your blogs' but since sessions have not been implemented yet, its mainly a universal Blogs page where you can see blogs posted by all users
def your_blogs():                                     
  if logged_in == True:                   #check if the user is logged in
    if os.path.exists("blog_data.json"):  #check if blog_data.json exists
      with open("blog_data.json") as datafile:  #if it does, load its data into the saveddata dictionary
        saveddata = json.load(datafile)
    else:
      saveddata = {}      #If dosen't, start a new empty saveddata dict
    return render_template('your_blogs.html', l_in = logged_in, posts = saveddata)   #only a logged in user can view the posted blogs.
  else:
    return redirect(url_for('login', l_in = logged_in))


@app.route("/contact_us", methods=['GET','POST'])   #route to the 'contact us' page
def contact_us():
    return render_template('contact_us.html', l_in = logged_in)


@app.route("/scr", methods=['GET','POST'])    #scr --> show contact results
def scr():
  if logged_in == True: 
                                                        
    # Check if there are other contact data stored in contact_data.json
    if os.path.exists("contact_data.json"):
      # If there are, load it into the saveddata dict
      with open("contact_data.json") as datafile:
        saveddata = json.load(datafile)
    else:
      #If there aren't, start a new empty dict
      saveddata = {}

    if request.method == "POST":
      # If new scores are entered and received via the POST method
      # Store the subject scores under email as the 'primary key', since 2 people can't have the same email
      saveddata[request.form['email']] = request.form

    # Store the latest subject, score information by overwriting the old contact_data.json
    with open("contact_data.json", "w") as datafile:
      json.dump(saveddata, datafile)
      
    return render_template('scr.html', form=saveddata, l_in = logged_in)    #only a logged in user can view the contact data.
  
  else:   
                                                                      
    return redirect(url_for('about_us', l_in = logged_in))

#BLOG HANDLING ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

@app.route("/display_post/<id>", methods=['GET', 'POST'])    #route to display an individual post by retrieving the post id from the url
def display_post(id):
  id = str(id)
  if logged_in == True:       #user authentication
    
    if os.path.exists("blog_data.json"):
      
      with open("blog_data.json") as datafile:
        saveddata = json.load(datafile)
        if id in saveddata:         #check if the post exists in the json file
          blog = saveddata[id]  #retrieve the post data from the json file and push it to display_post.html 
        else:
          abort(404)        #if it does not, abort with an error
    else:
      abort(404)            #honestly, these aborts will not be activiated unless and until someone tampers with the backend code and the json file while the server is running

    return render_template('display_post.html', l_in = logged_in, post=blog)  #push the post data to display_post.html
  else:
    return redirect(url_for('login', l_in = logged_in))


@app.route("/create_post", methods=['GET', 'POST'])    
def create_post():
  if logged_in == True:     #check if user is logged in
         
    #get the date on which the post is published
    from datetime import date
    dt = date.today().strftime("%d %B %Y")  
    
    #code to get a unique id for each post
    if os.path.exists('count.txt'):   
      #get the integer in count.txt if it exists
      f = open("count.txt", "r")
      count = int(f.read())
      f.close()
    else:
      #if count.txt does not exist, assign the value 1 to count
      count = 1
    
    if request.method  == 'POST':
      id = request.form['id']
      
      #check if blog_data.json exists
      if os.path.exists("blog_data.json"):
        # If there are, load it into the saveddata dict
        with open("blog_data.json") as datafile:
          saveddata = json.load(datafile)
      else:
        #If there aren't, start a new empty dict
        saveddata = {}

      #update the dict with the new form submission
      saveddata[id] = request.form
      
      # Store the latest subject, score information by overwriting the old file
      with open("blog_data.json", "w") as datafile:
        json.dump(saveddata, datafile)
      
      count+=1  #increment the value of count by 1 when a blog is posted
    
      f = open("count.txt", "w")    #overwrite the count.txt file with the new count value
      f.write(str(count))
      f.close()
        
      return redirect(url_for('your_blogs', l_in = logged_in))    #after successfully creating a post, redirect user to the 'Blogs' page
    else: 
      return render_template('create_post.html', l_in = logged_in, date=dt, cnt = count, author=user_info['name']) #if request.method is GET, redirect to the form and push author, date and id data to the form
  else:                                                                                  #author name is the full name of the user that is currently logged in
    return redirect(url_for('login', l_in = logged_in))   #if user is not logged in, redirect him to the login page
    

@app.route("/edit_post/<id>", methods=['GET', 'POST'])   #route to edit a specific post by retrieving the post id from the url
def edit_post(id):
  id = str(id)
  if logged_in == True:     #user auth
    if os.path.exists("blog_data.json"):
      
      #code to load the current blog data into variable named blog
      with open("blog_data.json") as datafile:
        saveddata = json.load(datafile)
      if id in saveddata:
          blog = saveddata[id]
          
      else:
        abort(404) 
              
    else:
      abort(404)
        
    if request.method  == 'POST':
      category = request.form['category']
      title = request.form['title']
      content = request.form['content']
      synopsis = request.form['synopsis']
      
      #overwrite the blog data with the newly submitted data
      blog['category'] = category             
      blog['title'] = title
      blog['content'] = content
      blog['synopsis'] = synopsis
      
      with open("blog_data.json", "w") as datafile:   #push the new data back to the json file
        json.dump(saveddata, datafile)
        
      return redirect(url_for('display_post', id = id, l_in = logged_in))
    
    return render_template('edit_post.html', l_in = logged_in, blog = blog, id=id)  #when the form is first opened, edit_post.html is immediately rendered because the request method is GET not POST. POST is only run after the form is submitted
                                                               #existing blog data is pushed and displayed in the form as the value of a field
  else:
    
    return redirect(url_for('login', l_in = logged_in))


@app.route("/delete_post/<id>", methods=['POST'])   #method is limited to POST only so that the post is not accidentally deleted by entering a url
def delete_post(id):                                #user needs to be logged in to reach the delete post button anyways so no point adding a login checker here
  id = str(id)
  if os.path.exists("blog_data.json"):
    with open("blog_data.json") as datafile:
      saveddata = json.load(datafile)
    if id in saveddata:                             #if the blog's data is in the json file, delete it
      del saveddata[id]
      
      with open("blog_data.json", "w") as datafile:  #dump the new dict without the deleted post back to the json file
        json.dump(saveddata, datafile)
      
      return redirect(url_for('your_blogs', l_in = logged_in))
      
    else:
      abort(404)        #this will be called if you're trying to delete a post that never existed but since this route dosent accept a GET request anyways, I don't see how that will happen but eh, its there for safety purposes
  else:
    abort(404)

#BLOG HANDLING ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#USER AUTHENTICATION ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

@app.route("/sign_up", methods=['GET', 'POST'])
def sign_up():
  if request.method  == 'POST':
      #variables to be loaded
      name = request.form['name']
      email = request.form['email']
      password = request.form['password']
      
      #check if auth_data.json exists
      if os.path.exists("auth_data.json"):
        # If it does, load its data into the saveddata dict
        with open("auth_data.json") as datafile:
          saveddata = json.load(datafile)
      else:
        #If there isin't, start a new empty dict
        saveddata = {}

      #update the dict with the new form submission
      saveddata[email] = request.form
      
      # Store the newly registered user's data by overwriting the old file
      with open("auth_data.json", "w") as datafile:
        json.dump(saveddata, datafile)
        
      return redirect(url_for('login', l_in = logged_in))    #after successfully signing up, redirect user to the login page for conformation
  
  else: 
    
    return render_template('sign_up.html', l_in = logged_in)


@app.route("/login", methods=['GET', 'POST'])   
def login():
  error = None
  if request.method  == 'POST':     #receive the form data
    #variables to be verified
    email = request.form['email']
    password = request.form['password']
    
    if os.path.exists("auth_data.json"):
      with open("auth_data.json") as datafile:    #load auth_data from auth_data.json to a local variable
        saveddata = json.load(datafile)
      if (email in saveddata) and (saveddata[email]['email'] == email) and (saveddata[email]['password'] == password):  #verify if the username exists and if it does, it matches the password stored along with it 
        global logged_in, user_info
        logged_in = True       #if the user is validated, the global variable logged_in is set to True and this is passed to all the html pages
        user_info = saveddata[email]  #the global variable called user_info now contains the name, email and password of the current active user
        #check if profile_data.json exists
        if os.path.exists("profile_data.json"):
          # If it does, load it into the profile_data dict
          with open("profile_data.json") as datafile:
            profile_data = json.load(datafile)
          
          if email in profile_data: #if this is not the user's first time logging in, he is directly sent to the homepage
            return redirect(url_for('root', l_in = logged_in))
          else:
            #if this is the user's first time logging in, assign the default values to his profile_data
            default_data = {'name': user_info['name'], 'job': 'What you do', 'location':'25.0000° N, 71.0000° W', 'description':'Totally short and optional description about yourself, what you do and so on.'}
            #update profile_data with the default data for the user
            profile_data[email] = default_data
        else:
          #if the very first user of the website is logging in, start a new empty dict, load the default data and push it to the newly created profile_data
          profile_data = {}
          
          default_data = {'name': user_info['name'], 'job': 'What you do', 'location':'25.0000° N, 71.0000° W', 'description':'Totally short and optional description about yourself, what you do and so on.'}
          #update profile_data with the default data for the user
          profile_data[email] = default_data
        
        #push the new profile_data to profile_data.json by overwriting the old file
        with open("profile_data.json", "w") as datafile:
          json.dump(profile_data, datafile)
          
        return redirect(url_for('root', l_in = logged_in))
      else:
        error = "Your credentials don't match. Please try again."     #if the username does not exist or the password for the entered username is not correct, this error message is relayed to the login form where it is then displayed
    else:
      error = 'No accounts have been registered yet. Please sign up for one first.'   #if auth_data does not exist (i.e. no accounts have been registered yet), this error messaage is relayed to the login form where it is then displayed
      
  return render_template('login.html', l_in = logged_in, error=error)


@app.route("/tbfy", methods=['GET', 'POST'])    #route to the 'too bad for you' page if you click Forgot Password :)
def tbfy():     #tbfy --> too bad for you
  return render_template('tbfy.html', l_in = logged_in)


@app.route("/logout", methods=['GET', 'POST'])  #when the user clicks logout in the profile page, the global variables logged_in and user_info will be set to False and None respectively
def logout():
  global logged_in, user_info
  logged_in = False
  user_info = None
  return redirect(url_for('root', l_in = logged_in))  #the logged out user will then be redirected to the home page

#USER AUTHENTICATION ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#PROFILE HANDLING ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

@app.route("/profile", methods=['GET', 'POST'])
def profile():
  if logged_in == True:
    #check if profile_data.json exists
    if os.path.exists("profile_data.json"):
      # if it does, load it into the profile_data dict
      with open("profile_data.json") as datafile:
        profile_data = json.load(datafile)
    else:
      abort(404)  #if profile_data.json does not exist (which should not happen as it is created upon login and this code can only be run on a logged in user), an error 404 is returned, for safety purposes
      
    return render_template('profile.html', l_in = logged_in, name=profile_data[user_info['email']]['name'], job=profile_data[user_info['email']]['job'], location=profile_data[user_info['email']]['location'], description=profile_data[user_info['email']]['description'])
                                                             #render the profile page with all the data from the profile_data.json file listed under the user's email which is retrieved from the global variable user_info
  else:
    return redirect(url_for('login', l_in = logged_in))

@app.route("/edit_profile", methods=['GET', 'POST'])
def edit_profile():
  if logged_in == True:
    
    #retrieve the current profile_data of the user from profile_data.json and push it to the html form to be used as the value of the respective inputs
    if os.path.exists("profile_data.json"):
      with open("profile_data.json") as datafile:
        profile_data = json.load(datafile)
      
      if request.method  == 'POST':
        #variables received from the form submission
        name = request.form['name']
        job = request.form['job']
        location = request.form['location']
        description = request.form['description']
        
        #update the data in the profile_data dict
        profile_data[user_info['email']]['name'] = name
        profile_data[user_info['email']]['job'] = job
        profile_data[user_info['email']]['location'] = location
        profile_data[user_info['email']]['description'] = description
        
        #push the new updated profile_data dict back to profile_data.json
        with open("profile_data.json", "w") as datafile:
          json.dump(profile_data, datafile)
        
        return redirect(url_for('profile', l_in = logged_in))
        
      return render_template('edit_profile.html', l_in = logged_in, name=profile_data[user_info['email']]['name'], job=profile_data[user_info['email']]['job'], location=profile_data[user_info['email']]['location'], description=profile_data[user_info['email']]['description'])
                                                                    #push the data from profile_data to the html form to be used as the value of the respective inputs
    else:
      abort(404)  #if profile_data.json does not exist (which should not happen as it is created upon login and this code can only be run on a logged in user), an error 404 is returned, for safety purposes
    
  else:
    return redirect(url_for('login', l_in = logged_in))


@app.route("/delete_profile", methods=['POST'])   #for this route, only the post method is accepted lest the user accidentally deletes his profile/account
def delete_profile():
  #load the global variables
  global logged_in, user_info   
  
  #load profile_data and auth_data respectively
  if os.path.exists("profile_data.json") and os.path.exists("auth_data.json"):
    with open("profile_data.json") as datafile:
      profile_data = json.load(datafile)
    with open("auth_data.json") as datafile:
      auth_data = json.load(datafile)
      
    if (user_info['email'] in profile_data) and (user_info['email'] in auth_data):
      #delete profile from profile_data
      del profile_data[user_info['email']]
      #delete account from auth_data
      del auth_data[user_info['email']]
      #set global variables to False and None respectively
      logged_in = False
      user_info = None
      
      #push the edited data back to profile_data and auth_data respectively
      with open("profile_data.json", "w") as datafile:
        json.dump(profile_data, datafile)
      with open("auth_data.json", "w") as datafile:
        json.dump(auth_data, datafile)
      
      return redirect(url_for('root', l_in = logged_in))
      
    else:
      abort(404)        #should never occur unless someone tampers with the backend data while the server is running
  else:
    abort(404)    #should never occur at all/does not make sense for it to occur but it is there for safety purposes

#PROFILE HANDLING ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


@app.errorhandler(404)    #404 errorhandler
def not_found(error):
  return render_template("404.html", l_in = logged_in) 

#Run Script
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True) 
    
#Terminal Commands to kill port
'''sudo lsof -i:8080'''
'''sudo kill (enter PID)'''
