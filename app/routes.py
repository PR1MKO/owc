from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_mail import Message
from . import mail

main = Blueprint("main", __name__)

@main.route("/")
def index():
    return render_template("index.html")

@main.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")

        if not name or not email or not message:
            flash("Please fill out all fields.", "danger")
            return redirect(url_for("main.contact"))

        msg = Message(
            subject=f"New Contact Form Submission from {name}",
            sender=email,
            recipients=["your@email.com"],  # TODO: update this
            body=message
        )
        mail.send(msg)
        flash("Message sent successfully!", "success")
        return redirect(url_for("main.contact"))

    return render_template("contact.html")
