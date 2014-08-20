from flask import render_template

def error_page(message):
    return render_template('shared/error.html.slim', message=message)