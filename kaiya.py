import socket
import requests
import json
import time
import threading

# Connection Information
network = "irc.rizon.net"
port = 6667
channel = "#fakku"
nickname = "Kaiya"
password = ""
api = "https://api.fakku.net/"

# Connect to network
irc = socket.socket()
irc.connect((network, port))

# Sending messages in channel
def sendMessage(msg, user, private):
	msg = msg.encode('utf-8')

	if(private == True):
		irc.send("PRIVMSG " + user + " :" + msg + "\r\n")
	else:
		irc.send("PRIVMSG " + channel + " :" + msg + "\r\n")

# Extract Nickname
def getNick(data):
	nick = data.split('!')[0]
	nick = nick.replace(':', ' ')
	nick = nick.replace(' ', '')
	nick = nick.strip(' \t\n\r')
	return nick

# Extract search terms
def getSearchTerms(data):
	terms = data.split('!search ')

	# Make sure the user gave terms
	if 2 == len(terms) and 1 <= len(terms[1].lstrip()):
		terms = terms[1].strip(' \t\n\r')
		return terms
	else:
		return False

# Get latest posts
def getNews():
	# Send index request to API to get front page posts.
	r = requests.get(api + "index")

	if(r.status_code) == 200:
		# Convert json to dictionary
		results = json.loads(r.text)

		# Get latest entry
		request = results['index'][0]

		# Check if news topic or content
		if 'topic_title' in request:
			if request["topic_time"] >= (time.time()-400):
				sendMessage("Hey sukebei! A new topic was posted. "+ request['topic_title'] +" : "+ request['topic_url'] +"", "", False)
		else:
			if request["content_date"] >= (time.time()-400):
				sendMessage("Hey sukebei! A new "+ request['content_category'] +" was posted. "+ request['content_name'] +" : "+ request['content_url'] +"", "", False)

	# call getNews() again in 300 seconds
	threading.Timer(300, getNews).start()

# Authenticate and join the channel
irc.send("NICK " + nickname + "\r\n")
irc.send("USER " + nickname + " " + nickname + " " + nickname + ":Python IRC\r\n")
irc.send("nickserv IDENTIFY %s\r\n" % password)
irc.send("JOIN " + channel + "\r\n")

# Begin news loop thing
getNews()

# Main loop
while True:
	data = irc.recv(4096)
	print data

	# Keep alive
	if data.find("PING") != -1:
		irc.send("PONG " + data.split()[1] + "\r\n")

	# Search
	if data.find(":!search") != -1:
		private = True

		terms = getSearchTerms(data)

		if terms == False:
			sendMessage("You typed the command in wrong... bakka...", getNick(data), private)
		else:
			sendMessage("Hmf~ fine "+getNick(data)+", hold on while I search for you...", getNick(data), private)

			# Send search request to API.
			r = requests.get(api + "search/" + str(terms))

			# Check if API call failed.
			if(r.status_code) != 200:
				sendMessage("I encountered an error, try again later bakka.", getNick(data), private)
			else:
				# Convert json to dictionary
				results = json.loads(r.text)

				sendMessage("Hey "+getNick(data)+" sukebei... I found those things for you... You better like them.", getNick(data), private)
				for request in results['content']:
					sendMessage(request['content_name'] + " : " + request['content_url'], getNick(data), private)

	# About the bot
	if data.find(":!about") != -1:
		if data.find(nickname + " :!about") != -1:
			private = True
		else:
			private = False
		sendMessage("My name is "+nickname+". You can use me to find things on Fakku for you. I was created by Kisuka.", getNick(data), private)

	# Help
	if data.find(":!help") != -1:
		if data.find(nickname + " :!help") != -1:
			private = True
		else:
			private = False
		sendMessage("Try using the !search <terms> command bakka.", getNick(data), private)