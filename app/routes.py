import re
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_mail import Message
from . import mail, db
from .models import NewsletterSubscriber

main = Blueprint("main", __name__)

# Simple email regex for basic validation
EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")

@main.route('/', methods=['GET'])
@main.route('/index', methods=['GET'])
def index():
    form = {"name": "", "email": "", "message": ""}
    newsletter = {"name": "", "email": ""}
    return render_template('index.html', form=form, newsletter=newsletter)

@main.route('/privacy')
def privacy():
    return render_template('privacy.html')

@main.route('/test')
def test():
    return "✅ Test route OK"

@main.route('/contact', methods=['GET'])
def contact():
    form = {"name": "", "email": "", "message": ""}
    return render_template('contact.html', form=form)

@main.route('/submit', methods=['POST'])
def submit():
    form_id = request.form.get('form_id', '').strip().lower()
    if not form_id:
        flash('Invalid form submission.', 'danger')
        return redirect(request.referrer or url_for('main.index'))

    # Honeypot spam filter
    if request.form.get('company'):
        current_app.logger.warning('Honeypot triggered for %s', form_id)
        return redirect(request.referrer or url_for('main.index'))

    if form_id == 'contact':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        message = request.form.get('message', '').strip()
        accept_policy = request.form.get('accept_policy')
        wants_newsletter = request.form.get('newsletter') == 'on'

        errors = []
        if not name:
            errors.append('Name is required.')
        if not email:
            errors.append('Email is required.')
        if not message:
            errors.append('Message is required.')
        if email and not EMAIL_REGEX.match(email):
            errors.append('Please enter a valid email address.')
        if not accept_policy:
            errors.append('You must accept the Privacy Policy.')

        if errors:
            for err in errors:
                flash(err, 'danger')
            form = {"name": name, "email": email, "message": message}
            template = 'contact.html' if request.referrer and 'contact' in request.referrer else 'index.html'
            if template == 'index.html':
                newsletter = {"name": "", "email": ""}
                return render_template('index.html', form=form, newsletter=newsletter)
            return render_template('contact.html', form=form)

        email_body = (
            f"Name: {name}\n"
            f"Email: {email}\n"
            f"Message:\n{message}"
        )

        if wants_newsletter:
            email_body += "\n\n<strong>New newsletter subscriber</strong>"
            subscriber = NewsletterSubscriber(name=name, email=email)
            db.session.add(subscriber)
            db.session.commit()
            
        email_body += f"\n\nForm source: {form_id}"

        msg = Message(
            subject=f"Online Wine Club Contact – {name}",
            recipients=[current_app.config["CONTACT_RECIPIENT"]],
            body=email_body,
        )

        if EMAIL_REGEX.match(email):
            msg.reply_to = email

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
        return redirect(url_for('main.redirect_with_delay', target=url_for('main.index')))

    elif form_id == 'newsletter':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        accept_policy = request.form.get('accept_policy')

        errors = []
        if not name:
            errors.append('Name is required.')
        if not email:
            errors.append('Email is required.')
        if email and not EMAIL_REGEX.match(email):
            errors.append('Please enter a valid email address.')
            
        if not accept_policy:
            errors.append('You must accept the Privacy Policy.')

        if errors:
            for err in errors:
                flash(err, 'danger')
            form = {"name": "", "email": "", "message": ""}
            newsletter = {"name": name, "email": email}
            return render_template('index.html', form=form, newsletter=newsletter)

        try:
            subscriber = NewsletterSubscriber(name=name, email=email)
            db.session.add(subscriber)
            db.session.commit()
        except Exception:
            db.session.rollback()
            current_app.logger.exception('Failed to save newsletter subscriber')

        email_body = (
            "New Newsletter Subscriber.\n"
            f"Name: {name}\n"
            f"Email: {email}\n\n"
            f"Form source: {form_id}"
        )

        msg = Message(
            subject="New Newsletter Subscriber",
            recipients=[current_app.config["CONTACT_RECIPIENT"]],
            body=email_body,
        )

        if EMAIL_REGEX.match(email):
            msg.reply_to = email

        try:
            current_app.logger.debug("Sending newsletter email: %s", msg.body)
            mail.send(msg)
        except Exception:
            current_app.logger.exception('Failed to send newsletter email')

        flash('Your message has been sent. Thank you!', 'success')
        form = {"name": "", "email": "", "message": ""}
        newsletter = {"name": "", "email": ""}
        return render_template('index.html', form=form, newsletter=newsletter)

    flash('Invalid form submission.', 'danger')
    return redirect(request.referrer or url_for('main.index'))


@main.route("/redirect")
def redirect_with_delay():
    target = request.args.get("target", url_for("main.index"))
    return render_template("redirect.html", target=target)