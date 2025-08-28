# AI-Powered Ticket & Workflow Automation

This project automates a support ticket lifecycle by integrating Google Sheets, AWS Lambda, and the OpenAI API. It automatically tracks new tickets, uses AI to categorize and prioritize them, updates their status, and sends email notifications.

## Features

* **Automated Ticket Ingestion**: Monitors a Google Sheets file for new ticket entries in real-time.
* **AI-Powered Analysis**: Leverages the OpenAI GPT API to automatically categorize tickets (e.g., Technical, Billing, General Inquiry) and assign a priority level (High, Medium, Low) based on the ticket's description.
* **Status Updates**: Updates the Google Sheet with the AI-generated category and priority, providing an instant overview of the ticket queue.
* **Email Notifications**: Automatically sends a detailed email notification for each new, processed ticket to a designated support address.
* **Serverless Architecture**: Built on AWS Lambda for a cost-effective, scalable, and maintenance-free backend.

## Technology Stack

* **Backend**: Python 3.12
* **Cloud Platform**: AWS Lambda
* **Database/Trigger**: Google Sheets
* **AI Service**: OpenAI API (GPT-3.5-Turbo)
* **Deployment**: Git, AWS CLI, Google Cloud SDK

## How It Works

1.  A new ticket is created by adding a row in a designated Google Sheet, leaving the `Category` and `Priority` fields blank.
2.  An AWS EventBridge trigger runs the AWS Lambda function on a fixed schedule (e.g., every 5 minutes).
3.  The Lambda function authenticates with the Google Sheets API using a Service Account.
4.  It scans the sheet for rows where the `Category` is empty, identifying them as new tickets.
5.  For each new ticket, the function sends the `Description` to the OpenAI API.
6.  OpenAI returns a suggested `Category` and `Priority`.
7.  The function updates the corresponding row in the Google Sheet with this new information.
8.  Finally, the function logs into a specified Gmail account and sends an email notification with the ticket details to a recipient address.

## Setup and Installation

1. Clone the Repository
2. Set Up a Python Virtual Environment and install requirements
3. Configure Credentials
- Create a Google Cloud project, enable the Google Sheets API, and create a Service Account.
- Create a Google Sheet and Share this sheet.
4. Deploy to AWS Lambda
5. Configure Lambda Environment Variables
6. Set Up a Trigger
- in the Lambda console, add an EventBridge (CloudWatch Events) trigger.


