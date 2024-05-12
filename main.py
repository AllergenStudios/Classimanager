import os
import sys
import subprocess
import time

import requests
import shutil
import zipfile
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QListWidget, QPushButton, QWidget, QInputDialog, QMessageBox

if not os.path.exists(os.environ.get('USERPROFILE') + "\\ClassiCube Servers"):
    os.mkdir(os.environ.get('USERPROFILE') + "\\ClassiCube Servers")

class ServerLauncher(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Classimanager")
        self.setGeometry(100, 100, 400, 300)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.server_list = QListWidget()
        self.layout.addWidget(self.server_list)

        self.add_new_button = QPushButton("Add New")
        self.layout.addWidget(self.add_new_button)

        self.launch_button = QPushButton("Launch")
        self.layout.addWidget(self.launch_button)

        self.delete_button = QPushButton("Delete")
        self.layout.addWidget(self.delete_button)

        self.add_new_button.clicked.connect(self.add_new_server)
        self.launch_button.clicked.connect(self.launch_server)
        self.delete_button.clicked.connect(self.delete_server)

        self.populate_server_list()

    def populate_server_list(self):
        # Directory containing server folders
        server_directory = f"{os.environ.get('USERPROFILE')}\\Classicube Servers"

        if not os.path.isdir(server_directory):
            print(f"Error: '{server_directory}' is not a valid directory.")
            return

        self.server_list.clear()

        servers = os.listdir(server_directory)

        for server in servers:
            if os.path.isdir(os.path.join(server_directory, server)):
                self.server_list.addItem(server)

    def add_new_server(self):
        # Prompt user for the name of the server folder
        server_name, ok = QInputDialog.getText(self, "Server Name", "Enter the name of the server folder:")
        if not ok:
            return  # User cancelled

        # Fetch latest release information from GitHub API
        github_repo_url = "https://api.github.com/repos/ClassiCube/MCGalaxy/releases/latest"
        response = requests.get(github_repo_url)

        if response.status_code == 200:
            release_info = response.json()
            assets = release_info.get("assets", [])
            if assets:
                # Get the download URL of the first asset
                download_url = assets[0]["browser_download_url"]
                print("Download URL:", download_url)

                # Download the asset
                download_command = f"curl -L -o MCGalaxy.zip {download_url}"
                try:
                    subprocess.run(download_command, shell=True, check=True)
                except subprocess.CalledProcessError:
                    print("Error: Failed to download the latest release.")
                    return

                print("Download successful.")

                # Move the downloaded zip file to the server directory
                server_directory = f"{os.environ.get('USERPROFILE')}\\Classicube Servers"
                zip_file_path = "MCGalaxy.zip"
                shutil.move(zip_file_path, server_directory)

                # Unzip the downloaded file
                with zipfile.ZipFile(os.path.join(server_directory, zip_file_path), "r") as zip_ref:
                    # Create a folder for the server
                    server_folder = os.path.join(server_directory, server_name)
                    os.makedirs(server_folder, exist_ok=True)
                    zip_ref.extractall(server_folder)

                # Remove the zip file
                os.remove(os.path.join(server_directory, zip_file_path))

                time.sleep(2.5)

                # Edit server.properties file
                main_properties = """
                #   Edit the settings below to modify how your server operates. This is an explanation of what each setting does.
#   server-name                   = The name which displays on classicube.net
#   motd                          = The message which displays when a player connects
#   port                          = The port to operate from
#   verify-names                  = Verify the validity of names
#   public                        = Set to true to appear in the public server list
#   max-players                   = The maximum number of connections
#   max-guests                    = The maximum number of guests allowed
#   max-maps                      = The maximum number of maps loaded at once
#   world-chat                    = Set to true to enable world chat
#   irc                           = Set to true to enable the IRC bot
#   irc-nick                      = The name of the IRC bot
#   irc-server                    = The server to connect to
#   irc-channel                   = The channel to join
#   irc-opchannel                 = The channel to join (posts OpChat)
#   irc-port                      = The port to use to connect
#   irc-identify                  = (true/false)    Do you want the IRC bot to Identify itself with nickserv. Note: You will need to register it's name with nickserv manually.
#   irc-password                  = The password you want to use if you're identifying with nickserv
#   backup-time                   = The number of seconds between automatic backups
#   overload                      = The higher this is, the longer the physics is allowed to lag.  Default 1500
#   use-whitelist                 = Switch to allow use of a whitelist to override IP bans for certain players.  Default false.
#   force-cuboid                  = Run cuboid until the limit is hit, instead of canceling the whole operation.  Default false.
#   profanity-filter              = Replace certain bad words in the chat.  Default false.
#   notify-on-join-leave          = Show a balloon popup in tray notification area when a player joins/leaves the server.  Default false.
#   allow-tp-to-higher-ranks      = Allows the teleportation to players of higher ranks
#   agree-to-rules-on-entry       = Forces all new players to the server to agree to the rules before they can build or use commands.
#   admins-join-silent            = Players who have adminchat permission join the game silently. Default true
#   server-owner                  = The minecraft name, of the owner of the server.
#   guest-limit-notify            = Show -Too Many Guests- message in chat when maxGuests has been reached. Default false
#   guest-join-notify             = Shows when guests and lower ranks join server in chat and IRC. Default true
#   guest-leave-notify            = Shows when guests and lower ranks leave server in chat and IRC. Default true
#   announcement-interval         = The delay in between server announcements in minutes. Default 5

#   UseMySQL                      = Use MySQL (true) or use SQLite (false)
#   Host                          = The host name for the database (usually 127.0.0.1)
#   SQLPort                       = Port number to be used for MySQL.  Unless you manually changed the port, leave this alone.  Default 3306.
#   Username                      = The username you used to create the database (usually root)
#   Password                      = The password set while making the database
#   DatabaseName                  = The name of the database stored (Default = MCZall)

#   defaultColor                  = The color code of the default messages (Default = &e)

#   kick-on-hackrank              = Set to true if hackrank should kick players
#   hackrank-kick-time            = Number of seconds until player is kicked
#   custom-rank-welcome-messages  = Decides if different welcome messages for each rank is enabled. Default true.
#   ignore-ops                    = Decides whether or not an operator can be ignored. Default false.

#   admin-verification            = Determines whether admins have to verify on entry to the server.  Default true.
#   verify-admin-perm             = The minimum rank required for admin verification to occur.

#   mute-on-spam                  = If enabled it mutes a player for spamming.  Default false.
#   spam-messages                 = The amount of messages that have to be sent "consecutively" to be muted.
#   spam-mute-time                = The amount of seconds a player is muted for spam.
#   spam-counter-reset-time       = The amount of seconds the "consecutive" messages have to fall between to be considered spam.

#   As an example, if you wanted the spam to only mute if a user posts 5 messages in a row within 2 seconds, you would use the folowing:
#   mute-on-spam                  = true
#   spam-messages                 = 5
#   spam-mute-time                = 60
#   spam-counter-reset-time       = 2

# Server settings
server-name = [MCGalaxy] Default
motd = Welcome!
max-players = 16
max-guests = 14
port = 25565
public = false
verify-names = true
default-rank = guest
server-owner = the owner
enable-cpe = true

# Level settings
autoload = true
world-chat = true
main-name = main
default-texture-url = 
default-texture-pack-url = 

# Security settings
use-whitelist = false
admin-verification = true
verify-admin-perm = 80

# Webclient settings
support-web-client = true
allow-ip-forwarding = true

# Other settings
HeartbeatURL = http://www.classicube.net/heartbeat.jsp
core-secret-commands = true
software-staff-prefixes = true
position-interval = 100
agree-to-rules-on-entry = false
admins-join-silent = false
checkpoints-respawn-clientside = true
rplimit = 500
rplimit-norm = 10000
physicsrestart = true
physics-undo-max = 50000
afk-minutes = 10
max-bots-per-level = 192
deathcount = true
repeat-messages = false
announcement-interval = 5
money-name = moneys
guest-limit-notify = false
guest-join-notify = true
guest-leave-notify = true
show-world-changes = true
kick-on-hackrank = true
hackrank-kick-time = 5
show-empty-ranks = false
draw-reload-threshold = 0.00100000004749745
allow-tp-to-higher-ranks = true
os-perbuild-default = 120
protect-staff-ips = true
classicube-account-plus = false
listen-ip = 0.0.0.0
disabled-commands = 
disabled-modules = 
death-invulnerability-cooldown = 2

# Error handling settings
restart-on-error = true

# Update settings
check-updates = true

# Backup settings
backup-time = 300
blockdb-backup-time = 60
backup-location = levels/backups

# Review settings
review-cooldown = 600

# IRC bot settings
irc = false
irc-port = 6697
irc-server = irc.esper.net
irc-nick = ForgeBot
irc-channel = #changethis
irc-opchannel = #changethistoo
irc-identify = false
irc-nickserv-name = NickServ
irc-password = 
irc-ssl = false
irc-ignored-nicks = 
irc-player-titles = true
irc-show-world-changes = false
irc-show-afk = false
irc-command-prefix = .x
irc-controller-verify = HalfOp
irc-controller-rank = 100

# Database settings
UseMySQL = false
host = 127.0.0.1
SQLPort = 3306
Username = root
Password = password
DatabaseName = MCZallDB
Pooling = true

# Tablist settings
tablist-rank-sorted = true
tablist-global = true
tablist-bots = false

# Chat settings
parse-emotes = true
dollar-before-dollar = true
disabledstandardtokens = 
profanity-filter = false
profanity-replacement = *
host-state = Alive

# Colors settings
defaultColor = &e
irc-color = &5
help-syntax-color = &a
help-desc-color = &e
warning-error-color = &c

# Messages settings
cheapmessage = true
cheap-message-given =  is now invincible
custom-ban-message = You're banned!
custom-shutdown-message = Server shutdown. Rejoin in 10 seconds.
custom-promote-message = &6Congratulations for working hard and getting &2PROMOTED!
custom-demote-message = &4DEMOTED! &6We're sorry for your loss. Good luck on your future endeavors! &1:'(
custom-restart-message = Server restarted. Sign in again and rejoin.
custom-whitelist-message = This is a private server!
default-login-message = connected
default-logout-message = disconnected

# Logging settings
log-notes = true
file-logging = True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True
console-logging = True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True

# Spam control settings
mute-on-spam = false
spam-messages = 8
spam-mute-time = 60
spam-counter-reset-time = 5
cmd-spam-check = true
cmd-spam-count = 25
cmd-spam-block-time = 30
cmd-spam-interval = 1
block-spam-check = true
block-spam-count = 200
block-spam-interval = 5
ip-spam-check = true
ip-spam-count = 10
ip-spam-block-time = 180
ip-spam-interval = 60

# Env settings
Weather = -1
EdgeLevel = -1
SidesOffset = -1
CloudsHeight = -1
MaxFog = -1
clouds-speed = -1
weather-speed = -1
weather-fade = -1
skybox-hor-speed = -1
skybox-ver-speed = -1
HorizonBlock = 255
EdgeBlock = 255
ExpFog = -1
CloudColor = 
FogColor = 
SkyColor = 
ShadowColor = 
LightColor = 
SkyboxColor = 


                """

                os.mkdir(f"{server_folder}\\properties")

                server_properties_file = f"{server_folder}\\properties\\server.properties"
                with open(server_properties_file, "w") as f:
                    f.write(main_properties)
                time.sleep(1)
                if os.path.exists(server_properties_file):
                    try:
                        with open(server_properties_file, "r") as f:
                            lines = f.readlines()

                        # Modify line 63
                        lines[62] = f"server-name = {server_name}\n"  # Assuming line 63 is indexed at 62

                        # Write back to the file
                        with open(server_properties_file, "w") as f:
                            f.writelines(lines)
                    except Exception as e:
                        print(f"Error: Failed to edit server.properties file: {e}")
                else:
                    print("Error: server.properties file not found.")

                # Repopulate the server list
                self.populate_server_list()
            else:
                print("Error: No assets found in the latest release.")
        else:
            print("Error: Failed to fetch latest release information from GitHub.")

    def launch_server(self):
        selected_server = self.server_list.currentItem().text()
        server_path = f"{os.environ.get('USERPROFILE')}\\Classicube Servers\\{selected_server}"

        # Assuming the executable file is named "MCGalaxy.exe" in each server folder
        server_exe = f"{server_path}\\MCGalaxy.exe"

        if os.path.isfile(server_exe):
            subprocess.Popen(server_exe)
        else:
            print(f"Error: Cannot find 'MCGalaxy.exe' in '{selected_server}'.")

    def delete_server(self):
        selected_server = self.server_list.currentItem().text()
        server_path = f"{os.environ.get('USERPROFILE')}\\Classicube Servers\\{selected_server}"

        # Prompt user confirmation
        reply = QMessageBox.question(self, 'Delete Server', f"Are you sure you want to delete '{selected_server}'?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            reply_again = QMessageBox.question(self, 'Delete Server', f"Are you REALLY sure you want to delete '{selected_server}'?",
                                                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply_again == QMessageBox.Yes:
                try:
                    shutil.rmtree(server_path)
                    print(f"Server '{selected_server}' deleted successfully.")
                except Exception as e:
                    print(f"Error: Failed to delete server '{selected_server}': {e}")
                self.populate_server_list()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ServerLauncher()
    window.show()
    sys.exit(app.exec())
