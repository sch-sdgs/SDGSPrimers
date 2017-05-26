#!flask/bin/python
from app.primers import app

if __name__ == "__main__":
    app.run(debug=True, host='10.182.155.26', port=5001)
