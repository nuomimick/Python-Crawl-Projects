def send_mail(send_from, send_to, subject, text, files=None,server="xxx.xxx.com"):
    assert isinstance(send_to, list),'send_to should be list'

    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = COMMASPACE.join(send_to)
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
            
    smtp = smtplib.SMTP(server)
    smtp.sendmail(send_from, send_to, msg.as_string())
    smtp.close()
