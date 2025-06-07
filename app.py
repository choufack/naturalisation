from flask import Flask
from api import api_eligibility

# Initialisation de l'application Flask
app = Flask(__name__)
app.register_blueprint(api_eligibility, url_prefix='/api')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
