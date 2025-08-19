import os
import pyotp
import flask
import time
from collections import defaultdict
from time import time as now

app = flask.Flask(__name__)

# Track failed attempts per client IP
failed_attempts = defaultdict(list)
BLOCK_DURATION = 300  # seconds
MAX_ATTEMPTS = 5

SECRET = os.environ.get("GITHUB_TOTP_SECRET")
API_KEY = os.environ.get("API_KEY")

if not SECRET:
    raise RuntimeError("NO SECRET")

totp = pyotp.TOTP(SECRET)

# Helper functions for rate limiting failed attempts
def is_blocked(client_ip):
    attempts = failed_attempts[client_ip]
    # Remove old attempts outside block duration
    failed_attempts[client_ip] = [t for t in attempts if now() - t < BLOCK_DURATION]
    if len(failed_attempts[client_ip]) >= MAX_ATTEMPTS:
        return True
    return False

def register_failed_attempt(client_ip):
    failed_attempts[client_ip].append(now())

def github_otp(request):
    args = request.args

    client_ip = request.remote_addr
    if is_blocked(client_ip):
        return ("Too many failed attempts. Try again later.", 403)

    service = args.get("service")
    key = request.headers.get("X-API-Key")
    if key != API_KEY:
        register_failed_attempt(client_ip)
        return ("Unauthorized", 403)

    if service and service.lower() == "github":
        code = totp.now()
        seconds_left = int(totp.interval - time.time() % totp.interval)
        return {"otp": code, "valid_for_seconds": seconds_left}
    else:
        return {"error": "unknown service"}, 400

@app.route("/", methods=["GET"])
def otp_request():
    return github_otp(flask.request)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)