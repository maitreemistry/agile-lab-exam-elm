import os
from functools import wraps
from typing import Callable

from flask import Flask, flash, redirect, render_template, request, session, url_for


class LeaveManager:
    def __init__(self, leave_balances: dict[str, int]):
        self.leave_balances = leave_balances.copy()

    def leaves_left(self, employee: str) -> int:
        return self.leave_balances[employee]

    def request_leave(self, employee: str, days: int) -> bool:
        if days <= 0:
            raise ValueError("Leave days must be positive")

        if days > self.leaves_left(employee):
            return False

        self.leave_balances[employee] -= days
        return True


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "local-development-secret"),
        APP_USERNAME=os.environ.get("APP_USERNAME", "admin"),
        APP_PASSWORD=os.environ.get("APP_PASSWORD", "leave123"),
    )
    if test_config:
        app.config.update(test_config)

    leave_manager = LeaveManager({"Rushvi": 5})

    def login_required(view: Callable) -> Callable:
        @wraps(view)
        def wrapped(*args, **kwargs):
            if "employee" not in session:
                return redirect(url_for("login"))
            return view(*args, **kwargs)

        return wrapped

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form.get("username", "")
            password = request.form.get("password", "")
            if (
                username == app.config["APP_USERNAME"]
                and password == app.config["APP_PASSWORD"]
            ):
                session["employee"] = "Rushvi"
                return redirect(url_for("home"))
            flash("Invalid username or password.", "error")

        return render_template("login.html"), (
            401 if request.method == "POST" else 200
        )

    @app.route("/")
    @login_required
    def home():
        employee = session["employee"]
        return render_template(
            "index.html",
            employee=employee,
            leaves_left=leave_manager.leaves_left(employee),
        )

    @app.route("/request-leave", methods=["POST"])
    @login_required
    def request_leave():
        try:
            days = int(request.form.get("days", ""))
            approved = leave_manager.request_leave(session["employee"], days)
        except ValueError:
            flash("Enter a valid positive number of leave days.", "error")
        else:
            if approved:
                flash(f"Leave request approved for {days} day(s).", "success")
            else:
                flash("Not enough leaves left for this request.", "error")

        return redirect(url_for("home"))

    @app.route("/logout", methods=["POST"])
    def logout():
        session.clear()
        return redirect(url_for("login"))

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
