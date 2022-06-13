import socket
import urllib.request
def hostname_resolves(hostname):
	try:
		socket.gethostbyname(hostname)
		return 1
	except socket.error:
		return 0
urllib.request.urlopen("https://www.volunteermatch.org").getcode()
try:
	urllib.request.urlopen("https://www.volunteermatch.org").getcode()
	print("YUP!")
except Exception:
	print("nope")
	pass
