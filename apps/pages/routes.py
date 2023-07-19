from flask import render_template, redirect, request, url_for, session
from flask import send_file
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter , landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.utils import ImageReader
from apps import db
from apps.authentication import blueprint
from apps.utils.forms import PersonalInfo,KYCForm,MemberBankingForm, NomineeForm,ThriftFund,ThriftFund1,ThriftFund2,ThriftFund3, Search, ShareForm,ShareForm1,LoanForm,LoanForm1,LoanForm2,LoanForm3, ShareForm2, ReportForm
from apps.utils.models import Users, Members, ThriftFunds, Shares,Loan, LoanDebitTransactions, GlobalValues
import random as r
import datetime  
from collections import Counter
from django.views.decorators.csrf import csrf_exempt
import pdfkit
from io import BytesIO
# import urllib
import urllib.request
from io import StringIO
import PIL.Image
import PyPDF2
from PyPDF2 import PdfWriter, PdfReader
import fitz
import io
from flask import make_response
from sqlalchemy import and_
import os, uuid
from apps.config import Config

# PerShareAmount = 10
# rateofInterest = 10.5





@csrf_exempt
@blueprint.route('/PI1', methods=['GET', 'POST'])
def pi1():
    personalInfo = PersonalInfo(request.form)
    if request.method == 'POST':
        file = request.files['profile_image']
        sign_file = request.files['sign_image']

        filename = str(uuid.uuid4())
        filename2 = str(uuid.uuid4())
        filename += '.jpg'
        filename2 += '.jpg'
        file.save(os.path.join(Config.UPLOAD_FOLDER, filename))
        sign_file.save(os.path.join(Config.UPLOAD_FOLDER, filename2))

        form_data = {
            'firstname': request.form['firstname'],
            'lastname': request.form['lastname'],
            'dob': request.form['dob'],
            'age': request.form['age'],
            'gender': request.form['gender'],
            'status': request.form['status'],
            'guardian_firstname': request.form['guardian_firstname'],
            'guardian_relation': request.form['guardian_relation'],
            'phoneno': request.form['phoneno'],
            'email': request.form['email'],
            'address_line1': request.form['address_line1'],
            'address_line2': request.form['address_line2'],
            'state': request.form['state'],
            'pincode': request.form['pincode'],
            'Thrift_FundBalance' : 0,
            'ShareBalance' : 0.0,
            'LoanAmount' : 0.0 , 
            'Active' : 1, 
            'MemberDate' : datetime.date.today(),
            'ApprovedStatus' : 'Pending',
            'image1' : filename,
            'image2' : filename2
            
        }
        session['email']  = form_data['email']

        currmember2 = Members.query.filter_by(email=session['email']).first()
        if currmember2:
            return render_template('pages/PI1.html', form=personalInfo)
        member = Members(**form_data)
        db.session.add(member)
        db.session.commit()
        currmember2 = Members.query.filter_by(email=session['email']).first()

        today = datetime.date.today()
        year = today.year
        month = today.month
        userid = str(year) + str(month).zfill(2) + str(currmember2.id).zfill(4)
        print(userid,"this is user id")
        currmember2.userid = userid
        db.session.commit()
        return render_template('pages/PI1.html', form=personalInfo, memberID=userid)

    return render_template('pages/PI1.html', form=personalInfo)



@blueprint.route('/Thrift_Fund_report_download' , methods=['GET', 'POST'])
def Thrift_Fund_report_download():
    reportform= ReportForm()
    if request.method == 'POST':

        financialYear = request.form['FinancialYear']
        # membercode = request.form['MemberCode']
        members = Members.query.all()

        year1 = int(financialYear[0:4])
        if request.form['FromDate'] : 
            fromDate = request.form['FromDate']
        else :
            fromDate = str(year1) + "-04-01"
        
        if request.form['ToDate'] : 
            toDate = request.form['ToDate']
        else :
            toDate = str(year1+1) + "-03-31"

        
        
        if request.form['MemberCode'] : 
            thriftFunds = ThriftFunds.query.filter(and_(ThriftFunds.ThriftCreateDate >= fromDate, ThriftFunds.ThriftCreateDate <= toDate , ThriftFunds.member_id == request.form['MemberCode'] ))
        else :  
            thriftFunds = ThriftFunds.query.filter(and_(ThriftFunds.ThriftCreateDate >= fromDate, ThriftFunds.ThriftCreateDate <= toDate))

        # Create a file-like buffer to receive PDF data.
        buffer = BytesIO()

        # Create the PDF object, using the buffer as its "file."
        p = canvas.Canvas(buffer, (1200,700))

        StartY = 500
        StartX = 50
        today = datetime.date.today()
        year = today.year
        month = today.month
        day = today.day
        datestring = str(day) + "/" +  str(month) + "/" +  str(year)

        # Add some custom text (you can customize this part as needed)
        p.drawString(StartX + 420, StartY + 90, datestring )

        activeMembers = Members.query.filter(and_(Members.MemberDate >= fromDate, Members.MemberDate <= toDate, Members.Active == 1 , Members.Thrift_FundBalance > 0 )).count()
        openingBalance = 0
        currentBalance = 0
        closedaccount = 0

        for member in members :
            currentBalance += member.Thrift_FundBalance
            thriftFund = ThriftFunds.query.filter(and_(ThriftFunds.ThriftCreateDate >= fromDate, ThriftFunds.ThriftCreateDate <= toDate , ThriftFunds.member_id == member.userid )).first()
            if thriftFund :
                openingBalance += thriftFund.ThriftBalance
                if thriftFund.ThriftBalance != 0 :
                    if member.Thrift_FundBalance == 0 :
                        closedaccount += 1



        # Add some custom text (you can customize this part as needed)
        p.drawString(StartX, StartY, "Financial Year : " + financialYear )
        p.drawString(StartX, StartY-20, "Total Number of Active Members : " + str(activeMembers))
        p.drawString(StartX, StartY-40, "Total Number of Member closed their A/C : " + str(closedaccount))
        p.drawString(StartX, StartY-60, "Opening thrift Balance : " + str(openingBalance))
        p.drawString(StartX, StartY-80, "Current Thrift Balance : " + str(currentBalance))

        data = [
            ["S.No.", "Member Code", "Member Name", "Date", "Credit", "Debit", "Balance", "Mode of Payment", "Bank A/C Number" , "Transaction #"],
        ]

        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ])

        table_data = [data[0]]

        for idx, thriftFund in enumerate(thriftFunds) :
            print(thriftFund.member_id, "here")
            member = Members.query.filter_by(userid=thriftFund.member_id).first()
            modeofpayment = ""
            transactionid = ""
            if thriftFund.Thrift_Credit_Amount : 
                modeofpayment = thriftFund.Thrift_Credit_PayMethod
                transactionid = thriftFund.Thrift_Credit_TransactionID
            else :
                modeofpayment = thriftFund.Thrift_Debit_PayMethod
                transactionid = thriftFund.Thrift_Debit_TransactionID
            row = [idx+1, member.userid, member.firstname + " " + member.lastname,thriftFund.ThriftCreateDate,thriftFund.Thrift_Credit_Amount,thriftFund.Thrift_Debit_Amount,thriftFund.ThriftBalance,modeofpayment,member.accountno,transactionid]
            table_data.append(row)

        # Other data can be added as necessary

        table = Table(table_data)
        table.setStyle(table_style)

        # Draw the table on the canvas
        table.wrapOn(p, StartX, StartY-270)
        table.drawOn(p, StartX-20, StartY-290)

        # Close the PDF object cleanly, and ensure we're at the beginning of the file.
        p.showPage()
        p.save()
        buffer.seek(0)

        pdf_path = 'Co-operative letter head.docx.pdf'



        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        can.drawString(10, 100, "Hello world")
        can.save()

        #move to the beginning of the StringIO buffer
        packet.seek(0)

        # create a new PDF with Reportlab
        new_pdf = PdfReader(buffer)
        # read your existing PDF
        existing_pdf = PdfReader(open(pdf_path, "rb"))
        output = PdfWriter()
        # add the "watermark" (which is the new pdf) on the existing page
        page = existing_pdf.pages[0]
        page.merge_page(new_pdf.pages[0])
        output.add_page(page)
        # finally, write "output" to a real file
        output_stream = open("destination.pdf", "wb")
        output.write(output_stream)
        output_stream.close()

        output_stream = open("destination.pdf", "rb")
        

        response = make_response(output_stream.read())
        response.headers['Content-Disposition'] = 'attachment; filename=destination.pdf'
        response.headers['Content-type'] = 'application/pdf'

    return response

@blueprint.route('/Loan_report_download' , methods=['GET', 'POST'])
def Loan_report_download():
    reportform= ReportForm()
    if request.method == 'POST':

        financialYear = request.form['FinancialYear']
        # membercode = request.form['MemberCode']
        members = Members.query.all()

        year1 = int(financialYear[0:4])
        if request.form['FromDate'] : 
            fromDate = request.form['FromDate']
        else :
            fromDate = str(year1) + "-04-01"
        
        if request.form['ToDate'] : 
            toDate = request.form['ToDate']
        else :
            toDate = str(year1+1) + "-03-31"

        
        
        if request.form['MemberCode'] : 
            loans = LoanDebitTransactions.query.filter(and_(LoanDebitTransactions.TransactionDate >= fromDate, LoanDebitTransactions.TransactionDate <= toDate , LoanDebitTransactions.member_id == request.form['MemberCode'] ))
        else :  
            loans = LoanDebitTransactions.query.filter(and_(LoanDebitTransactions.TransactionDate >= fromDate, LoanDebitTransactions.TransactionDate <= toDate))

        # Create a file-like buffer to receive PDF data.
        buffer = BytesIO()

        # Create the PDF object, using the buffer as its "file."
        p = canvas.Canvas(buffer, (1200,700))

        StartY = 500
        StartX = 50
        today = datetime.date.today()
        year = today.year
        month = today.month
        day = today.day
        datestring = str(day) + "/" +  str(month) + "/" +  str(year)

        # Add some custom text (you can customize this part as needed)
        p.drawString(StartX + 420, StartY + 90, datestring )

        activeMembers = Members.query.filter(and_(Members.MemberDate >= fromDate, Members.MemberDate <= toDate, Members.Active == 1 , Members.LoanAmount > 0 )).count()
        openingBalance = 0
        currentBalance = 0
        closedaccount = 0

        for member in members :
            currentBalance += member.LoanAmount
            loan = LoanDebitTransactions.query.filter(and_(LoanDebitTransactions.TransactionDate >= fromDate, LoanDebitTransactions.TransactionDate <= toDate , LoanDebitTransactions.member_id == member.userid )).first()
            if loan :
                openingBalance += int(loan.Amount)
                if int(loan.Amount) != 0 :
                    if member.LoanAmount == 0 :
                        closedaccount += 1



        # Add some custom text (you can customize this part as needed)
        p.drawString(StartX, StartY, "Financial Year : " + financialYear )
        p.drawString(StartX, StartY-20, "Total Number of Active Members : " + str(activeMembers))
        p.drawString(StartX, StartY-40, "Total Number of Member closed their A/C : " + str(closedaccount))
        p.drawString(StartX, StartY-60, "Opening Loan Balance : " + str(openingBalance))
        p.drawString(StartX, StartY-80, "Current Loan Balance : " + str(currentBalance))

        data = [
            ["S.No.", "Member Code", "Member Name", "EMI Date", "EMI Amount", "Mode of Payment", "Bank A/C Number" , "Transaction #"],
        ]

        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ])

        table_data = [data[0]]

        for idx, loan in enumerate(loans) :
            member = Members.query.filter_by(userid=loan.member_id).first()
            # modeofpayment = ""
            # transactionid = ""
            # if thriftFund.Thrift_Credit_Amount : 
            #     modeofpayment = thriftFund.Thrift_Credit_PayMethod
            #     transactionid = thriftFund.Thrift_Credit_TransactionID
            # else :
            #     modeofpayment = thriftFund.Thrift_Debit_PayMethod
            #     transactionid = thriftFund.Thrift_Debit_TransactionID
            row = [idx+1, member.userid, member.firstname + " " + member.lastname,loan.TransactionDate, loan.Amount,loan.PaymentMode,member.accountno,loan.TransactionID]
            table_data.append(row)

        # Other data can be added as necessary

        table = Table(table_data)
        table.setStyle(table_style)

        # Draw the table on the canvas
        table.wrapOn(p, StartX, StartY-270)
        table.drawOn(p, StartX-20, StartY-290)

        # Close the PDF object cleanly, and ensure we're at the beginning of the file.
        p.showPage()
        p.save()
        buffer.seek(0)

        pdf_path = 'Co-operative letter head.docx.pdf'



        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        can.drawString(10, 100, "Hello world")
        can.save()

        #move to the beginning of the StringIO buffer
        packet.seek(0)

        # create a new PDF with Reportlab
        new_pdf = PdfReader(buffer)
        # read your existing PDF
        existing_pdf = PdfReader(open(pdf_path, "rb"))
        output = PdfWriter()
        # add the "watermark" (which is the new pdf) on the existing page
        page = existing_pdf.pages[0]
        page.merge_page(new_pdf.pages[0])
        output.add_page(page)
        # finally, write "output" to a real file
        output_stream = open("destination.pdf", "wb")
        output.write(output_stream)
        output_stream.close()

        output_stream = open("destination.pdf", "rb")
        

        response = make_response(output_stream.read())
        response.headers['Content-Disposition'] = 'attachment; filename=destination.pdf'
        response.headers['Content-type'] = 'application/pdf'

    return response

@blueprint.route('/Share_report_download' , methods=['GET', 'POST'])
def Share_report_download():
    reportform= ReportForm()
    if request.method == 'POST':

        financialYear = request.form['FinancialYear']
        # membercode = request.form['MemberCode']
        members = Members.query.all()

        year1 = int(financialYear[0:4])
        if request.form['FromDate'] : 
            fromDate = request.form['FromDate']
        else :
            fromDate = str(year1) + "-04-01"
        
        if request.form['ToDate'] : 
            toDate = request.form['ToDate']
        else :
            toDate = str(year1+1) + "-03-31"

        
        
        if request.form['MemberCode'] : 
            shares = Shares.query.filter(and_(Shares.ShareCreateDate >= fromDate, Shares.ShareCreateDate <= toDate , Shares.member_id == request.form['MemberCode'] ))
        else :  
            shares = Shares.query.filter(and_(Shares.ShareCreateDate >= fromDate, Shares.ShareCreateDate <= toDate))

        # Create a file-like buffer to receive PDF data.
        buffer = BytesIO()

        # Create the PDF object, using the buffer as its "file."
        p = canvas.Canvas(buffer, (1200,700))

        StartY = 500
        StartX = 50
        today = datetime.date.today()
        year = today.year
        month = today.month
        day = today.day
        datestring = str(day) + "/" +  str(month) + "/" +  str(year)

        # Add some custom text (you can customize this part as needed)
        p.drawString(StartX + 420, StartY + 90, datestring )

        activeMembers = Members.query.filter(and_(Members.MemberDate >= fromDate, Members.MemberDate <= toDate, Members.Active == 1 , Members.ShareBalance > 0 )).count()
        openingBalance = 0
        currentBalance = 0
        closedaccount = 0

        for member in members :
            currentBalance += member.ShareBalance
            share = Shares.query.filter(and_(Shares.ShareCreateDate >= fromDate, Shares.ShareCreateDate <= toDate , Shares.member_id == member.userid )).first()
            if share :
                openingBalance += int(share.ShareTotalAmount)
                if int(share.ShareTotalAmount) != 0 :
                    if member.ShareBalance == 0 :
                        closedaccount += 1



        # Add some custom text (you can customize this part as needed)
        p.drawString(StartX, StartY, "Financial Year : " + financialYear )
        p.drawString(StartX, StartY-20, "Total Number of Active Members : " + str(activeMembers))
        p.drawString(StartX, StartY-40, "Total Number of Member closed their A/C : " + str(closedaccount))
        p.drawString(StartX, StartY-60, "Opening Share Balance : " + str(openingBalance))
        p.drawString(StartX, StartY-80, "Current Share Balance : " + str(currentBalance))

        data = [
            ["S.No.", "Member Code", "Member Name", "Share Credit", "Share Debit", "Payment Method", "Bank A/C Number" , "Transaction #"],
        ]

        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ])

        table_data = [data[0]]

        for idx, share in enumerate(shares) :
            member = Members.query.filter_by(userid=share.member_id).first()
            amount = 0
            if share.ShareTotalAmount :
                amount = share.ShareTotalAmount
            else :
                amount = share.CreditShareAmount
            # modeofpayment = ""
            # transactionid = ""
            # if thriftFund.Thrift_Credit_Amount : 
            #     modeofpayment = thriftFund.Thrift_Credit_PayMethod
            #     transactionid = thriftFund.Thrift_Credit_TransactionID
            # else :
            #     modeofpayment = thriftFund.Thrift_Debit_PayMethod
            #     transactionid = thriftFund.Thrift_Debit_TransactionID
            row = [idx+1, member.userid, member.firstname + " " + member.lastname,amount, share.DebitShareAmount,share.DebitSharePayMethod,member.accountno,share.DebitShareTransactionID]
            table_data.append(row)

        # Other data can be added as necessary

        table = Table(table_data)
        table.setStyle(table_style)

        # Draw the table on the canvas
        table.wrapOn(p, StartX, StartY-270)
        table.drawOn(p, StartX-20, StartY-290)

        # Close the PDF object cleanly, and ensure we're at the beginning of the file.
        p.showPage()
        p.save()
        buffer.seek(0)

        pdf_path = 'Co-operative letter head.docx.pdf'



        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        can.drawString(10, 100, "Hello world")
        can.save()

        #move to the beginning of the StringIO buffer
        packet.seek(0)

        # create a new PDF with Reportlab
        new_pdf = PdfReader(buffer)
        # read your existing PDF
        existing_pdf = PdfReader(open(pdf_path, "rb"))
        output = PdfWriter()
        # add the "watermark" (which is the new pdf) on the existing page
        page = existing_pdf.pages[0]
        page.merge_page(new_pdf.pages[0])
        output.add_page(page)
        # finally, write "output" to a real file
        output_stream = open("destination.pdf", "wb")
        output.write(output_stream)
        output_stream.close()

        output_stream = open("destination.pdf", "rb")
        

        response = make_response(output_stream.read())
        response.headers['Content-Disposition'] = 'attachment; filename=destination.pdf'
        response.headers['Content-type'] = 'application/pdf'

    return response




@blueprint.route('/member_report_download' , methods=['GET', 'POST'])
def member_report_download():
    reportform= ReportForm()
    if request.method == 'POST':

        financialYear = request.form['FinancialYear']
        year1 = int(financialYear[0:4])
        if request.form['FromDate'] : 
            fromDate = request.form['FromDate']
        else :
            fromDate = str(year1) + "-04-01"
        
        if request.form['ToDate'] : 
            toDate = request.form['ToDate']
        else :
            toDate = str(year1+1) + "-03-31"

        # membercode = request.form['MemberCode']
        members = Members.query.filter(and_(Members.MemberDate >= fromDate, Members.MemberDate <= toDate))
        print(toDate)
        print(fromDate)
        totalmembers = Members.query.filter(and_(Members.MemberDate >= fromDate, Members.MemberDate <= toDate)).count()
        activeMembers = Members.query.filter(and_(Members.MemberDate >= fromDate, Members.MemberDate <= toDate, Members.Active == 1)).count()
        nonactiveMembers = Members.query.filter(and_(Members.MemberDate >= fromDate, Members.MemberDate <= toDate, Members.Active == 0)).count()
        # thriftFunds = ThriftFunds.query.all()


        # Create a file-like buffer to receive PDF data.
        buffer = BytesIO()

        # Create the PDF object, using the buffer as its "file."
        print(landscape(letter))
        p = canvas.Canvas(buffer, (1200,700))

        StartY = 500
        StartX = 50
        # today = datetime.date.today()
        today = datetime.date.today()
        year = today.year
        month = today.month
        day = today.day
        datestring = str(day) + "/" +  str(month) + "/" +  str(year)

        # Add some custom text (you can customize this part as needed)
        p.drawString(StartX + 420, StartY + 90, datestring )


        p.drawString(StartX, StartY, "Number of Members : " + str(totalmembers) )
        p.drawString(StartX, StartY - 20 , "Address : Regd. 203, Hari Om Commercial Complex, New Dak Bunglow Road" )
        p.drawString(StartX, StartY-40, "City : Patna")
        p.drawString(StartX, StartY-60, "Country : India")
        p.drawString(StartX, StartY-80, "Pincode : 800001" )
        p.drawString(StartX, StartY-100, "Number of Active Members : " + str(activeMembers) )
        p.drawString(StartX, StartY-120, "Number of Deactivated Members : " + str(nonactiveMembers))

        data = [
            ["S.No.", "Member Joining Date","Member Code", "Member Name", "Member Address", "Member Phone Number", "Thrift Balance", "Loan Balance", "Shares Balance"],
        ]

        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 6),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 2),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ])

        table_data = [data[0]]

        for idx, member in enumerate(members) :
            # member = Members.query.filter_by(id=thriftFund.member_id).first()
            row = [idx+1,member.MemberDate, member.userid, member.firstname + " " + member.lastname,member.address_line1 ,member.phoneno,member.Thrift_FundBalance,member.LoanAmount,member.ShareBalance]
            table_data.append(row)

        # Other data can be added as necessary

        table = Table(table_data)
        table.setStyle(table_style)

        # Draw the table on the canvas
        table.wrapOn(p, StartX, StartY-270)
        table.drawOn(p, StartX-20, StartY-290)

        # Close the PDF object cleanly, and ensure we're at the beginning of the file.
        p.showPage()
        p.save()
        buffer.seek(0)

        pdf_path = 'Co-operative letter head.docx.pdf'


        # create a new PDF with Reportlab
        new_pdf = PdfReader(buffer)
        # read your existing PDF
        existing_pdf = PdfReader(open(pdf_path, "rb"))
        output = PdfWriter()
        # add the "watermark" (which is the new pdf) on the existing page
        page = existing_pdf.pages[0]
        page.merge_page(new_pdf.pages[0])
        output.add_page(page)
        # finally, write "output" to a real file
        output_stream = open("destination.pdf", "wb")
        output.write(output_stream)
        output_stream.close()

        output_stream = open("destination.pdf", "rb")
        

        response = make_response(output_stream.read())
        response.headers['Content-Disposition'] = 'attachment; filename=destination.pdf'
        response.headers['Content-type'] = 'application/pdf'

    return response


@blueprint.route('/business_report_download' , methods=['GET', 'POST'])
def business_report_download():
    reportform= ReportForm()
    if request.method == 'POST':

        financialYear = request.form['FinancialYear']
        year1 = int(financialYear[0:4])
        if request.form['FromDate'] : 
            fromDate = request.form['FromDate']
        else :
            fromDate = str(year1) + "-04-01"
        
        if request.form['ToDate'] : 
            toDate = request.form['ToDate']
        else :
            toDate = str(year1+1) + "-03-31"

        # membercode = request.form['MemberCode']
        members = Members.query.filter(and_(Members.MemberDate >= fromDate, Members.MemberDate <= toDate))
        print(toDate)
        print(fromDate)
        totalmembers = Members.query.filter(and_(Members.MemberDate >= fromDate, Members.MemberDate <= toDate)).count()
        activeMembers = Members.query.filter(and_(Members.MemberDate >= fromDate, Members.MemberDate <= toDate, Members.Active == 1)).count()
        nonactiveMembers = Members.query.filter(and_(Members.MemberDate >= fromDate, Members.MemberDate <= toDate, Members.Active == 0)).count()
        # thriftFunds = ThriftFunds.query.all()


        # Create a file-like buffer to receive PDF data.
        buffer = BytesIO()

        # Create the PDF object, using the buffer as its "file."
        print(landscape(letter))
        p = canvas.Canvas(buffer, (1200,700))

        StartY = 500
        StartX = 50
        # today = datetime.date.today()
        today = datetime.date.today()
        year = today.year
        month = today.month
        day = today.day
        datestring = str(day) + "/" +  str(month) + "/" +  str(year)

        # Add some custom text (you can customize this part as needed)
        p.drawString(StartX + 420, StartY + 90, datestring )


        p.drawString(StartX, StartY, "Number of Members : " + str(totalmembers) )
        p.drawString(StartX, StartY - 20 , "Address : Regd. 203, Hari Om Commercial Complex, New Dak Bunglow Road" )
        p.drawString(StartX, StartY-40, "City : Patna")
        p.drawString(StartX, StartY-60, "Country : India")
        p.drawString(StartX, StartY-80, "Pincode : 800001" )
        p.drawString(StartX, StartY-100, "Number of Active Members : " + str(activeMembers) )
        p.drawString(StartX, StartY-120, "Number of Deactivated Members : " + str(nonactiveMembers))

        data = [
            ["S.No.", "Member Name" ,"Member Joining Date","Member Code", "Member Status", "Thrift Balance", "Loan Balance", "Total Number of Shares"],
        ]

        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 6),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 2),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ])

        table_data = [data[0]]

        for idx, member in enumerate(members) :
            # member = Members.query.filter_by(id=thriftFund.member_id).first()
            status = "Active"
            if member.Active == 0 :
                status = "Deactivated"
            row = [idx+1,member.firstname + " " + member.lastname,member.MemberDate, member.userid,status ,member.Thrift_FundBalance,member.LoanAmount,member.ShareBalance]
            table_data.append(row)

        # Other data can be added as necessary

        table = Table(table_data)
        table.setStyle(table_style)

        # Draw the table on the canvas
        table.wrapOn(p, StartX, StartY-270)
        table.drawOn(p, StartX-20, StartY-290)

        # Close the PDF object cleanly, and ensure we're at the beginning of the file.
        p.showPage()
        p.save()
        buffer.seek(0)

        pdf_path = 'Co-operative letter head.docx.pdf'


        # create a new PDF with Reportlab
        new_pdf = PdfReader(buffer)
        # read your existing PDF
        existing_pdf = PdfReader(open(pdf_path, "rb"))
        output = PdfWriter()
        # add the "watermark" (which is the new pdf) on the existing page
        page = existing_pdf.pages[0]
        page.merge_page(new_pdf.pages[0])
        output.add_page(page)
        # finally, write "output" to a real file
        output_stream = open("destination.pdf", "wb")
        output.write(output_stream)
        output_stream.close()

        output_stream = open("destination.pdf", "rb")
        

        response = make_response(output_stream.read())
        response.headers['Content-Disposition'] = 'attachment; filename=destination.pdf'
        response.headers['Content-type'] = 'application/pdf'

    return response

@blueprint.route('/MGI2', methods=['GET', 'POST'])
def MGI2():
    kycform = KYCForm(request.form)
    personalInfo = PersonalInfo()
    if 'email' not in session : 
        return render_template('pages/PI1.html', form=personalInfo)
    currmember = Members.query.filter_by(email=session['email']).first()


    if currmember :
        kycform.pf_no.data =  currmember.pf_no 
        kycform.gender.data =  currmember.gender 
        kycform.id_proof_name.data =  currmember.id_proof_name 
        kycform.id_proof_no.data =  currmember.id_proof_no 
        kycform.address_proof_name.data =  currmember.address_proof_name 
        kycform.address_proof_no.data =  currmember.address_proof_no 
        kycform.sign_proof_name.data =  currmember.sign_proof_name 
        kycform.pan_no.data =  currmember.pan_no 
    

    if request.method == 'POST':
        print("herer")
        currmember = Members.query.filter_by(email=session['email']).first()

        currmember.pf_no = request.form['pf_no']
        currmember.gender = request.form['gender']
        currmember.id_proof_name = request.form['id_proof_name']
        currmember.id_proof_no = request.form['id_proof_no']
        currmember.address_proof_name = request.form['address_proof_name']
        currmember.address_proof_no = request.form['address_proof_no']
        currmember.sign_proof_name = request.form['sign_proof_name']
        currmember.pan_no = request.form['pan_no']

        
        db.session.commit()
    return render_template('pages/MGI2.html', form=kycform)

@blueprint.route('/MBI3', methods=['GET', 'POST'])
def MBI3():
    memberbanking = MemberBankingForm(request.form)
    personalInfo = PersonalInfo()
    if 'email' not in session : 
        return render_template('pages/PI1.html', form=personalInfo)
    currmember = Members.query.filter_by(email=session['email']).first()

    if currmember :
        memberbanking.bankname.data =   currmember.bankname  
        memberbanking.branchName.data = currmember.branchName  
        memberbanking.accountno.data =  currmember.accountno  
        memberbanking.category.data =   currmember.category  
        memberbanking.ifsc_code.data =  currmember.ifsc_code  
        memberbanking.micr_code.data =  currmember.micr_code  

    if request.method == 'POST':
        print("herer")
        currmember = Members.query.filter_by(email=session['email']).first()

        currmember.bankname = request.form['bankname']
        currmember.branchName = request.form['branchName']
        currmember.accountno = request.form['accountno']
        currmember.category = request.form['category']
        currmember.ifsc_code = request.form['ifsc_code']
        currmember.micr_code = request.form['micr_code']

        
        db.session.commit()
    return render_template('pages/MBI3.html', form=memberbanking)

@blueprint.route('/NI4', methods=['GET', 'POST'])
def NI4():
    nomineeForm = NomineeForm(request.form)
    personalInfo = PersonalInfo()
    if 'email' not in session : 
        return render_template('pages/PI1.html', form=personalInfo)
    currmember = Members.query.filter_by(email=session['email']).first()

    if currmember :
        nomineeForm.nomi_name.data = currmember.nomi_name  
        nomineeForm.nomi_dob.data = currmember.nomi_dob  
        nomineeForm.nomi_age.data = currmember.nomi_age  
        nomineeForm.nomi_relation.data = currmember.nomi_relation  
        nomineeForm.nomi_per_share.data = currmember.nomi_per_share  

    if request.method == 'POST':
        print("herer")
        currmember = Members.query.filter_by(email=session['email']).first()

        currmember.nomi_name = request.form['nomi_name']
        currmember.nomi_dob = request.form['nomi_dob']
        currmember.nomi_age = request.form['nomi_age']
        currmember.nomi_relation = request.form['nomi_relation']
        currmember.nomi_per_share = request.form['nomi_per_share']        
        db.session.commit()

    return render_template('pages/NI4.html', form=nomineeForm)

@blueprint.route('/Edit', methods=['GET', 'POST'])
def Edit():
    personalInfo = PersonalInfo()
    if 'email' not in session : 
        return render_template('pages/PI1.html', form=personalInfo)
    currmember = Members.query.filter_by(email=session['email']).first()
    
    personalInfo = PersonalInfo(request.form)
    memberbanking = MemberBankingForm(request.form)
    nomineeForm = NomineeForm(request.form)
    kycform = KYCForm(request.form)

    if currmember : 
        personalInfo.firstname.data = currmember.firstname
        personalInfo.dob2.data = currmember.dob
        personalInfo.age.data = currmember.age
        personalInfo.gender.data = currmember.gender
        personalInfo.status.data = currmember.status
        personalInfo.guardian_firstname.data = currmember.guardian_firstname
        personalInfo.guardian_relation.data = currmember.guardian_relation
        personalInfo.phoneno.data = currmember.phoneno
        personalInfo.email.data = currmember.email
        personalInfo.address_line1.data = currmember.address_line1
        personalInfo.address_line2.data = currmember.address_line2
        personalInfo.state.data = currmember.state
        personalInfo.pincode.data = currmember.pincode

        kycform.pf_no.data =  currmember.pf_no 
        kycform.gender.data =  currmember.gender 
        kycform.id_proof_name.data =  currmember.id_proof_name 
        kycform.id_proof_no.data =  currmember.id_proof_no 
        kycform.address_proof_name.data =  currmember.address_proof_name 
        kycform.address_proof_no.data =  currmember.address_proof_no 
        kycform.sign_proof_name.data =  currmember.sign_proof_name 
        kycform.pan_no.data =  currmember.pan_no 

        memberbanking.bankname.data =   currmember.bankname  
        memberbanking.branchName.data = currmember.branchName  
        memberbanking.accountno.data =  currmember.accountno  
        memberbanking.category.data =   currmember.category  
        memberbanking.ifsc_code.data =  currmember.ifsc_code  
        memberbanking.micr_code.data =  currmember.micr_code  

        nomineeForm.nomi_name.data = currmember.nomi_name  
        nomineeForm.nomi_dob2.data = currmember.nomi_dob  
        nomineeForm.nomi_age.data = currmember.nomi_age  
        nomineeForm.nomi_relation.data = currmember.nomi_relation  
        nomineeForm.nomi_per_share.data = currmember.nomi_per_share  

    return render_template('pages/Edit.html',form=personalInfo,form1 =kycform,form2 = memberbanking, form3 = nomineeForm, currmember=currmember)

@blueprint.route('/Thrift', methods=['GET', 'POST'])
def Thrift():
    SearchForm = Search(request.form)
    Tform = ThriftFund(request.form)
    Tform1 = ThriftFund1(request.form)
    Tform2 = ThriftFund2(request.form)
    Tform3 = ThriftFund3(request.form)
    

    if request.method == 'POST':
        print("herer")
        
        if 'payment_method' in request.form :
            currmember = Members.query.filter_by(email=session['email']).first()
            form_data = {
                'Thrift_Credit_Amount': request.form['total_amount'],
                'Thrift_Credit_Mobile': request.form['phoneno'],
                'Thrift_Credit_PayMethod'  : request.form['payment_method'],
                'Thrift_Credit_TransactionID' : request.form['transcation_id'],
                'member_id' : currmember.userid,
                'ThriftCreateDate' : datetime.date.today(),
                'ThriftBalance' : currmember.Thrift_FundBalance + int(request.form['total_amount']),
                
            }
            currmember = Members.query.filter_by(email=session['email']).first()
            currmember.Thrift_FundBalance += int(request.form['total_amount'])
            thriftFund = ThriftFunds(**form_data)
            db.session.add(thriftFund)
            db.session.commit()

        if 'transfer' in request.form : 
            currmember = Members.query.filter_by(email=session['email']).first()
            form_data = {
                'Thrift_Debit_Amount': request.form['amount'],
                'Thrift_Debit_Transfer': request.form['transfer'],
                'Thrift_Debit_PayMethod'  : request.form['mode_of_transaction'],
                'Thrift_Debit_TransactionID' : request.form['transcation_id2'],
                'Thrift_Debit_ChequeNo' : request.form['cheque_number'],
                'member_id' : currmember.userid,
                'ThriftCreateDate' : datetime.date.today(),
                'ThriftBalance' : currmember.Thrift_FundBalance - int(request.form['amount'])
            }
            currmember.Thrift_FundBalance -= int(request.form['amount'])
            thriftFund = ThriftFunds(**form_data)
            db.session.add(thriftFund)
            db.session.commit()

        if 'text' in request.form : 
            query = request.form['text']
            currmember = Members.query.filter_by(userid=query).first()
            session['email']  = currmember.email
        
        transactions = []
        if session['email'] :
            currmember = Members.query.filter_by(email=session['email']).first()
            transactions = ThriftFunds.query.filter_by(member_id = currmember.userid).with_entities(ThriftFunds.Thrift_Credit_Amount, ThriftFunds.Thrift_Credit_TransactionID, ThriftFunds.Thrift_Debit_Amount,ThriftFunds.Thrift_Debit_TransactionID).all()
        
        return render_template('pages/Thrift.html',form=Tform,form1=Tform1,form2=Tform2,form3=Tform3, currmember=currmember,search = SearchForm,hid=True, transactions = transactions)


    return render_template('pages/Thrift.html',form=Tform,form1=Tform1,form2=Tform2,form3=Tform3,search = SearchForm,hid=False)

@blueprint.route('/Share', methods=['GET', 'POST'])
def Share():
    SearchForm = Search(request.form)
    Sform = ShareForm(request.form)
    Sform1 = ShareForm1(request.form)
    Sform2 = ShareForm2(request.form)

    globalValues = GlobalValues.query.first()
    PerShareAmount = globalValues.PerShareAmount


    if request.method == 'POST':
        

        if 'Office_Name' in request.form :
            currmember = Members.query.filter_by(email=session['email']).first()
            form_data = {
                'member_id' : currmember.userid,
                'ShareDateofJoinig': request.form['DateofJoin'],
                'ShareDateofAllotment': request.form['DateofAllotment'],
                'ShareOfficeName': request.form['Office_Name'],
                'ShareDateofRetirement': request.form['DateofRetirement'],
                'ShareTotalAmount': request.form['investAmount'],
                'ShareCreateDate' : datetime.date.today(),
                'ApprovedStatus' : 'Pending'
            }
            shares = float(float(request.form['investAmount']) / PerShareAmount )
            currmember.ShareBalance += shares
            share = Shares(**form_data)
            db.session.add(share)
            db.session.commit()
        
        if 'investAmount2' in request.form :
            currmember = Members.query.filter_by(email=session['email']).first()
            form_data = {
                'member_id' : currmember.userid,
                'CreditShareAmount': request.form['investAmount2'],
                'ShareCreateDate' : datetime.date.today()
                
            }
            shares = float(float(request.form['investAmount2']) / PerShareAmount )
            currmember.ShareBalance += shares
            share = Shares(**form_data)
            db.session.add(share)
            db.session.commit()

        if 'mode_of_transaction' in request.form :
            currmember = Members.query.filter_by(email=session['email']).first()
            form_data = {
                'member_id' : currmember.userid,
                'DebitShareAmount': request.form['amount'],
                'DebitSharePayMethod': request.form['mode_of_transaction'],
                'DebitShareChequeNo': request.form['cheque_number'],
                'DebitShareTransactionID': request.form['transcation_id2'],
                'ShareCreateDate' : datetime.date.today()
            }
            shares = float(float(request.form['amount']) / PerShareAmount )
            currmember.ShareBalance -= shares
            share = Shares(**form_data)
            db.session.add(share)
            db.session.commit()


        if 'text' in request.form : 
            query = request.form['text']
            currmember = Members.query.filter_by(userid=query).first()
            session['email']  = currmember.email

        transactions = Shares.query.filter_by(member_id = currmember.userid).with_entities(Shares.member_id, Shares.CreditShareAmount, Shares.DebitShareAmount).all()
        print(transactions)
        return render_template('pages/Share.html',search=SearchForm,form=Sform,form1=Sform1,form2=Sform2,currmember=currmember,hid=True,PerShareAmount = PerShareAmount, transactions=transactions)

    return render_template('pages/Share.html',search=SearchForm,form=Sform,form1=Sform1,form2=Sform2,hid=False)

@blueprint.route('/loan', methods=['GET', 'POST'])
def loan():
    SearchForm = Search(request.form)
    Lform = LoanForm(request.form)
    Lform1 = LoanForm1(request.form)
    Lform2 = LoanForm2(request.form)
    Lform3 = LoanForm3(request.form)

    globalValues = GlobalValues.query.first()
    rateofInterest = globalValues.rateofInterest
    

    if request.method == 'POST':
        
        if 'LoanAmount' in request.form :
            currmember = Members.query.filter_by(email=session['email']).first()
            form_data = {
                'member_id': currmember.userid,
                'LoanOfficeName': request.form['Office_Name'],
                'LoanType': request.form['Loan_Type'],
                'LoanDate' : datetime.date.today(),
                'LoanAmount': request.form['LoanAmount'],
                'ApprovedStatus' : 'Pending'
            }
            currmember.LoanAmount += int(request.form['LoanAmount'])
            currmember.LoanEMIAmount = currmember.LoanAmount*0.001*16.60
            loan = Loan(**form_data)
            db.session.add(loan)
            db.session.commit()

        if 'EmployeeName' in request.form : 
            currmember = Members.query.filter_by(email=session['email']).first()
            currLoan = Loan.query.filter_by(member_id=currmember.userid).first()
            currLoan.EmployeeName = request.form['EmployeeName']
            currLoan.EmployeeCode = request.form['EmployeeCode']
            currLoan.EmployeePhoneNo = request.form['EmployeePhoneNo']
            currLoan.MemberName = request.form['MemberName']
            currLoan.MemberCode = request.form['MemberCode']
            currLoan.MemberPhoneNo = request.form['MemberPhoneNo']
            
            db.session.commit()
        
        if 'Amount2' in request.form :
            currmember = Members.query.filter_by(email=session['email']).first()
            currLoan = Loan.query.filter_by(member_id=currmember.userid).first()
            form_data = {
                'member_id': currmember.userid,
                'Amount': request.form['Amount2'],
                'PaymentMode': request.form['Payment_Mode'],
                'TransactionID' : request.form['TransactionID'],
                'TransactionDate': datetime.date.today(),
                'Interest' : 0
            }
            
            transaction = LoanDebitTransactions(**form_data)
            db.session.add(transaction)
            db.session.commit()
            cnt = LoanDebitTransactions.query.filter_by(member_id=currmember.userid).count()
            if cnt != 1 :
                lasttransaction = LoanDebitTransactions.query.filter_by(id = int(transaction.id)-1).first()
                last_date = lasttransaction.TransactionDate
                date_time_obj = datetime.datetime.strptime(last_date, '%Y-%m-%d')
                delta = datetime.date.today() - datetime.datetime.date(date_time_obj)
                noOfDays = delta.days
                interest = (currmember.LoanAmount*rateofInterest*noOfDays)/36500
                transaction.Interest = round(interest)
            
            currmember.LoanAmount -= int(request.form['Amount2'])
            currmember.LoanEMIAmount = currmember.LoanAmount*0.001*16.60
            db.session.commit()
        
        if 'Amount3' in request.form :
            currmember = Members.query.filter_by(email=session['email']).first()
            currLoan = Loan.query.filter_by(member_id=currmember.userid).first()

            form_data = {
                'member_id': currmember.userid,
                'Amount': request.form['Amount3'],
                'PaymentMode': request.form['Payment_Mode2'],
                'TransactionID' : request.form['TransactionID2'],
                'TransactionDate': datetime.date.today(),
                'Interest' : 0
            }
            transaction = LoanDebitTransactions(**form_data)
            db.session.add(transaction)
            db.session.commit()
            cnt = LoanDebitTransactions.query.filter_by(member_id=currmember.userid).count()
            if cnt != 1 :
                lasttransaction = LoanDebitTransactions.query.filter_by(id = int(transaction.id)-1).first()
                last_date = lasttransaction.TransactionDate
                date_time_obj = datetime.datetime.strptime(last_date, '%Y-%m-%d')
                delta = datetime.date.today() - datetime.datetime.date(date_time_obj)
                noOfDays = delta.days
                interest = (currmember.LoanAmount*rateofInterest*noOfDays)/36500
                transaction.Interest = round(interest)
            
            currmember.LoanAmount -= int(request.form['Amount3'])
            currmember.LoanEMIAmount = currmember.LoanAmount*0.001*16.60
            db.session.commit()

        if 'text' in request.form : 
            query = request.form['text']
            currmember = Members.query.filter_by(userid=query).first()
            session['email']  = currmember.email
        
        transactions = LoanDebitTransactions.query.filter_by(member_id = currmember.userid).with_entities(LoanDebitTransactions.Amount, LoanDebitTransactions.PaymentMode, LoanDebitTransactions.TransactionDate, LoanDebitTransactions.Interest).all()
        sum = 0
        sumInterest = 0
        for i in transactions :
            print(i)
            sum+= int(i.Amount)
            sumInterest+= float(i.Interest)
        return render_template('pages/loan.html',form=Lform,form1=Lform1,form2=Lform2,form3=Lform3, currmember=currmember,search = SearchForm,hid=True, transactions= transactions,sum=round(sum),sumInterest=round(sumInterest) ,tenure = globalValues.tenure,limit = globalValues.limit,processingFee = globalValues.processingFee,variable = globalValues.variable)


    return render_template('pages/loan.html',form=Lform,form1=Lform1,form2=Lform2,form3=Lform3,search = SearchForm,hid=False)

@blueprint.route('/Global_update', methods=['GET', 'POST'])
def GlobalUpdate():
    global_values = GlobalValues.query.first()
    if request.method == 'POST':
        if 'tenure' in request.form :
            global_values.tenure = request.form['tenure']
            db.session.commit()
        elif 'limit' in request.form :
            global_values.limit = request.form['limit']
            db.session.commit()
        elif 'pfees' in request.form :
            global_values.processingFee = request.form['pfees']
            db.session.commit()
        elif 'roi' in request.form :
            global_values.rateofInterest = request.form['roi']
            db.session.commit()
        elif 'variable' in request.form :
            global_values.variable = request.form['variable']
            db.session.commit()

    return render_template('pages/Global_update.html',tenure= global_values.tenure,limit= global_values.limit,pfees= global_values.processingFee,roi= global_values.rateofInterest, variable= global_values.variable)


@blueprint.route('/report', methods=['GET', 'POST'])
def report():
    return render_template('pages/report.html')

@blueprint.route('/demo', methods=['GET', 'POST'])
def demo():
    return render_template('pages/demo.html')

@blueprint.route('/member', methods=['GET', 'POST'])
def member():
    reportform = ReportForm()
    return render_template('pages/member.html', form=reportform)

@blueprint.route('/business', methods=['GET', 'POST'])
def business():
    reportform = ReportForm()
    return render_template('pages/business.html',form=reportform)

@blueprint.route('/Thrift_Fund_report', methods=['GET', 'POST'])
def Thrift_Fund_report():
    reportform = ReportForm()
    return render_template('pages/Thrift_Fund_Report.html', form=reportform)

@blueprint.route('/Loan_Report', methods=['GET', 'POST'])
def Loan_Report():
    reportform = ReportForm()
    return render_template('pages/Loan_Report.html',form=reportform)


@blueprint.route('/Shares_Report', methods=['GET', 'POST'])
def Shares_Report():
    reportform = ReportForm()
    return render_template('pages/Shares_Report.html', form=reportform)

@blueprint.route('/admin_update', methods=['GET', 'POST'])
def admin_update():
    return render_template('pages/admin_update.html')


@blueprint.route('/member_approval/<id>', methods=['GET', 'POST'])
def member_approval(id):
    member = Members.query.filter_by(userid=id).first()
    return render_template('pages/member_approval.html',member=member)


@blueprint.route('/loan_approval/<id>', methods=['GET', 'POST'])
def loan_approval(id):
    loan = Loan.query.filter_by(member_id=id).first()
    return render_template('pages/loan_approval.html',loan=loan)


@blueprint.route('/share_approval/<id>', methods=['GET', 'POST'])
def share_approval(id):
    share = Shares.query.filter_by(member_id=id).first()
    return render_template('pages/share_approval.html',share=share)


@blueprint.route('/Thrift_approval', methods=['GET', 'POST'])
def Thrift_approval():
    return render_template('pages/Thrift_approval.html')
@blueprint.route('/Global_update', methods=['GET', 'POST'])
def Global_update():
    return render_template('pages/Global_update.html')


@blueprint.route('/member_approval_list', methods=['GET', 'POST'])
def member_approval_list():
    members = Members.query.filter_by(ApprovedStatus="Pending").all()
    # print(members.count())
    return render_template('pages/member_approval_list.html',members=members)


@blueprint.route('/loan_approval_list', methods=['GET', 'POST'])
def loan_approval_list():
    loans = Loan.query.filter_by(ApprovedStatus="Pending").all()
    return render_template('pages/loan_approval_list.html',loans=loans)


@blueprint.route('/share_approval_list', methods=['GET', 'POST'])
def share_approval_list():
    shares = Shares.query.filter_by(ApprovedStatus="Pending").all()
    return render_template('pages/share_approval_list.html', shares=shares)

@blueprint.route('/deny_member/<id>', methods=['GET', 'POST'])
def deny_member (id):
    member = Members.query.filter_by(userid=id).first()

    member.ApprovedStatus = "Denied"
    db.session.commit()
    members = Members.query.filter_by(ApprovedStatus="Pending").all()
    return render_template('pages/member_approval_list.html',members=members)

@blueprint.route('/approve_member/<id>', methods=['GET', 'POST'])
def approve_member (id):
    member = Members.query.filter_by(userid=id).first()

    member.ApprovedStatus = "Approved"
    db.session.commit()
    members = Members.query.filter_by(ApprovedStatus="Pending").all()
    return render_template('pages/member_approval_list.html',members=members)

@blueprint.route('/deny_share/<id>', methods=['GET', 'POST'])
def deny_share (id):
    share = Shares.query.filter_by(member_id=id, ApprovedStatus="Pending").first()

    share.ApprovedStatus = "Denied"
    db.session.commit()
    shares = Shares.query.filter_by(ApprovedStatus="Pending").all()
    return render_template('pages/share_approval_list.html',shares=shares)

@blueprint.route('/approve_share/<id>', methods=['GET', 'POST'])
def approve_share (id):
    share = Shares.query.filter_by(member_id=id, ApprovedStatus="Pending").first()

    share.ApprovedStatus = "Approved"
    db.session.commit()
    shares = Shares.query.filter_by(ApprovedStatus="Pending").all()
    return render_template('pages/share_approval_list.html',shares=shares)


@blueprint.route('/deny_loan/<id>', methods=['GET', 'POST'])
def deny_loan (id):
    loan = Loan.query.filter_by(member_id=id, ApprovedStatus="Pending").first()

    loan.ApprovedStatus = "Denied"
    db.session.commit()
    loans = Loan.query.filter_by(ApprovedStatus="Pending").all()
    return render_template('pages/loan_approval_list.html',loans=loans)

@blueprint.route('/approve_loan/<id>', methods=['GET', 'POST'])
def approve_loan (id):
    loan = Loan.query.filter_by(member_id=id, ApprovedStatus="Pending").first()

    loan.ApprovedStatus = "Approved"
    db.session.commit()
    loans = Loan.query.filter_by(ApprovedStatus="Pending").all()
    return render_template('pages/loan_approval_list.html',loans=loans)



# @blueprint.route('/firstVisit', methods=['GET', 'POST'])
# def firstVisit():
#     recipes = Recipes.query.filter_by(authorusername=session['username'])
#     user = Users.query.filter_by(username=session['username']).first()
#     additionalForm = AdditionalUserInfo()
#     if request.method == 'POST':

#         aboutauthor = request.form['aboutauthor']
#         user.about = aboutauthor

#         foodprefs = request.form.getlist('tags')
#         favcuisines = request.form.getlist('cuisines')

#         tags = request.form.getlist('tags')



#         for tag in foodprefs :
#             parts = tag.split(',')
#             tags_part = [x.strip('[]""') for x in parts]
#             for tag_child in tags_part:
#                 foodpref = FoodPreference(user_id = user.id , foodpref = tag_child)
#                 db.session.add(foodpref)


#         for tag in favcuisines :
#             parts = tag.split(',')
#             tags_part = [x.strip('[]""') for x in parts]
#             for tag_child in tags_part:
#                 favcuisine = FavCuisine(user_id = user.id , favcuisine = tag_child)
#                 db.session.add(favcuisine)
        
#         db.session.commit()
        
#         curr_user = session['username']
#         user = Users.query.filter_by(username=session['username']).first()

#         recipes = Recipes.query.filter_by(authorusername=curr_user).with_entities(Recipes.description, Recipes.dishname ,Recipes.id).all()
#         return redirect(url_for('authentication_blueprint.author'))  
#     else:
#         return render_template('home/author.html' ,recipes = recipes, user=user, form=additionalForm , flag = True)


# @blueprint.route('/author', methods=['GET', 'POST'])
# def author():
#     recipes = Recipes.query.filter_by(authorusername=session['username'])
#     user = Users.query.filter_by(username=session['username']).first()
#     additionalForm = AdditionalUserInfo()
#     favCuisines = FavCuisine.query.filter_by(user_id = user.id)
#     foodPreferences = FoodPreference.query.filter_by(user_id = user.id)
#     likedrecipes = db.session.query(Recipes).join(Likes).filter(Likes.user_id == user.id).all()
#     numberofSuggestions = Suggestions.query.filter_by(authorusername=user.username).count()
#     return render_template('home/author.html' ,recipes = recipes, user=user, form=additionalForm ,favCuisines=favCuisines, foodPreferences=foodPreferences,flag = False, likedrecipes = likedrecipes, numberofSuggestions = numberofSuggestions)



# @blueprint.route('/dashboard', methods=['GET', 'POST'])
# def dashboard():
#     recipes = Recipes.query.filter(Recipes.id == None)
#     searchForm = Search()
    
#     if request.method == 'POST':
#         query = request.form['text']
#         tags = request.form['tags']
#         print(request.form)
#         if 'username' in session :
#             user = Users.query.filter_by(username=session['username']).first()
#             search = SearchQueries(searchQuery = query , user_id=user.id)
#             db.session.add(search)
#             db.session.commit()

#         tags = tags.replace('[','').replace(']','').replace('"','').split(',')
#         for tag in tags:
#             currRecipe = db.session.query(Recipes).join(Labels).filter(Labels.recipe_id == Recipes.id).filter(Labels.label == tag)
#             recipes = recipes.union_all(currRecipe)

#         recipes = recipes.filter(Recipes.dishname.like("%"+query+"%")).all()
#         return render_template('home/dashboard.html' ,recipes = recipes, form=searchForm)
#     else :
#         recipes = Recipes.query.all()
#     return render_template('home/dashboard.html' ,recipes = recipes, form=searchForm)

# @blueprint.route('/recommend', methods=['GET', 'POST'])    
# def get_recommended_recipes(num_recommendations=5):
#     user = Users.query.filter_by(username=session['username']).first()
#     liked_recipes_tags_list = db.session.query(Labels).join(db.session.query(Recipes).join(Likes).filter(Likes.user_id == user.id)).filter(Recipes.id == Labels.recipe_id)
#     liked_recipe_tags = [recipe.label for recipe in liked_recipes_tags_list]
#     common_tags = [tag for tag, count in Counter(liked_recipe_tags).most_common(1)]
#     recipes = Recipes.query.join(Labels).filter(Labels.label.in_(common_tags)).limit(num_recommendations).all()

#     liked_recipes = db.session.query(Recipes).join(Likes).filter(Likes.user_id == user.id)
#     liked_recipe_authors = [recipe.authorusername for recipe in liked_recipes ]
#     # return recommended_recipes
#     recipes = Recipes.query.filter(Recipes.authorusername.in_(liked_recipe_authors)).all()
#     return render_template('home/recommend.html' ,recipes = recipes)

# @blueprint.route('/view-notifications', methods=['GET', 'POST'])    
# def viewnotif():
#     user = Users.query.filter_by(username=session['username']).first()
#     suggestions=  Suggestions.query.filter_by(authorusername=session['username']).all()
#     recipe_with_suggestions = [item.recipeid for item in suggestions]
#     recipes = Recipes.query.filter(Recipes.id.in_(recipe_with_suggestions)).all()
#     return render_template('home/view-notifications.html' ,recipes = recipes)
