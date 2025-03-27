Team: Omar Ramirez
Steps to run

NOTE: You need to update your own CONNECTION_STRING in the .env file, I am using MongoDB Atlas. Recommending using mongodb

1. Create .venv folder
2. Install packages using requirments.txt file
3. Select Interpreter
4. Run app.py

Avialble API endpoints

A. Method: POST, Link: http://localhost:5000/register
form data - 'username', 'password'

B. Method: POST, Link: http://localhost:5000/login
Cotent-Type: application/json
json data - 'username', 'password

C. Method: POST, Link: http://localhost:5000/file_upload
file data - 'file'

D. Method: GET, Link: http://localhost:5000/public

E. Method: GET, Link: http://localhost:5000/protected
token info - 'token'

F. Method: GET, Link: http://localhost:5000/logout

G. Method: POST, Link: http://localhost:5000/update_delete
update username - 'username

H. Method: Delete, Link: http://localhost:5000/update_delete
