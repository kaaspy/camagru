# Camagru

Instagram if it was bought from wish at 95% discount

## Features

- Your password is hashed
- No injections available
- You can register and log in
- You can disconnect
- You can modify your profile
- You can browse posts with pagination
- You can like and comment posts
- You can be notified when someone comment your posts
- You can use the editor to make new posts
- Use your webcam or a image file and our stickers
- You can delete your posts in the editor

## Installation

```bash
# Clone the repository
git clone 

# Navigate to the project directory
cd camagru

# docker-compose it
docker-compose up --build
```

## Misc

There is a SQL injection sample file

## PHP standard library correspondances

### Core
@app.route : $_SERVER['REQUEST_URI']
redirect() : header('Location: ' . $url); exit;
url_for() : url construction from array
render_template() : include 
flash() : $_SESSION['flash']
session object : $_SESSION global
g object : $GLOBALS
request object : $_POST, $_GET, $_FILES, $_SERVER
abort() : http_response_code(404); exit;
@app.errorhandler : set_error_handler()
@app.context_processor : Define global variables before including templates

### Auth
generate_password_hash() : password_hash($password, PASSWORD_DEFAULT)
check_password_hash() : password_verify($password, $hash)
secrets.token_urlsafe() : base64_encode(random_bytes(16))
@functools.wraps : manually preserve function metadata
session.clear() : session_unset()

### DB
sqlite3.connect() : new SQLite3($database_path)
cursor.execute() : $db->prepare()->execute()
fetchone() : $result->fetchArray(SQLITE3_ASSOC)
fetchall() : $result->fetchArray(SQLITE3_ASSOC) in a loop
db.commit() : Changes auto-committed by default
db.IntegrityError : $db->lastErrorCode()
executescript() : $db->exec($sql)
register_converter() : manually convert after fetching
row_factory : fetch as associative array with SQLITE3_ASSOC

### File

os.makedirs() : mkdir()
os.path.join() : . concatenation
os.path.exists() : file_exists() or is_dir()
os.listdir() : glob()
os.path.isfile() : is_file()
os.remove() : unlink()
os.removedirs() : rmdir()
os.getenv() : getenv()

### Image

Image.open() : imagecreatefrompng(), imagecreatefromjpeg()
Image.new() : imagecreatetruecolor()
paste() : imagecopymerge()
save() : imagepng(), imagejpeg()
PIL operations : GD library functions

### Mail

Thread() : No native threading use synchronous sending
flask_mail.Mail : mail() 
Message() : Build email headers and body for mail()

### Utils

datetime : DateTime
strftime() : $date->format()
uuid.uuid4() : uniqid()
click.command() : Create CLI scripts with #!/usr/bin/env php and $argv
functools.wraps : manually preserve metadata
itertools : array_map(), array_filter(), array_reduce()

[x for x in y] : array_map() or foreach loop
any(c.isupper() for c in password) : preg_match('/[A-Z]/', $password)
any(c.islower() for c in password) : preg_match('/[a-z]/', $password)
any(c.isdigit() for c in password) : preg_match('/[0-9]/', $password)
next(u for u in users if ...) : array_filter() then reset()
dict() : ['key' => 'value']

### Patterns

@login_required : Check authentication at start of protected functions
@bp.before_app_request : Create middleware function called at beginning of requests
@app.teardown_appcontext : register_shutdown_function()