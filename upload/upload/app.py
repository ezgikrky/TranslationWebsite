import os
from flask import Flask, render_template, request, redirect, abort, flash, url_for
from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm
from wtforms import FileField,SubmitField
from werkzeug.utils import secure_filename
import os
import requests, os, uuid
from dotenv import load_dotenv
load_dotenv()
import string

app = Flask(__name__)
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
import time
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import os

@app.route('/')
def upload_file():
   return render_template('index.html')

@app.route( '/uploader',methods = ['GET', 'POST'])
def upload_file2():
   liste = []
   if request.method == 'POST':
      f = request.files['file']
      f.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),"images" ,secure_filename(f.filename)))


         # Get Configuration Settings
      #load_dotenv()  # sanal ortamdan gerekli şeyleri alır
      endpoint = os.getenv('COG_SERVICE_ENDPOINT')
      key = os.getenv('COG_SERVICE_KEY')

         # Authenticate Computer Vision client
         # CVC fotoğrafı görmesine ve neyin nerede olduğunu algılamasına yarar
      computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(key))
         # Extract test

      images_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".\images")
      read_image_path = os.path.join(images_folder, f.filename)

      with open(read_image_path, "rb") as image:
         # Call the API
         # okuma işleminin sonucunu almak için kullanılır
         read_response = computervision_client.read_in_stream(image, raw=True)

      # Get the operation location (URL with an ID at the end)
      # okuma sonucuna erişmek için 'GetReadResult' işleminde kullanılması gereken URL'yi içerir.
      # urlyi aldı
      read_operation_location = read_response.headers["Operation-Location"]
      # Grab the ID from the URL
      # urlyi ayıkladı
      operation_id = read_operation_location.split("/")[-1]

      # Retrieve the results
      # sonuçlar
      while True:
         read_result = computervision_client.get_read_result(operation_id)
         if read_result.status.lower() not in ['notstarted', 'running']:
            break
         time.sleep(1)

      # Get the detected text
      # metin algılanırsa
      if read_result.status == OperationStatusCodes.succeeded:
         # sonucu analiz eder ve okur
         for page in read_result.analyze_result.read_results:
            # satır satır yaz
            for line in page.lines:
               # Print line
               print(line.text)
               liste.append(line.text)
               liste.append(" ")
   print("\n")

   metin =liste
   Text = ""
   for i in metin:
       if i not in string.punctuation:
           Text += i
   print(Text)
   return render_template("text.html",isim=Text)


@app.route('/text', methods=['GET'])
def index():
    return render_template('text.html')

@app.route('/translate', methods=['GET','POST'])
def index_post():

    original_text = request.form['text']
    target_language = request.form['language']


    key = os.environ['KEY']
    print(key)
    endpoint = os.environ['ENDPOINT']
    location = os.environ['LOCATION']


    path = '/translate?api-version=3.0'

    target_language_parameter = '&to=' + target_language

    constructed_url = endpoint + path + target_language_parameter


    headers = {
        'Ocp-Apim-Subscription-Key': key,
        'Ocp-Apim-Subscription-Region': location,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }

    body = [{ 'text': original_text }]

    translator_request = requests.post(constructed_url, headers=headers, json=body)

    translator_response = translator_request.json()


    translated_text = translator_response[0]['translations'][0]['text']

    return render_template(
        'result.html',
        translated_text=translated_text,
        original_text=original_text,
        target_language=target_language
    )




if __name__=="__main__":
    app.run(debug=True)
