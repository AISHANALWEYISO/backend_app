import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


GMAIL_USER     = os.getenv('GMAIL_USER', 'nalweyisoa22@gmail.com')
GMAIL_PASSWORD = os.getenv('GMAIL_APP_PASSWORD', 'tgqurrvoduppghpv')
ADMIN_EMAIL    = os.getenv('GMAIL_USER', 'nalweyisoa22@gmail.com')

MTN_NUMBER     = os.getenv('MTN_NUMBER',   '0766753527')
AIRTEL_NUMBER  = os.getenv('AIRTEL_NUMBER','0750163604')


def send_email(to_email: str, subject: str, body: str) -> bool:
    """Send an email using Gmail SMTP. Returns True on success."""
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From']    = f"Yucca Agro <{GMAIL_USER}>"
        msg['To']      = to_email

        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(GMAIL_USER, GMAIL_PASSWORD)
            smtp.send_message(msg)

        print(f" Email sent to {to_email}")
        return True

    except Exception as e:
        print(f" Email failed: {e}")
        return False


# Email Templates 

def email_order_created(farmer_name, farmer_email, order_ref,
                        amount, credits, package, payment_method):
    """
    Sent to farmer after they create an order.
    Tells them which number to send money to and what to do next.
    """
    send_to = MTN_NUMBER if payment_method.upper() == 'MTN' else AIRTEL_NUMBER

    subject = f"Yucca Agro – Payment Instructions for {order_ref}"

    body = f"""Dear {farmer_name},

Thank you for choosing Yucca Agro!

Your order has been created. Please follow the steps below to complete your payment:

ORDER DETAILS
Order Reference : {order_ref}
Package         : {package}
Credits         : {credits} scan(s)
Amount          : UGX {amount:,}
Payment Method  : {payment_method}

HOW TO PAY

1. Send UGX {amount:,} to {payment_method} number: {send_to}
2. Use "{order_ref}" as your payment reference/reason
3. After sending, you will receive an SMS with a Transaction ID
   e.g: "TXN123456789"
4. Copy that Transaction ID
5. Go back to the Yucca Agro app and enter the Transaction ID


IMPORTANT

- Credits are added after we verify your payment
- Verification takes a few minutes
- Keep your Transaction ID safe

If you have any issues, reply to this email.

Happy Farming! 
Yucca Agro Team
"""
    send_email(farmer_email, subject, body)


def email_admin_new_payment(farmer_name, farmer_email, farmer_phone,
                             order_ref, amount, credits, package,
                             payment_method, transaction_id, order_id):
    """
    Sent to admin (Aisha) when farmer submits their transaction ID.
    """
    subject = f" New Payment Submitted – {order_ref}"

    body = f"""New payment submitted on Yucca Agro!


FARMER DETAILS

Name           : {farmer_name}
Email          : {farmer_email}
Phone          : {farmer_phone}


PAYMENT DETAILS

Order Ref      : {order_ref}
Package        : {package}
Credits        : {credits} scan(s)
Amount         : UGX {amount:,}
Method         : {payment_method}
Transaction ID : {transaction_id}


ACTION REQUIRED

1. Check your {payment_method} app/phone to confirm 
   UGX {amount:,} was received from the farmer

2. If confirmed, approve using Postman:
   POST /api/payment/admin/approve/{order_id}
   Headers: Authorization: Bearer YOUR_ADMIN_TOKEN

3. If not received, reject using Postman:
   POST /api/payment/admin/reject/{order_id}
   Body: {{"reason": "Transaction ID not found"}}



Yucca Agro System
"""
    send_email(ADMIN_EMAIL, subject, body)


def email_payment_approved(farmer_name, farmer_email,
                            order_ref, credits, total_credits):
    """
    Sent to farmer when admin approves their payment.
    """
    subject = f" Payment Approved – {credits} Credits Added!"

    body = f"""Dear {farmer_name},

Great news! Your payment has been verified and approved.


CREDITS ADDED

Order Reference  : {order_ref}
Credits Added    : {credits} scan(s)
Total Credits    : {total_credits} scan(s)


You can now use your credits to:
- Scan your soil 


Open the Yucca Agro app to start scanning!

Thank you for trusting Yucca Agro.

Happy Farming! 
Yucca Agro Team
"""
    send_email(farmer_email, subject, body)


def email_payment_rejected(farmer_name, farmer_email, order_ref, reason):
    """
    Sent to farmer when admin rejects their payment.
    """
    subject = f" Payment Could Not Be Verified – {order_ref}"

    body = f"""Dear {farmer_name},

Unfortunately, we could not verify your payment for order {order_ref}.


REASON

{reason}


WHAT TO DO

1. Check that you sent money to the correct number
2. Make sure you entered the correct Transaction ID
3. Try submitting your order again in the app
4. Reply to this email if you need help

We are here to help you!

Yucca Agro Team
"""
    send_email(farmer_email, subject, body)