from app import create_app

app = create_app()

if __name__ == "__main__":
    print(
        f"Starting the defects-over-time service on port 5000"
    )
    app.run(port=5000, host="0.0.0.0")
