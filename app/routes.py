import re
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_mail import Message
from . import mail, db
from .models import NewsletterSubscriber

main = Blueprint("main", __name__)

# Simple email regex for basic validation
EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")

@main.route("/")
def index():
    return render_template("index.html")

@main.route('/privacy')
def privacy():
    return render_template('privacy.html')

@main.route('/test')
def test():
    return "✅ Test route OK"

@main.route('/contact', methods=['GET', 'POST'])
def contact():
    form = {"name": "", "email": "", "message": ""}
    
    if request.method == 'POST':
        form["name"] = request.form.get('name', '').strip()
        form["email"] = request.form.get('email', '').strip()
        form["message"] = request.form.get('message', '').strip()
        accept_policy = request.form.get("accept_policy")
        wants_newsletter = request.form.get("newsletter") == "on"
        name = form["name"]
        email = form["email"]

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
            
        if not accept_policy:
            errors.append("You must accept the Privacy Policy.")

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template('contact.html', form=form)
            
        email_body = (
            f"Name: {form['name']}\n"
            f"Email: {form['email']}\n"
            f"Message:\n{form['message']}"
        )

        if wants_newsletter:
            email_body += "\n\n<strong>New newsletter subscriber</strong>"
            subscriber = NewsletterSubscriber(name=name, email=email)
            db.session.add(subscriber)
            db.session.commit()

        msg = Message(
            subject=f"Online Wine Club Contact – {form['name']}",
            recipients=[current_app.config["CONTACT_RECIPIENT"]],
            body=email_body,
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
            
        referrer = request.referrer
        if referrer and referrer != request.url:
            return redirect(url_for('main.redirect_with_delay', target=referrer))
        else:
            return redirect(url_for('main.redirect_with_delay', target=url_for('main.index')))

    return render_template('contact.html', form=form)


@main.route("/redirect")
def redirect_with_delay():
    target = request.args.get("target", url_for("main.index"))
    return render_template("redirect.html", target=target)