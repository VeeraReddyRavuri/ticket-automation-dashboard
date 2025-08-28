import os
import json
import smtplib
from email.mime.text import MIMEText
from google.oauth2 import service_account
from googleapiclient.discovery import build
import openai

# --- CONFIGURATION ---
# Google Sheets
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'ticket-workflow-automation-72021b33af1c.json' 
SPREADSHEET_ID = '1DVwGHuhu1IEUukeSOBWq7A58XVRVmp4Myih7qgcUIR4'
RANGE_NAME = 'Sheet1!A:E' 

# OpenAI
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY') # Will be set in Lambda
openai.api_key = OPENAI_API_KEY

# Email Notifications
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
EMAIL_SENDER = os.environ.get('EMAIL_SENDER') # Will be set in Lambda
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD') # Will be set in Lambda
EMAIL_RECIPIENT = 'yourdoomsday1212@gmail.com'


def get_google_sheets_service():
    """Initializes and returns the Google Sheets service object."""
    creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    return service.spreadsheets()

def get_new_tickets(service):
    """Fetches new tickets from the Google Sheet that have a blank category."""
    result = service.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    all_values = result.get('values', [])

    if not all_values:
        return []

    new_tickets = []
    # UPDATED: More robust logic to find the correct row index
    for i, row in enumerate(all_values):
        # Skip the header row
        if i == 0:
            continue

        # The actual sheet row number is the list index + 1
        sheet_row_number = i + 1

        # Skip empty rows
        if not row or not any(row):
            continue

        # Check if ticket data exists and if the category (4th column) is empty
        if len(row) >= 3 and (len(row) < 4 or not row[3]): 
            ticket = {
                'row_index': sheet_row_number,
                'id': row[0],
                'subject': row[1],
                'description': row[2],
            }
            new_tickets.append(ticket)
    return new_tickets

def categorize_ticket(description):
    """Uses OpenAI to categorize and prioritize a ticket."""
    try:
        prompt_text = (f"Categorize the following ticket description into one of these categories: "
                       f"[Technical, Billing, General Inquiry]. Also, assign a priority: [High, Medium, Low].\n\n"
                       f"Description: \"{description}\"\n\n"
                       f"Category: \n"
                       f"Priority:")
 
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt_text}],
            max_tokens=20,
            temperature=0
        )
        text = response.choices[0].message.content.strip()


        lines = text.split('\n')
        category = "Uncategorized"
        priority = "Low"
        if len(lines) > 0:
            category = lines[0].replace('Category:', '').strip()
        if len(lines) > 1:
            priority = lines[1].replace('Priority:', '').strip()

        return category, priority
    except Exception as e:
        print(f"Error with OpenAI: {e}")
        return "Uncategorized", "Low"

def update_ticket_status(service, row_index, category, priority):
    """Updates the ticket status in the Google Sheet."""
    values = [[category, priority]]
    body = {'values': values}
    range_to_update = f'Sheet1!D{row_index}:E{row_index}'
    service.values().update(
        spreadsheetId=SPREADSHEET_ID, range=range_to_update,
        valueInputOption='RAW', body=body).execute()

def send_email_notification(ticket, category, priority):
    """Sends an email notification for a new ticket."""
    subject = f"New Ticket [{priority}]: {ticket['subject']}"
    body = (f"A new ticket has been created and categorized:\n\n"
            f"ID: {ticket['id']}\n"
            f"Subject: {ticket['subject']}\n"
            f"Description: {ticket['description']}\n\n"
            f"Category: {category}\n"
            f"Priority: {priority}")

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECIPIENT

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, [EMAIL_RECIPIENT], msg.as_string())
        print("Email notification sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")


def lambda_handler(event, context):
    """The main function that AWS Lambda will execute."""
    service = get_google_sheets_service()
    new_tickets = get_new_tickets(service)

    if not new_tickets:
        print("No new tickets to process.")
        return {'statusCode': 200, 'body': json.dumps('No new tickets.')}

    for ticket in new_tickets:
        category, priority = categorize_ticket(ticket['description'])
        update_ticket_status(service, ticket['row_index'], category, priority)
        send_email_notification(ticket, category, priority)
        print(f"Processed ticket ID: {ticket['id']}")

    return {
        'statusCode': 200,
        'body': json.dumps(f'Successfully processed {len(new_tickets)} tickets.')
    }
