from flask import Flask
from app.routes import main  

app = Flask(__name__)

# Register the Blueprint
app.register_blueprint(main)

if __name__ == '__main__':
    app.run(debug=True)
