from flask_login import UserMixin
from apps import db, login_manager
from datetime import datetime
from flask import session
from sqlalchemy.orm import backref
from apps.utils.util import hash_pass


class Users(db.Model, UserMixin):

    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True)
    password = db.Column(db.String(64))
    name = db.Column(db.String(64))
    type = db.Column(db.String(64))

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]

            if property == 'password':
                value = hash_pass(value)  # we need bytes here (not plain str)

            setattr(self, property, value)

    def __repr__(self):
        return str(self.id)

class Members(db.Model, UserMixin):

    __tablename__ = 'members'

    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.String(64))
    firstname = db.Column(db.String(64))
    lastname = db.Column(db.String(64))
    dob = db.Column(db.String(64))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(64))
    status = db.Column(db.String(64))
    guardian_firstname = db.Column(db.String(64))
    guardian_relation = db.Column(db.String(64))
    phoneno = db.Column(db.Integer)
    email = db.Column(db.String(64))
    address_line1 = db.Column(db.String(64))
    address_line2 = db.Column(db.String(64))
    state = db.Column(db.String(64))
    pincode = db.Column(db.Integer)

    pf_no = db.Column(db.Integer)
    id_proof_name = db.Column(db.String(64))
    id_proof_no = db.Column(db.Integer)
    address_proof_name = db.Column(db.String(64))
    address_proof_no = db.Column(db.Integer)
    sign_proof_name = db.Column(db.String(64))
    pan_no = db.Column(db.Integer)
    image1 = db.Column(db.String(64))
    image2 = db.Column(db.String(64))

    bankname = db.Column(db.String(64))
    branchName = db.Column(db.String(64))
    accountno = db.Column(db.Integer)
    category = db.Column(db.String(64))
    ifsc_code = db.Column(db.String(64))
    micr_code = db.Column(db.String(64))

    nomi_name = db.Column(db.String(64))
    nomi_dob = db.Column(db.String(64))
    nomi_age = db.Column(db.Integer)
    nomi_relation = db.Column(db.String(64))
    nomi_per_share = db.Column(db.Integer)

    Thrift_FundBalance = db.Column(db.Integer)
    ShareBalance = db.Column(db.Float)
    LoanAmount = db.Column(db.Float)
    LoanEMIAmount = db.Column(db.Float)
    Active = db.Column(db.Integer)
    MemberDate = db.Column(db.String(64))
    ApprovedStatus = db.Column(db.String(64))


class ThriftFunds(db.Model, UserMixin):

    __tablename__ = 'thrift_funds'

    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'))
    
    Thrift_Credit_Amount = db.Column(db.Integer)
    Thrift_Credit_Mobile = db.Column(db.Integer)
    Thrift_Credit_PayMethod = db.Column(db.String(64))  
    Thrift_Credit_TransactionID = db.Column(db.String(64)) 

    Thrift_Debit_Amount = db.Column(db.Integer)
    Thrift_Debit_Transfer = db.Column(db.String(64))
    Thrift_Debit_PayMethod = db.Column(db.String(64))  
    Thrift_Debit_ChequeNo = db.Column(db.String(64))  
    Thrift_Debit_TransactionID = db.Column(db.String(64))  
    ThriftCreateDate = db.Column(db.String(64)) 
    ThriftBalance = db.Column(db.Integer)
    ApprovedStatus = db.Column(db.String(64))
     

class Shares(db.Model, UserMixin):

    __tablename__ = 'shares'

    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'))

    ShareOfficeName = db.Column(db.String(64))
    ShareCreateDate = db.Column(db.String(64))
    ShareDateofJoinig = db.Column(db.String(64))
    ShareDateofAllotment = db.Column(db.String(64))
    ShareDateofRetirement = db.Column(db.String(64))
    ShareTotalAmount = db.Column(db.Integer)  

    CreditShareAmount = db.Column(db.Integer) 

    DebitShareAmount =  db.Column(db.Integer) 
    DebitSharePayMethod  = db.Column(db.String(64)) 
    DebitShareChequeNo  = db.Column(db.String(64)) 
    DebitShareTransactionID  = db.Column(db.String(64)) 
    ApprovedStatus = db.Column(db.String(64))
    


class Loan(db.Model, UserMixin):

    __tablename__ = 'loan'

    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'))
    LoanCode = db.Column(db.String(64))
    LoanOfficeName = db.Column(db.String(64))
    LoanDate = db.Column(db.String(64))
    LoanFormNo = db.Column(db.String(64))
    LoanType = db.Column(db.String(64)) 
    LoanAmount = db.Column(db.String(64)) 
    LoanTenure = db.Column(db.String(64)) 
    LoanEMIAmount = db.Column(db.String(64)) 

    EmployeeName = db.Column(db.String(64))
    EmployeeCode = db.Column(db.String(64))
    EmployeePhoneNo = db.Column(db.String(64))
    MemberName = db.Column(db.String(64))
    MemberCode = db.Column(db.String(64))
    MemberPhoneNo = db.Column(db.String(64))
    ApprovedStatus = db.Column(db.String(64))

class LoanDebitTransactions(db.Model, UserMixin):

    __tablename__ = 'loan_transactions'

    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'))
    Amount = db.Column(db.String(64))
    PaymentMode = db.Column(db.String(64))
    TransactionID = db.Column(db.String(64))
    TransactionDate = db.Column(db.String(64))
    Interest = db.Column(db.String(64))


class GlobalValues(db.Model,UserMixin) :
    __tablename__ = 'global_values'
    id = db.Column(db.Integer, primary_key=True)
    tenure = db.Column(db.Integer)
    limit = db.Column(db.Integer)
    processingFee = db.Column(db.Integer)
    PerShareAmount = db.Column(db.Integer)
    rateofInterest = db.Column(db.Integer)
    variable = db.Column(db.Float)


@login_manager.user_loader
def user_loader(id):
    return Users.query.filter_by(id=id).first()


# @login_manager.request_loader
# def request_loader(request):
#     username = request.form.get('username')
#     user = Users.query.filter_by(username=username).first()
#     return user if user else None
