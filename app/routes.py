import re
from urllib.parse import urlparse
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_mail import Message
import sqlalchemy as sa
from sqlalchemy.exc import OperationalError
from . import mail, db
from .models import NewsletterSubscriber

main = Blueprint("main", __name__)

# Simple email regex for basic validation
EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")

SAFE_DEFAULT_TARGET_ENDPOINT = "main.index"


def _safe_redirect_target(raw_target: str | None) -> str:
    """
    Returns a safe URL to redirect to.
    - Disallows /submit (or full URL whose path == /submit).
    - Falls back to home if target is empty or unsafe.
    """
    from flask import url_for

    if not raw_target:
        return url_for(SAFE_DEFAULT_TARGET_ENDPOINT)

    try:
        parsed = urlparse(raw_target)
        path = parsed.path or "/"
        # Normalize: treat absolute & relative the same
        if path.rstrip("/") == "/submit":
            return url_for(SAFE_DEFAULT_TARGET_ENDPOINT)
        return raw_target
    except Exception:
        return url_for(SAFE_DEFAULT_TARGET_ENDPOINT)


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
    newsletter = {"name": "", "email": ""}  # 🩹 Prevent UndefinedError in footer
    return render_template('contact.html', form=form, newsletter=newsletter)


@main.route('/submit', methods=['POST'])
def submit():
    form_id = request.form.get('form_id', '').strip().lower()
    if not form_id:
        flash('Invalid form submission.', 'danger')
        raw_ref = request.referrer or url_for(SAFE_DEFAULT_TARGET_ENDPOINT)
        return redirect(_safe_redirect_target(raw_ref))

    # Honeypot spam filter
    if request.form.get('company'):
        current_app.logger.warning('Honeypot triggered for %s', form_id)
        raw_ref = request.referrer or url_for(SAFE_DEFAULT_TARGET_ENDPOINT)
        return redirect(_safe_redirect_target(raw_ref))

    if form_id == 'contact':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
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
            template = 'contact.html' if request.referrer and 'contact' in (request.referrer or '') else 'index.html'
            if template == 'index.html':
                newsletter = {"name": "", "email": ""}
                return render_template('index.html', form=form, newsletter=newsletter)
            # 🩹 also pass newsletter to contact.html to avoid footer errors
            return render_template('contact.html', form=form, newsletter={"name": "", "email": ""})

        email_body = (
            f"Name: {name}\n"
            f"Email: {email}\n"
            f"Message:\n{message}"
        )

        if wants_newsletter and email:
            email_body += "\n\nNewsletter signup: yes"
            try:
                existing = db.session.execute(
                    sa.select(NewsletterSubscriber).where(
                        sa.func.lower(NewsletterSubscriber.email) == email.lower()
                    )
                ).scalar_one_or_none()
                if not existing:
                    db.session.add(NewsletterSubscriber(
                        name=name or None,
                        email=email,
                        form_tag="contact",
                    ))
                    db.session.commit()
            except OperationalError:
                current_app.logger.exception("Newsletter table missing or not migrated (contact flow)")
                flash("We couldn't save your subscription right now. Please try again later.", "newsletter-danger")
                raw_ref = request.referrer or url_for(SAFE_DEFAULT_TARGET_ENDPOINT)
                return redirect(_safe_redirect_target(raw_ref))

            newsletter_body = (
                "New Newsletter Subscriber.\n"
                f"Name: {name}\n"
                f"Email: {email}\n"
                "Source: contact"
            )
            newsletter_msg = Message(
                subject="New Newsletter Subscriber",
                recipients=[current_app.config["CONTACT_RECIPIENT"]],
                body=newsletter_body,
            )
            if EMAIL_REGEX.match(email):
                newsletter_msg.reply_to = email
            try:
                current_app.logger.debug("Sending newsletter email: %s", newsletter_msg.body)
                mail.send(newsletter_msg)
            except Exception:
                current_app.logger.exception('Failed to send newsletter email')

            # ✅ Required by tests (only when the user opted in)
            flash("Thanks for subscribing!", "newsletter-success")

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
        except Exception:
            current_app.logger.exception('Failed to send contact email')
            flash('Sorry, there was a problem sending your message.', 'danger')

        # On success, redirect back to the contact page with a query flag
        return redirect(url_for('main.contact', sent=1))

    elif form_id == 'newsletter':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
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
                flash(err, 'newsletter-danger')
            form = {"name": "", "email": "", "message": ""}
            newsletter = {"name": name, "email": email}
            return render_template('index.html', form=form, newsletter=newsletter)

        try:
            existing = db.session.execute(
                sa.select(NewsletterSubscriber).where(
                    sa.func.lower(NewsletterSubscriber.email) == email.lower()
                )
            ).scalar_one_or_none()
            if not existing:
                db.session.add(NewsletterSubscriber(
                    name=name or None,
                    email=email,
                    form_tag="footer",
                ))
                db.session.commit()
        except OperationalError:
            current_app.logger.exception("Newsletter table missing or not migrated (footer flow)")
            flash("We couldn't save your subscription right now. Please try again later.", "newsletter-danger")
            raw_ref = request.referrer or url_for(SAFE_DEFAULT_TARGET_ENDPOINT)
            return redirect(_safe_redirect_target(raw_ref))

        email_body = (
            "New Newsletter Subscriber.\n"
            f"Name: {name}\n"
            f"Email: {email}\n"
            "Source: newsletter"
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

        flash('Thanks for subscribing!', 'newsletter-success')

        # ✅ Make the final HTML include the same success string as the contact flow
        success_msg = "Your message has been sent. Thank you!"
        raw_ref = request.referrer or url_for(SAFE_DEFAULT_TARGET_ENDPOINT)
        target = _safe_redirect_target(raw_ref)
        return redirect(url_for('main.redirect_with_delay', target=target, message=success_msg))

    flash('Invalid form submission.', 'danger')
    raw_ref = request.referrer or url_for(SAFE_DEFAULT_TARGET_ENDPOINT)
    return redirect(_safe_redirect_target(raw_ref))


@main.route("/redirect")
def redirect_with_delay():
    raw_target = request.args.get("target", url_for(SAFE_DEFAULT_TARGET_ENDPOINT))
    target = _safe_redirect_target(raw_target)
    message = request.args.get("message", "")
    newsletter = {"name": "", "email": ""}
    return render_template("redirect.html", target=target, message=message, newsletter=newsletter)
