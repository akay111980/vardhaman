import requests
import json

import os
from io import BytesIO
from django.template.loader import get_template
import xhtml2pdf.pisa as pisa
import uuid
from django.conf import settings
from django.utils import timezone

# notification sending Function.
def sendNotification(registerToken , messageTitle , messageBody):

    reqUrl = "https://exp.host/--/api/v2/push/send"

    headersList = {
        "Accept": "application/json",
        "Accept-encoding" : "gzip, deflate",
        "Content-Type" : "application/json",
    }

    payload = json.dumps({
        "to": registerToken,
        "sound": "default",
        "title": messageTitle,
        "body": messageBody
    })

    response = requests.request("POST", reqUrl, data=payload,  headers=headersList)
    print(response.text)
    

# Function is used to Upload Invoice in the folder
def savePdf(param: dict):
    template = get_template("pdf_template.html")
    html = template.render(param)

    # Generate a UUID for the file name
    fileName = str(uuid.uuid4())

    # Get the current date in YYYYMMDD format
    dateNow = timezone.now().strftime("%Y%m%d")

    # Generate the directory path
    directory_path = os.path.join(settings.MEDIA_ROOT, 'invoices', dateNow)

    # Create the directory if it doesn't exist
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

    # Generate the file path
    file_path = os.path.join(directory_path, f"{fileName}.pdf")
    
    # Render HTML to PDF and save to the file
    try:
        with open(file_path, 'wb+') as output:
            pdf = pisa.pisaDocument(BytesIO(html.encode('UTF-8')), output)
        
        if pdf.err:
            # If there's an error during PDF generation, return False
            return '', False
        else:
            # If PDF generation is successful, return the file name and True
            return fileName, True

    except Exception as e:
        # If any exception occurs, print the error and return False
        print(e)
        return '', False
    
    
# check the num indicator
def sign_indicator(amount):
    if amount - int(amount) < 0.5:
        return True
    else:
        return False
