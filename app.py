from flask import Flask, flash, request, redirect, url_for, render_template
import urllib.request
import os
import cv2
import numpy as np
from werkzeug.utils import secure_filename
 
app = Flask(__name__)
 
UPLOAD_FOLDER = 'static/uploads'
 
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
 
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
 
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convertToCMYK(img):
    try:
        # Create float
        bgr = img.astype(float)/255.

        # Extract channels
        with np.errstate(invalid='ignore', divide='ignore'):
            K = 1 - np.max(bgr, axis=2)
            C = (1-bgr[...,2] - K)/(1-K)
            M = (1-bgr[...,1] - K)/(1-K)
            Y = (1-bgr[...,0] - K)/(1-K)

        # Convert the input BGR image to CMYK colorspace
        CMYK = (np.dstack((C,M,Y,K)) * 255).astype(np.uint8)
        
        return CMYK
    except:
        print(type(img))


def rgb_to_hsv(r,g,b):
    r = r / 255.0; 
    g = g / 255.0; 
    b = b / 255.0; 
  
    # h, s, v = hue, saturation, value 
    cmax = max(r, max(g, b)); # maximum of r, g, b 
    cmin = min(r, min(g, b)); # minimum of r, g, b 
    diff = cmax - cmin; # diff of cmax and cmin. 
    h,s = -1,-1
  
    # if cmax and cmax are equal then h = 0 
    if cmax == cmin: 
        h = 0; 
  
    # if cmax equal r then compute h 
    elif cmax == r:
        h = (60 * ((g - b) / diff) + 360 % 360); 
  
    # if cmax equal g then compute h 
    elif (cmax == g) :
        h = (60 * ((b - r) / diff) + 120 % 360); 
  
    # if cmax equal b then compute h 
    elif (cmax == b) :
        h = (60 * ((r - g) / diff) + 240 % 360); 
  
    # if cmax equal zero 
    if (cmax == 0) :
        s = 0; 
    else:
        s = (diff / cmax) * 100; 
  
    # compute v 
    v = cmax * 100; 
    
    return (h,s,v)


def convertToHSV(img):
    
    h,w,c = img.shape
    
    new_image = []
    for y in range(h):
        each_row = []
        for x in range(w):
            (r,g,b) = tuple(img[y,x])
            (h,s,v) = rgb_to_hsv(r,g,b) 
            each_row.append((h,s,v))
        new_image.append(each_row)
    
    new_image = np.array(new_image)
    
    return new_image
    
def redFilter(img):
    
    h,w,c = img.shape
    
    red_filtered_image = []
    
    # Iterate over each pixel in the original image
    for x in range(h):
        each_row = []
        for y in range(w):
            # Get the RGB values of the pixel
            (r, g, b) = tuple(img[x,y])
            each_row.append((0, 0, r))
        # Apply the red filter by setting the green and blue channels to 0
        red_filtered_image.append(each_row)  
    
    red_filtered_image = np.array(red_filtered_image)
    
    return red_filtered_image  

def greenFilter(img):
    h,w,c = img.shape
    
    red_filtered_image = []
    
    # Iterate over each pixel in the original image
    for x in range(h):
        each_row = []
        for y in range(w):
            # Get the RGB values of the pixel
            (r, g, b) = tuple(img[x,y])
            each_row.append((0, g, 0))
        # Apply the red filter by setting the green and blue channels to 0
        red_filtered_image.append(each_row)  
    
    red_filtered_image = np.array(red_filtered_image)
    
    return red_filtered_image      

def blueFilter(img):
    h,w,c = img.shape
    
    red_filtered_image = []
    
    # Iterate over each pixel in the original image
    for x in range(h):
        each_row = []
        for y in range(w):
            # Get the RGB values of the pixel
            (r, g, b) = tuple(img[x,y])
            each_row.append((b,0,0))
        # Apply the red filter by setting the green and blue channels to 0
        red_filtered_image.append(each_row)  
    
    red_filtered_image = np.array(red_filtered_image)
    
    return red_filtered_image      

def processImage(filename , operation):
    image = cv2.imread(f"static/uploads/{filename}")
    if operation == 'ccmyk':
        new_image = convertToCMYK(image)
    elif operation == 'chsv':
        new_image = convertToHSV(image)
    elif operation == 'red':
        new_image = redFilter(image)
    elif operation == 'green':
        new_image = greenFilter(image)
    elif operation == 'blue':
        new_image = blueFilter(image)
    newFilePath = 'static/final/' + filename
    print(newFilePath)
    cv2.imwrite(newFilePath, new_image)
        
 
@app.route('/')
def home():
    return render_template('index.html')
 
@app.route('/', methods=['POST'])
def edit():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    operation = request.form.get('operation')
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        #print('upload_image filename: ' + filename)
        processImage(filename, operation)
        flash(f"Your image has been processed and is available <a href='static/final/{filename}' target='_blank'>here</a>")
        return render_template('index.html', filename=filename)
    else:
        flash('Allowed image types are - png, jpg, jpeg, gif')
        return redirect(request.url)

 
if __name__ == "__main__":
    app.run(debug=True , port=5001)