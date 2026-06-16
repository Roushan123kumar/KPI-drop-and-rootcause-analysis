import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class AlertEngine:

    def __init__(self, config):
        """
        config = {
            "email": {
                "sender": "pro411937@gmail.com",
                "password": "qzhlzmcwabyznztl",  # NOT your real password
                "receiver": "roushanjsr2033@gmail.com"
    
            }
        }
        """
        self.config = config

    # ==================================================
    # EMAIL ALERT (Gmail SMTP)
    # ==================================================
    def send_email(self, subject, body):
        try:
            cfg = self.config["email"]

            msg = MIMEMultipart()
            msg["From"] = cfg["sender"]
            msg["To"] = cfg["receiver"]
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain"))

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(cfg["sender"], cfg["password"])
                server.sendmail(cfg["sender"], cfg["receiver"], msg.as_string())

            return True, "Email sent successfully"
        except Exception as e:
            return False, str(e)