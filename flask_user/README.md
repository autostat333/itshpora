# Flask User
###Lib for log-in in Flask###

Designated to write to COOKIE:
- **STAT** info about user (*last_visit timestamp, kolvo_visits, his language etc*...all that is nned for analysis and user personalization)
- **STAT signature**  - signature for stat JSON
- **LOG_TOKEN** - log IN token (base64 encoded JSON with user information and signature)

    

The main logic is next:

```@app.before_request
def before_request():
    app.user = User('som secet key')  //it must be once, to put object in app.dictionary
    app.user.deserialize(request)   //pull from request cookie and from request.environ['SERVER_NAME']. Server name - it is IP, it must be equal to IP in log_token.
    
$app.after_request
def after_request():
    app.user_serialize(response)  //it put into cookies stat, stat_signature and if it is - log_token 
```    
If you need to use login, you can use it in next way:

```
app.user.registr(u_doc)
```

It creates new user in DB. 
u_doc must contain:
 - ['name'] = 'some user name'
 - ['pass'] = 'some pass' //it will be converted to md5 when inserting to DB
 - ['token_live_time'] = '86400'  //it is time for checking fresh session on not
 - ['roles'] = ['admin','superadmin']  //it is using for checking permission

Success returns: True
 
```
app.user.check_auth(roles)
```
**Roles** - contains list with roles for checking auth ..['admin']
It is checking permission and other params as authorization (validness, freshness etc).
Possible next errors:
 - Not LogIn
 - Not Valid Log Token
 - Not Valid IP
 - Session not fresh
 - Not enough permission

Success returns: True
 
```
app.user.login(user_name,user_pass)  //cretes new session dictionary and generate new log_token
```

If check_auth have dropped - you need to logIn (generate new log_token)
Possible next errors:
 - No Such User
 - Wrong Pass

Success returns: True
 
```
app.user.drop()
```
Set log-tokne='None'


#####BEFORE INIT

You need to determine other than default DB (simple db.txt file).

```
self._db_init()
```
Initialize DB (connections)


```
self._db_check_in(user_name)
```

It is looping throught the user table and find user doc by user_name. Returns user_id and user_document.
User_id not user_name

```
self._db_add(user_id,user_doc)
```
Add new document to DB (pass key, value) to method













    
