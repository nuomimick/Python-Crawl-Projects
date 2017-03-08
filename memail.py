def send_mail(send_from, send_to, send_cc,send_bcc,subject, text, files=None,
              server="xxx.xxx.com"):
    assert isinstance(send_to, list),'send_to should be list'

    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = COMMASPACE.join(send_to)
    msg['Cc'] = COMMASPACE.join(send_cc) if send_cc else None
    msg['Bcc'] = COMMASPACE.join(send_bcc) if send_bcc else None
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach(MIMEText(text, 'html'))

    for f in files:
        with open(f, "rb") as file:
            part = MIMEApplication(
                file.read(),
                Name=basename(f)
            )
            part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
            msg.attach(part)

    send_list = send_to
    if not send_cc:
    	send_list.append(send_cc)
    if not send_bcc:
    	send_list.append(send_bcc)

    smtp = smtplib.SMTP(server)
    smtp.sendmail(send_from, send_list, msg.as_string())
    smtp.close()
    
sender = 'xxx.xxx.com'
receivers = ['xxx.xxx.com']
ccs = ['xxx.xxx.com']

if receivers is not None:
    print ('sending mail to :')
    print (receivers)
    send_mail(sender,receivers,ccs,None,
              today.strftime('%Y-%m-%d') + " ToolNames",
	'''
	<html>
	<body>
	<h2>Get the toolnames from the file</h2>
	</body>
	</html>
	''',
	[filename]
	)
