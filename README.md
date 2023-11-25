# ColorSchemeEditor
Converts the RGB images to CMYK and HSV color schemes.
Also there are red, blue, and green filters wich shows only the red, blue and green component of the image respectively.

### Download the zip file or colne the repo to check the project


 To clone the repository:

```bash
git clone https://github.com/JainishParekh/ColorSchemeEditor.git
```

 or you can download the zip folder directly.

### You are required to have the python3

### Create the virtual Envirnment

Then you can create the virtual the envirnment in windows using following command.

Here, need to replace the **virtal-env-name** with **name you like for your virtual envirnment**.


```bash
python -m venv virtal-env-name
```

 Then enter the virtual envirnment in windows using the following command.

```bash
virtal-env-name/Scripts/activate
```

 To deactivate the virtual envirnment

```bash
deactivate
```

### To download the required libraries

 Then you can download the requirements directly fromt the requirements.txt file using the following command.

```bash
pip install -r requirements.txt
```

### To run the web app

```bash
python app.py
```

 Open the app on the local port after making sure of following code line in the *app.py file*

```python
app.run(debug=True , port = 8000)
```

### Description of the Web app

In this web app you can select the image that you need to transform, then you can select the required filters after which you can click on the submit button. 

These will give the success message if the image was converted then you can download the newly update image after clicking here. 
