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
        

def convertToHSV(img):
    # Ensure the input image is in the BGR color space
    b, g, r = cv2.split(img)

    # Normalize to the range [0, 1]
    b, g, r = b / 255.0, g / 255.0, r / 255.0

    # Compute the maximum and minimum values for each pixel
    max_channel = np.maximum.reduce([r, g, b])
    min_channel = np.minimum.reduce([r, g, b])

    # Compute the value (V) channel
    v = max_channel

    # Compute the saturation (S) channel
    s = np.where(max_channel != 0.0, (max_channel - min_channel) / max_channel, 0.0)

    # Compute the hue (H) channel
    delta = max_channel - min_channel
    h = np.where(delta != 0.0,
                 np.where(max_channel == r, (g - b) / delta + 6.0 * (g < b),  # Red is the dominant color
                          np.where(max_channel == g, (b - r) / delta + 2.0,  # Green is the dominant color
                                   (r - g) / delta + 4.0)),  # Blue is the dominant color
                 0.0)

    # Scale the hue to the range [0, 360]
    h = h * 60.0

    # Stack the H, S, V channels to get the HSV image
    hsv = np.stack((h, s, v), axis=-1)

    # Convert H, S, V channels to the range [0, 255]
    hsv = (hsv * [1.0 / 2.0, 255.0, 255.0]).astype(np.uint8)

    return hsv




def highlightRed(img):
    hsv = convertToHSV(img)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    lower_red = np.array([160,100,50])
    upper_red = np.array([180,255,255])

    # create a mask using the bounds set
    mask = cv2.inRange(hsv, lower_red, upper_red)
    # create an inverse of the mask
    mask_inv = cv2.bitwise_not(mask)
    # Filter only the red colour from the original image using the mask(foreground)
    res = cv2.bitwise_and(img, img, mask=mask)
    # Filter the regions containing colours other than red from the grayscale image(background)
    background = cv2.bitwise_and(gray, gray, mask = mask_inv)
    # convert the one channelled grayscale background to a three channelled image
    background = np.stack((background,)*3, axis=-1)
    # add the foreground and the background
    added_img = cv2.add(res, background)    

    return added_img

def highlightGreen(img):
    # hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    hsv = convertToHSV(img)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    lower_green = np.array( [30, 50, 50])
    upper_green = np.array( [90, 255, 255])

    # create a mask using the bounds set
    mask = cv2.inRange(hsv, lower_green, upper_green)
    # create an inverse of the mask
    mask_inv = cv2.bitwise_not(mask)
    # Filter only the red colour from the original image using the mask(foreground)
    res = cv2.bitwise_and(img, img, mask=mask)
    # Filter the regions containing colours other than red from the grayscale image(background)
    background = cv2.bitwise_and(gray, gray, mask = mask_inv)
    # convert the one channelled grayscale background to a three channelled image
    background = np.stack((background,)*3, axis=-1)
    # add the foreground and the background
    added_img = cv2.add(res, background)    

    return added_img

def highlightBlue(img):
    hsv = convertToHSV(img)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    lower_red = np.array([80, 168, 166])
    upper_red = np.array([120,255,255])

    # create a mask using the bounds set
    mask = cv2.inRange(hsv, lower_red, upper_red)
    # create an inverse of the mask
    mask_inv = cv2.bitwise_not(mask)
    # Filter only the red colour from the original image using the mask(foreground)
    res = cv2.bitwise_and(img, img, mask=mask)
    # Filter the regions containing colours other than red from the grayscale image(background)
    background = cv2.bitwise_and(gray, gray, mask = mask_inv)
    # convert the one channelled grayscale background to a three channelled image
    background = np.stack((background,)*3, axis=-1)
    # add the foreground and the background
    added_img = cv2.add(res, background)    

    return added_img

   

def processImage(filename , operation):
    image = cv2.imread(f"static/uploads/{filename}")
    if operation == 'ccmyk':
        new_image = convertToCMYK(image)
    elif operation == 'chsv':
        new_image = convertToHSV(image)
    elif operation == 'hRed':
        new_image = highlightRed(image)
    elif operation == 'hGreen':
        new_image = highlightGreen(image)
    elif operation == 'hBlue':
        new_image = highlightBlue(image)
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
        ori_filename = filename
        #print('upload_image filename: ' + filename)
        processImage(filename, operation)
        flash(f"""Your image has been processed and is available <a href='static/final/{filename}' target='_blank'>here</a>
              & the original image is <a href='static/uploads/{filename}' target='_blank'>here</a>""")
        return render_template('index.html', filename=filename)
    else:
        flash('Allowed image types are - png, jpg, jpeg, gif')
        return redirect(request.url)

 
if __name__ == "__main__":
    app.run(debug=True , port=5001)
    # app.run(debug=False , host='0.0.0.0')