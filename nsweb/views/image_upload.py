from flask import request

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['the_file']
        f.save('/var/www/uploads/uploaded_file.txt')

'''
forget this. Re-implementing flask-uploads. I looked at code and its doing exactly
 what I am now and they have testing harness and safety stuff! Let's use that instead. 
'''