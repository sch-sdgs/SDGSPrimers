#!flask/bin/python
from app.primers import app, db
import os
import app.config as config

if __name__ == "__main__":


    print "starting app"

    if not os.path.isfile(config.database_path):
        print "creating primaers database"
        db.create_all()


    app.run(debug=True, host='10.182.131.21', port=5004)
