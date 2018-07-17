from nsweb.core import create_app, app


# set up the flask app
create_app()


def main():

    app.run(debug=app.debug, port=5001, host='0.0.0.0')


if __name__ == "__main__":
    main()
