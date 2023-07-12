from flask import render_template, redirect, request, url_for, session
from flask_login import current_user, login_user, logout_user
from flask_mail import Message
import random
from apps.utils.models import Users, Members, ThriftFunds, Shares,Loan, LoanDebitTransactions, GlobalValues



from apps import db, login_manager, mail
from apps.authentication import blueprint
from apps.utils.forms import (
    LoginForm, 
)
from apps.utils.models import (
    Users,
)
from apps.utils.util import hash_pass, verify_pass


@blueprint.route('/')
def route_default():
    # Redirect the user to the login page when they visit the root URL
    return redirect(url_for('authentication_blueprint.login'))

@blueprint.route('/index')
# @login_required
def index():
    members = Members.query.all()
    thriftFunds = ThriftFunds.query.all()
    loans = Loan.query.all()
    shares = Shares.query.all()

    loanBalance = 0
    thriftBalance = 0
    shareBalance = 0
    activeMembers = 0
    inactiveMembers = 0

    for member in members :
            loanBalance += member.LoanAmount
            thriftBalance += member.Thrift_FundBalance
            shareBalance += member.ShareBalance
            if member.Active == 1 :
                activeMembers+=1
            else :
                inactiveMembers+=1
    user = session['user']
    session['usercode'] = 0
    
    if user == "Admin":
        session['usercode'] = 1
    return render_template('home/index.html',loanBalance= loanBalance,thriftBalance=thriftBalance,shareBalance=shareBalance,activeMembers=activeMembers,inactiveMembers=inactiveMembers)


# Login & Registration
@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm(request.form)
    if request.method == 'POST':
        # read form data
        # session['username'] = request.form['username']
        print("here")
        email = request.form['email']
        password = request.form['password']

        # Locate user
        user = Users.query.filter_by(email=email).first()

        # Check the password
        if user and (password == user.password):
            login_user(user)
            print(user.type , "this is in login function")
            session['user'] = user.type
            session['username'] = user.name
            return redirect(url_for('authentication_blueprint.route_default'))

        # Something (user or pass) is not ok
        return render_template('accounts/login.html',
                               msg='Wrong user or password',
                               form=login_form)

    # If the user is already authenticated, redirect them to the author page
    if current_user.is_authenticated:
        return redirect(url_for('authentication_blueprint.index'))
    # Otherwise, render the login template
    return render_template('accounts/login.html', form=login_form)


@blueprint.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    form = CreateAccountForm(request.form)
    if request.method == 'POST':
        if 'email' in request.form:
            email = request.form['email']
            user = Users.query.filter_by(email=email).first()
            if not user:
                # Email does not exist
                return render_template('accounts/forgot-password.html',
                                       msg='Email does not exist',
                                       form=form, flag=1)
            # code to send email
            otp = ""
            for i in range(4):  
                otp += str(random.randint(1, 9))
            user.otp = otp

            msg = Message('Twilio SendGrid Test Email', recipients=[email])
            msg.body = otp
            mail.send(msg)

            db.session.commit()
            session['email'] = request.form['email']
            return render_template('accounts/forgot-password.html',
                                   msg='Enter OTP sent on email',
                                   form=form, flag=2)
        elif 'otp' in request.form:
            otp = request.form['otp']
            email = session['email']
            user = Users.query.filter_by(email=email).first()

            if otp == user.otp:
                return render_template('accounts/forgot-password.html',
                                       msg='Enter New Password',
                                       form=form, flag=3)
            return render_template('accounts/forgot-password.html',
                                   msg='Wrong OTP',
                                   form=form, flag=2)
        elif 'password' in request.form:
            password = request.form['password']
            email = session['email']
            user = Users.query.filter_by(email=email).first()

            user.password = hash_pass(password)
            db.session.commit()

            return redirect(url_for('authentication_blueprint.login'))
    return render_template('accounts/forgot-password.html',
                           msg='Enter your Email',
                           form=form, flag=1)


@blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('authentication_blueprint.login'))

@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('home/page-403.html'), 403


@blueprint.errorhandler(403)
def access_forbidden(error):
    return render_template('home/page-403.html'), 403


@blueprint.errorhandler(404)
def not_found_error(error):
    return render_template('home/page-404.html'), 404


@blueprint.errorhandler(500)
def internal_error(error):
    return render_template('home/page-500.html'), 500
