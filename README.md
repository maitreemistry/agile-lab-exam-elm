# Employee Leave Management

A basic Flask app with a demo login and a five-day leave balance.

## Run locally

```powershell
python -m pip install -r requirements.txt
python app.py
```

Open <http://localhost:5000>. Demo credentials: `admin` / `leave123`.

## Build and run with Docker

From the project directory:

```powershell
docker build -t employee-leave .
docker run --rm -p 5001:5000 employee-leave
```

Open <http://localhost:5001>. `-p 5001:5000` maps host port 5001 to the
container's port 5000.

## Tests

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest -v
```

## Selenium login check

Start the app locally or with Docker, install a compatible Chrome browser,
then run:

```powershell
python selenium_login_test.py
```

The script uses Selenium Manager to locate/download a matching ChromeDriver.
Set `APP_URL` if the app is not at `http://127.0.0.1:5000`.