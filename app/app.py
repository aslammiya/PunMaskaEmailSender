from flask import Flask, request, render_template
import os
import requests
from werkzeug.utils import secure_filename
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import smtplib
import imaplib
import csv
import traceback

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def create_email_content_style(name):
    if name != " ":
        name = name.strip()
        greeting = f"Hey {name},"
    else:
        greeting = "Hey,"
    html_content = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                background-color: #f2f2f2;
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
            }}

            .email-container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background-color: #fff;
                border-radius: 8px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }}

            p {{
                font-size: 18px;
                color: #555;
            }}

            p.bold {{
                font-size: 20px;
                font-weight: bold;
                color: #7443f6;
            }}

            a.button {{
                display: inline-block;
                background-color: #7443f6;
                color: #fff;
                font-size: 16px;
                text-align: center;
                border-radius: 4px;
                padding: 8px 16px;
                margin-top: 5px;
                text-decoration: none;
                font-weight: bold;
                transition: background-color 0.2s ease;
            }}

            a.button:hover {{
                background-color: #5b2ee8;
            }}

            p.thanks {{
                font-size: 18px;
                margin-top: 20px;
            }}

            p.signature {{
                font-size: 18px;
                font-weight: bold;
                color: #7443f6;
                margin-top: 0;
                margin-bottom: 0;
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <p class="bold">{greeting}</p>
            <p>Do you know, Punmaska has taken over as <span style="color: #7443f6;">Desh ka Butter</span>?! 😱🤯</p>
            <p>I'm Aayushi from Punmaska, here to spread some pun-tastic vibes on your Instagram! 🚀</p>
            <a href="https://www.punmaska.com/coming-soon-03-1" class="button">🤌 Check out our Pun-Intended Pitch! 🤌</a>
            <p class="thanks">Hoping to see you on the other side of the screen! 💻</p>
            <p class="signature">Cheers,</p>
            <p class="signature">Punmaska! ☕</p>
        </div>
    </body>
    </html>
'''
    return html_content

def create_email_content(name):
    if name != " ":
        name = name.strip()
        greeting = f"Hey {name},"
    else:
        greeting = "Hey,"
    html_content = f'''
        <!DOCTYPE html>
        <html>
        <head>
        </head>
        <body>
            <div>
                <p>{greeting}</p>
                <p>Do you know, Punmaska has replaced Amul butter as Desh ka Butter?! 😱🤯</p>
                <p>I'm Aayushi from Punmaska. Here, to boost your Instagram! 🚀</p>
                <p>Click on the below link to have a look at our Pun intended pitch! 🤌</p>
                <a href="https://www.punmaska.com/coming-soon-03-1">https://www.punmaska.com/coming-soon-03-1</a>
                <br><p>Hoping to see you on the other side of the screen! 💻</p>
                <p>Cheers,<br>Punmaska! ☕</p>
            </div>
        </body>
        </html>
    '''
    return html_content

def send_email_with_attachments(subject, to_email, html_content, pdf_files=None, moveToSent=True, sentPdf=True, errAcc=[]):
    try:
        msg = MIMEMultipart()
        msg.set_unixfrom('author')
        msg['From'] = 'Pun Maska <createwith@punmaska.com>'
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(html_content, 'html'))

        if sentPdf == True:
            if pdf_files:
                for pdf_file in pdf_files:
                    with open(pdf_file, "rb") as f:
                        part = MIMEApplication(f.read(), Name=pdf_file)
                        part['Content-Disposition'] = f'attachment; filename="{pdf_file}"'
                        msg.attach(part)

        mailserver = smtplib.SMTP_SSL('smtpout.secureserver.net', 465)
        mailserver.ehlo()
        mailserver.login('createwith@punmaska.com', 'Punmaska@123')
        mailserver.sendmail('createwith@punmaska.com', to_email, msg.as_string())
        mailserver.quit()

        if moveToSent == True:
            with imaplib.IMAP4_SSL('imap.secureserver.net') as imap_server:
                username = 'createwith@punmaska.com'
                password = 'Punmaska@123'
                imap_server.login(username, password)
                imap_server.select("Sent")
                imap_server.append("Sent", None, None, msg.as_bytes())

        print('Email sent',to_email)

    except smtplib.SMTPException as smtp_ex:
        print(f'An error occurred while sending the email: {smtp_ex}')
        traceback.print_exc()
        errAcc.append(to_email)
    except Exception as e:
        print(f'An error occurred while sending the email: {e}')
        traceback.print_exc()
        errAcc.append(to_email)
    
def read_recipients_from_csv(csv_file):
    recipients = []
    try:
        with open(csv_file, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                name = f" {row['Name'].strip()}"
                email = row['Email'].strip()
                recipients.append((name, email))
    except Exception as e:
        print(f'An error occurred while reading the CSV file: {e}')

    return recipients


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'csv_file' not in request.files:
            return "No file part"
        
        file = request.files['csv_file']

        if file.filename == '':
            return "No selected file"
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            # Update the recipients list to use the uploaded CSV file
            recipients = read_recipients_from_csv(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            subject = "You and Punmaska > Chai and Bunmaska ☕🚀"
            pdf_files = [r"Punmaska_Overview.pdf"]
            moveToSent = False
            sentPdf = False
            errAcc = []

            for name, email in recipients:
                try:
                    html_content = create_email_content(name)
                    html_content = html_content.replace("{name}", name)
                    send_email_with_attachments(subject, email, html_content, pdf_files, moveToSent, sentPdf, errAcc)
                except Exception as e:
                    print(f"Error sending email to {email}: {e}")
                    errAcc.append(email)

            if errAcc:
                sendTelegramMessage(errAcc)
            else:
                sendTelegramMessage("All Done")

            return "Emails sent successfully"
    
    return render_template('index.html')

def sendTelegramMessage(message):
    bot_token = "6289896747:AAEReBXOFz83XIxkviNAZMIMfuMIOS2XGdw"
    id = 839567554
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={id}&text={message}"
        rsp = requests.get(url)
        rsp.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error sending Telegram message: {e}")

if __name__ == '__main__':
    app.run(debug=True)
