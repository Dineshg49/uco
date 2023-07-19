from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, FileField, TelField, DateField, TextAreaField, IntegerField, SelectMultipleField, validators, BooleanField, FloatField
from wtforms.validators import Email, DataRequired, Length, NumberRange
from wtforms import widgets
from datetime import datetime

class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget()
    option_widget = widgets.CheckboxInput()

class LoginForm(FlaskForm):
    email = StringField('Email',
                         id='email_login',
                         validators=[DataRequired()])
    password = PasswordField('Password',
                             id='pwd_login',
                             validators=[DataRequired()])

class PersonalInfo(FlaskForm):
    firstname = StringField('Firstname',
                         id='firstname_create', validators=[DataRequired()]
                         )
    lastname = StringField('lastname',
                         id='lastname_create', validators=[DataRequired()]
                         )
    dob = DateField('Dob',id='dob_create',format='%d-%m-%Y',validators=[DataRequired()])
    dob2 = StringField('DOB',id='dob')

    age = IntegerField('age', id='age_create',validators=[DataRequired(), NumberRange(min=18)])

    form_no = IntegerField('form_no', id='form_no_create')

    gender = SelectField('gender', choices = ['Male', 'Female', 'Transgender'], validators=[DataRequired()])

    status = SelectField('status', choices = ['Married', 'Unmarried'])

    guardian_firstname = StringField('guardian_firstname',
                         id='guardian_firstname_create', validators=[DataRequired()])
    guardian_relation = SelectField('guardian_relation', choices = ['Father', 'Mother', 'Spouse'], validators=[DataRequired()])

    phoneno = IntegerField('phoneno', id='phone_create', validators=[DataRequired(),NumberRange(min=1000000000,max=9999999999)])

    email = StringField('Email',
                         id='email_login', validators=[DataRequired(), Email()])
    
    address_line1 = StringField('AddressLine1', id='AddressLine1', validators=[DataRequired()])
    address_line2 = StringField('AddressLine2', id='AddressLine2', validators=[DataRequired()])

    state = SelectField('states', choices = ['Andhra Pradesh','Arunachal Pradesh','Assam',
    'Bihar','Chhattisgarh','Goa','Gujarat','Haryana','Himachal Pradesh','Jammu and Kashmir','Jharkhand',
    'Karnataka','Kerala','Madhya Pradesh','Maharashtra','Manipur','Meghalaya','Mizoram','Nagaland','Odisha',
    'Punjab','Rajasthan','Sikkim','Tamil Nadu','Telangana','Tripura','Uttar Pradesh',
    'Uttarakhand','West Bengal','Andaman and Nicobar','Chandigarh','Dadra and Nagar Haveli',
    'Daman and Diu','Lakshadweep','Delhi','Puducherry'], validators=[DataRequired()])

    pincode = IntegerField('pincode', id='pincode_create', validators=[DataRequired()])

    profile_image= FileField('profile', validators=[DataRequired()])

    sign_image= FileField('sign', validators=[DataRequired()])


class KYCForm(FlaskForm):
    pf_no = IntegerField('pf_no', id='pf_no_create',  validators=[DataRequired()])

    gender = SelectField('gender', choices = ['Male', 'Female', 'Transgender'],  validators=[DataRequired()])

    id_proof_name  = SelectField('id_proof_name', choices = ['Aadhar Card', 'Driving Licence', 'Electricity Bill', 'Passport', 'Pan Card', 'Voter ID Card'],  validators=[DataRequired()])

    id_proof_no = IntegerField('id_proof_no', id='id_proof_no_create',  validators=[DataRequired()])

    address_proof_name  = SelectField('address_proof_name', choices = ['Aadhar Card', 'Driving Licence', 'Electricity Bill', 'Passport', 'Pan Card'],  validators=[DataRequired()])

    address_proof_no = IntegerField('address_proof_no', id='address_proof_no_create',  validators=[DataRequired()])

    sign_proof_name  = SelectField('sign_proof_name', choices = ['Passport', 'Pan Card'],  validators=[DataRequired()])

    pan_no = StringField('pan_no', id='pan_no_create',  validators=[DataRequired()])

    image1= FileField('image1')

    image2= FileField('image2')



class MemberBankingForm(FlaskForm):
    bankname = SelectField('bank_name', choices = ['Axis Bank', 'Bank Of Baroda', 'Bank Of India', 'Canara Bank', 'Central Bank Of India', 'HDFC' 
    , 'Kotak Mahindra Bank' ,'Punjab National Bank','State Bank Of India','Union Bank Of India'],  validators=[DataRequired()])


    branchName = StringField('branchname',
                      id='branchname_create',  validators=[DataRequired()])
    
    accountno = IntegerField('accountno', id='accountno_create',  validators=[DataRequired()])

    category = SelectField('category', choices = ['Current Account', 'Saving Account', 'Salary Account'],  validators=[DataRequired()])

    ifsc_code = StringField('ifsc_code',
                      id='ifsc_code_create',  validators=[DataRequired()])
    
    micr_code = StringField('micr_code',
                      id='micr_code_create',  validators=[DataRequired()])


class NomineeForm(FlaskForm): 
    nomi_name = StringField('nomi_name',
                      id='nomi_name_create',  validators=[DataRequired()])
    
    nomi_dob = DateField('Dob',id='dob_create',format='%d-%m-%Y',  validators=[DataRequired()])
    nomi_dob2 = StringField('DOB',id='dob2',  validators=[DataRequired()])

    nomi_age = IntegerField('age', id='age_create',  validators=[DataRequired()])

    nomi_relation = SelectField('relation', choices = ['Father', 'Mother', 'Spouse'],  validators=[DataRequired()])

    nomi_per_share = IntegerField('per_share', id='per_share_create',  validators=[DataRequired()])

class ThriftFund(FlaskForm):

    DateofJoinig = DateField('DateofJoining',id='LastRecDate_create',format='%d-%m-%Y')


class ThriftFund1(FlaskForm):

    total_amount2 = IntegerField('amount', id='amount',  validators=[DataRequired()])

    payment_method = SelectField('payment_method', choices = ['Cheque', 'Cash', 'Net Banking'],  validators=[DataRequired()])

    transcation_id = IntegerField('transcation_id', id='transcation_id_create',  validators=[DataRequired()])

    total_amount = IntegerField('total_amount', id='total_amount_create',  validators=[DataRequired()])

    phoneno = IntegerField('phoneno', id='phone_create',  validators=[DataRequired()])

class ThriftFund2(FlaskForm):

    Date = DateField('Date',id='Date_create',format='%d-%m-%Y',  validators=[DataRequired()])

    Installment = DateField('Installment',id='Installment_create',format='%d-%m-%Y',  validators=[DataRequired()])

    payment_method = SelectField('payment_method', choices = ['Cheque', 'Cash', 'Net Banking'],  validators=[DataRequired()])

    transcation_id = IntegerField('transcation_id', id='transcation_id_create',  validators=[DataRequired()])

class ThriftFund3(FlaskForm):

    total_amount = IntegerField('amount', id='amount', validators=[DataRequired()])

    amount = IntegerField('amount', id='amount', validators=[DataRequired()])

    transfer = SelectField('transfer', choices = ['Loan A/C', 'Bank A/C'], validators=[DataRequired()])

    mode_of_transaction = SelectField('mode_of_transaction', choices = ['Cheque', 'Cash', 'Net Banking'], validators=[DataRequired()])

    cheque_number = IntegerField('cheque_number', id='cheque_number')

    transcation_id2 = IntegerField('transcation_id', id='transcation_id_create', validators=[DataRequired()])


class Search(FlaskForm):
    text = StringField('text', validators=[DataRequired()])


class ShareForm(FlaskForm):

    prevShareBalance = IntegerField('prevShareBalace', id='prevShareBalace_create')
    prevShareAmount = IntegerField('prevShareAmount', id='prevShareAmount_create')
    Office_Name = SelectField('Office_Name', choices = ['Head-Office-01', 'Head-Office-02'],  validators=[DataRequired()])
    DateofJoin = DateField('Date',format='%d-%m-%Y')
    DateofAllotment = DateField('Date',format='%d-%m-%Y')
    DateofRetirement = DateField('Date',format='%d-%m-%Y')
    perShareAmount = IntegerField('perShareamount', id='perShareamount_create')
    investAmount = IntegerField('investamount', id='investamount_create', validators=[DataRequired()])
    shareUnit = FloatField('shareUnit', id='shareUnit_create')
   
class ShareForm1(FlaskForm):

    prevShareBalance = IntegerField('prevShareBalace', id='prevShareBalace_create')
    prevShareAmount = IntegerField('prevShareAmount', id='prevShareAmount_create')
    perShareAmount = IntegerField('perShareamount', id='perShareamount_create')
    investAmount2 = IntegerField('investamount', id='investamount_create',  validators=[DataRequired()])
    shareUnit = FloatField('shareUnit', id='shareUnit_create')

class ShareForm2(FlaskForm):

    prevShareBalance = IntegerField('prevShareBalace', id='prevShareBalace_create')
    prevShareAmount = IntegerField('prevShareAmount', id='prevShareAmount_create')
    amount = IntegerField('amount', id='amount_create',  validators=[DataRequired()])
    remainingBalance = IntegerField('remainingBalance', id='remainingBalance_create')
    remainginShareAmount = IntegerField('remainginShareAmount', id='remainginShareAmount_create')
    mode_of_transaction = SelectField('mode_of_transaction', choices = ['Cheque', 'Cash', 'Net Banking'],  validators=[DataRequired()])
    cheque_number = IntegerField('cheque_number', id='cheque_number')
    transcation_id2 = IntegerField('transcation_id', id='transcation_id_create',  validators=[DataRequired()])



class LoanForm(FlaskForm):

    LoanCode = IntegerField('Code')
    Office_Name = SelectField('Office_Name', choices = ['Head-Office-1', 'Head-Office-2'],  validators=[DataRequired()])
    LoanDate = DateField('LoanDate',format='%d-%m-%Y', default=datetime.now())
    Loan_Type = SelectField('Loan_Type', choices = ['Housing', 'Construction'],  validators=[DataRequired()])
    LoanAmount = IntegerField('totalLoanAmount',  validators=[DataRequired()])
    Tenure = IntegerField('totalTenure')
    EMIAmount = IntegerField('totalEMIAmount')
    ProcessingFees = IntegerField('totalProcessingFees')


class LoanForm1(FlaskForm):
    EmployeeName = StringField('EmployeeName', validators=[DataRequired()])
    EmployeeCode = StringField('EmployeeCode', validators=[DataRequired()])
    EmployeePhoneNo = StringField('EmployeePhoneNo', validators=[DataRequired()])
    MemberName = StringField('MemberName', validators=[DataRequired()])
    MemberCode = StringField('MemberCode', validators=[DataRequired()])
    MemberPhoneNo = StringField('MemberPhoneNo', validators=[DataRequired()])
   

class LoanForm2(FlaskForm):

    EMIAmount2 = IntegerField('totalEMIAmount')
    Payment_Mode = SelectField('Payment_Mode', choices = ['Amount given by Member', 'Amount given from thrift A/C','Amount given from Share A/C'],  validators=[DataRequired()])
    Amount2 = IntegerField('Amount',  validators=[DataRequired()])
    TransactionID = StringField('TransactionID',  validators=[DataRequired()])


class LoanForm3(FlaskForm):

    Principle = IntegerField('Principle')
    EMI_Amount = IntegerField('EMI_Amount')
    No_of_EMI = IntegerField('No_of_EMI')
    Amount_Paid = IntegerField('Amount_Paid')
    Payment_Mode2 = SelectField('Payment_Mode', choices = ['Amount given by Member', 'Amount given from thrift A/C','Amount given from Share A/C'],  validators=[DataRequired()])
    Amount3 = IntegerField('Amount')
    TransactionID2 = StringField('TransactionID',  validators=[DataRequired()])


class ReportForm(FlaskForm):

    MemberCode = IntegerField('MemberCode')
    FromDate = DateField('fromDate',id='fromDate_create',format='%d-%m-%Y',)
    ToDate = DateField('ToDate',id='ToDate_create',format='%d-%m-%Y',)
    FinancialYear = SelectField('FinancialYear', choices = ['2023-24','2022-23', '2021-22','2020-21'])

    




    

    