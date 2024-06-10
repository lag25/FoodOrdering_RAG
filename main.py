import sys

# Append project root to PYTHONPATH
sys.path.append('.')

# Import and run your Flask app
from backend.whatsapp.get_messages import app

if __name__ == "__main__":
    app.run(debug=False)
