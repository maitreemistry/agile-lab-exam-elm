import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def local_app_is_running() -> bool:
    try:
        with urllib.request.urlopen(
            "http://127.0.0.1:5000/login", timeout=1
        ):
            return True
    except (urllib.error.URLError, TimeoutError):
        return False


def start_local_app() -> subprocess.Popen | None:
    if local_app_is_running():
        return None

    app_path = Path(__file__).with_name("app.py")
    process = subprocess.Popen(
        [sys.executable, str(app_path)],
        cwd=app_path.parent,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    login_url = "http://127.0.0.1:5000/login"
    deadline = time.monotonic() + 15

    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(
                f"The local app exited with status {process.returncode}."
            )
        try:
            with urllib.request.urlopen(login_url, timeout=1):
                return process
        except (urllib.error.URLError, TimeoutError):
            time.sleep(0.25)

    process.terminate()
    process.wait()
    raise RuntimeError(f"The local app did not start at {login_url}.")


def stop_local_app(process: subprocess.Popen | None) -> None:
    if process is None or process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()


def main():
    configured_url = os.environ.get("APP_URL")
    app_url = (configured_url or "http://127.0.0.1:5000").rstrip("/")
    local_app = None
    driver = None
    if configured_url is None:
        local_app = start_local_app()

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    try:
        driver = webdriver.Chrome(options=options)
        driver.get(f"{app_url}/login")
        driver.find_element(By.ID, "username").send_keys("admin")
        driver.find_element(By.ID, "password").send_keys("leave123")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "leave-balance"))
        )
        assert "Leaves left: 5" in driver.find_element(
            By.ID, "leave-balance"
        ).text
        print("Successful login test passed.")

        driver.find_element(
            By.CSS_SELECTOR, "form[action='/logout'] button"
        ).click()
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "username"))
        )
        driver.find_element(By.ID, "username").send_keys("admin")
        driver.find_element(By.ID, "password").send_keys("wrong-password")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        error = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "[role='alert']"))
        )
        assert "Invalid username or password." in error.text
        assert driver.current_url.endswith("/login")
        print("Invalid credentials test passed.")
    finally:
        if driver is not None:
            driver.quit()
        stop_local_app(local_app)


if __name__ == "__main__":
    main()
