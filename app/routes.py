from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_mail import Message
from . import mail

main = Blueprint("main", __name__)

@main.route("/")
def index():
    return render_template("index.html")

@main.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        if not name or not email or not message:
            flash('Minden mezőt ki kell tölteni!', 'danger')
            return redirect(url_for('main.contact'))

        msg = Message(
            subject=f"Online Wine Club kapcsolatfelvétel – {name}",
            recipients=['your_email@gmail.com'],  # Replace with your own address
            body=f"Név: {name}\nEmail: {email}\nÜzenet:\n{message}",
            reply_to=email
        )
        mail.send(msg)
        flash('Üzenet elküldve, köszönjük!', 'success')
        return redirect(url_for('main.contact'))

    return render_template('contact.html', form={})
