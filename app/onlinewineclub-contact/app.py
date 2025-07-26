from flask import Flask, render_template, request, flash, redirect, url_for
from dotenv import load_dotenv
import os
import re
from flask_mail import Mail, Message

load_dotenv()
app = Flask(__name__)

# Flask-Mail config
app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER")
app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT", 587))
app.config["MAIL_USE_TLS"] = os.getenv("MAIL_USE_TLS", "true").lower() == "true"
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_DEFAULT_SENDER")

mail = Mail(app)
app.secret_key = os.getenv("SECRET_KEY", "devmode")

EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    form_data = {"name": "", "email": "", "message": ""}

    if request.method == "POST":
        form_data["name"] = request.form.get("name", "").strip()
        form_data["email"] = request.form.get("email", "").strip()
        form_data["message"] = request.form.get("message", "").strip()
        form_id = request.form.get("form_id", "Generic Form").strip().lower()

        # 🛡️ Honeypot spam check
        if request.form.get("company"):
            print("[SPAM BLOCKED] Honeypot field was filled.")
            flash("Spam detected. Submission blocked.", "error")
            return redirect(url_for("contact"))

        errors = []

        if not form_data["name"]:
            errors.append("Name is required.")
        if not form_data["email"]:
            errors.append("Email is required.")
        elif not EMAIL_REGEX.match(form_data["email"]):
            errors.append("Please enter a valid email address.")
        if not form_data["message"]:
            errors.append("Message is required.")

        if errors:
            for err in errors:
                flash(err, "error")
            return render_template("contact.html", form=form_data)

        # ✅ Send email with clean subject format
        msg = Message(
            subject=f"{form_id} – new message",
            recipients=[app.config["MAIL_USERNAME"]],
            body=f"""
Name: {form_data['name']}
Email: {form_data['email']}

Message:
{form_data['message']}
"""
        )
        try:
            mail.send(msg)
            flash("Thank you! Your message has been received.", "success")
        except Exception as e:
            print(f"[MAIL ERROR] {e}")
            flash("Sorry, there was a problem sending your message.", "error")

        return redirect(url_for("contact"))

    return render_template("contact.html", form=form_data)

if __name__ == "__main__":
    app.run()
