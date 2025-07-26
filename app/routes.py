import re
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_mail import Message
from . import mail

main = Blueprint("main", __name__)

# Simple email regex for basic validation
EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")

@main.route("/")
def index():
    return render_template("index.html")

@main.route('/contact', methods=['GET', 'POST'])
def contact():
    form = {"name": "", "email": "", "message": ""}
    
    if request.method == 'POST':
        form["name"] = request.form.get('name', '').strip()
        form["email"] = request.form.get('email', '').strip()
        form["message"] = request.form.get('message', '').strip()

        errors = []
        if not form["name"] or not form["email"] or not form["message"]:
            if not form["name"]:
                errors.append('Name is required.')
            if not form["email"]:
                errors.append('Email is required.')
            if not form["message"]:
                errors.append('Message is required.')

        if form["email"] and not EMAIL_REGEX.match(form["email"]):
            errors.append('Please enter a valid email address.')

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template('contact.html', form=form)

        msg = Message(
            subject=f"Online Wine Club Contact – {form['name']}",
            recipients=['istvankiss1979@gmail.com'],
            body=(
                f"Name: {form['name']}\n"
                f"Email: {form['email']}\n"
                f"Message:\n{form['message']}"
            ),
        )

        if EMAIL_REGEX.match(form["email"]):
            msg.reply_to = form["email"]

        try:
            current_app.logger.debug("Sending contact email: %s", msg.body)
            mail.send(msg)
            flash('Your message has been sent. Thank you!', 'success')
        except Exception:
            current_app.logger.exception('Failed to send contact email')
            flash('Sorry, there was a problem sending your message.', 'danger')
            
        return redirect(url_for('main.contact'))

    return render_template('contact.html', form=form)
