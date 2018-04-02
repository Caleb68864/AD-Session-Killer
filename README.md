# AD Session Killer
App I wrote that lists users on Windows servers and makes it easy to kill their sessions

Currently it only works for citrix sessions, but modifying this line "if line.startswith(' ica-cgp#'):" should allow managing other types of user sessions.

# How to Use
Typing the server names separated by spaces into the servers text box and clicking "Refresh" will list all the users on the servers alphabetically.

You can also add a file named "servers.txt" to the directory of __main__.py with one server name on each line.
This will load the "Server:" text box on launch

Use RunAsAdmin.bat to run the script as a network admin.