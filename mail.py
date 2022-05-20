import os
import smtplib
import imghdr
from email.message import EmailMessage
from subdirectory_finder import emails
EMAIL_ADDRESS = os.environ.get('EMAIL_USER')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASS')
contacts = emails
msg = EmailMessage()
msg['Subject'] = str(input("What would you like the subject to be: "))
msg['From'] = EMAIL_ADDRESS
msg['To'] = contacts
message = input('What would you like the content to be:\n ')
msg.set_content(message)
if len(contacts) == 0:
	print("no emails found")
	exit()
# files = [r'C:\Users\ashwin\Pictures\Saved Pictures\coupon.png']
# if(len(files) != 0):
# 	msg.set_content('Image attached...')
# for file in files:
# 	with open(file, 'rb') as f:
# 		file_data = f.read()
# 		file_name = f.name
# 		if imghdr.what(file_name) != None:
# 			file_type = imghdr.what(f.name)
# 			msg.add_attachment(file_data, maintype='image', subtype=file_type, filename=file_name)
# 		else:
# 			msg.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)

with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
 smtp.ehlo()
 smtp.starttls()
 smtp.ehlo()
	
 smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
 smtp.send_message(msg)