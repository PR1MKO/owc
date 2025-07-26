from app import create_app

app = create_app()

if __name__ == "__main__":
    # Explicitly set the host and port to ensure the app is
    # accessible on http://127.0.0.1:5000
    app.run(host="127.0.0.1", port=5000, debug=True)
