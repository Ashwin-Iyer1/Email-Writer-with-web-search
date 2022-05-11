import os
import smtplib
import imghdr
from email.message import EmailMessage

EMAIL_ADDRESS = os.environ.get('EMAIL_USER')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASS')
contacts = ['']
contactsfile = open(r"C:\Users\ashwin\Downloads\contacts.txt")
with open(r"C:\Users\ashwin\Downloads\contacts.txt") as f:
	contacts = [line.strip() for line in f]
	print(contacts)
msg = EmailMessage()
msg['Subject'] = 'idek'
msg['From'] = EMAIL_ADDRESS
msg['To'] = contacts
msg.set_content('hello')
msg.set_content('Image attached...')

files = [r'C:\Users\ashwin\Pictures\Saved Pictures\coupon.png']

for file in files:
	with open(file, 'rb') as f:
		file_data = f.read()
		file_name = f.name
		if imghdr.what(file_name) != None:
			file_type = imghdr.what(f.name)
			msg.add_attachment(file_data, maintype='image', subtype=file_type, filename=file_name)
		else:
			msg.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)

with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
 smtp.ehlo()
 smtp.starttls()
 smtp.ehlo()
	
 smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
 smtp.send_message(msg)