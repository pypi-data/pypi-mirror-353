# SSL Email

## Table of Contents

- [Project Description](#project-description)
- [Installation](#installation)
- [Setup](#setup)
- [Usage](#usage)

## Project Description

This project allows sending STMP email over TLS using SSL. Use the Emailer class to create an instance for an outgoing email account, and call the `send` method to send an email. You can also use the EmailHandler class to add a custom email handler to your app's logger.

## Installation

`python -m pip install secure-email`

## Setup

### Keyring

The keyring library stores credentials in your machine's Windows Credential Locker. If you wish to make use of the Emailer class' use_keyring argument, make sure you have the [keyring](https://pypi.org/project/keyring/) library installed:

```
pip install keyring
```

To use keyring to fetch the password in the Emailer class, use the email address associated with the credentials as the name:

```Python
keyring.set_password(
  "username@domain.com",
  "username@domain.com",
  "supersecretpassword"
)
```

## Usage

`from secure_email import Emailer`

Files in the demo folder demonstrate how to use the two classes in this project--Emailer and EmailHandler. `send_email.py` demonstrates how to send an email from a python script, and the `flask_app` demonstrates how to add the EmailHandler to you app's logger. The Emailer and EmailHandler classes are both located in `sendmail.py` in the src folder.

### Emailer

Class for sending emails. Instantiating a class merely stores the info to create an STMP connection, while calling the send method creates the STMP connection, sends an email, and then closes the connection.

- Arguments:
  - secure_host (str): default SSL-enabled mail host
  - port (int): port number for mail host
  - email_address (str): "from" email address
  - password: (str | None): email password (default: None)
  - user: (str | None): username for server, if different than email address
  - unsecure_host: (str | None): backup non-SSL mail host
  - use_keyring (bool): whether to fetch password from keyring (default: False)
  - include_ssl_status (bool): whether to add line to body of sent emails indicating whether email was sent over SSL
    (default: False)
- Methods:
  - send
    - Sends STMP email
    - Arguments:
      - to (str|list[str]): email recipient(s)
      - subject (str): email subject line
      - body (str): body of email as text or HTML string
      - attachments (list[str]|list[iter[str]]): list of paths to files to attach to email. Can supply 2-length list or tuple of (path, encoding) to specify which encoding to use for an attachment, if other than UTF-8 (default: [])
      - ignore_attachment_errors (bool): whether to ignore errors when adding attachments. If True, attached files will send with invalid characters excluded. If False, files with any invalid characters will throw error. (default: True)
      - cc_list (list[str]): recipients to CC (default: [])
      - bcc_list (list[str]): recipients to BCC (default: [])
      - html (bool): whether to send body as HTML (default: False)
      - secure (bool): whether to send over SSL (default: True)
    - Returns:
      - response (str): either "success" or error message
- Example:

  ```Python
  # Supply password directly
  emailer = Emailer(
      "my.emailserver.com",  # host
      0,  # port
      "email@example.com",  # email_address
      password="supersecretpassword"
  )

  # Use password stored in keyring
  emailer = Emailer(
      "my.emailserver.com",  # host
      0,  # port
      "email@example.com",  # email_address
      use_keyring=True
  )

  response = emailer.send(
      "recipient@domain.org",  # to
      "Open Immediately!!!",  # subject
      "You may have won $1,000,000. Click the link below to find out",  # body
  )
  successful = response == "success"
  ```

### EmailHandler

Extends logging.handlers.SMTPHandler to use the [Emailer](#emailer) class to send emails (see the [logging library documentation](https://docs.python.org/3/library/logging.handlers.html#smtphandler) to learn more about the SMTPHandler). EmailHandler makes the following modifications to SMTPHandler:

- Modified arguments:
  - subject: (str | None): required in SMTPHandler, but optional in EmailHandler in case subject formatter is used instead; note that failing to provide a subject string or add a subject formatter will result in emails being sent with no subject

- Additional arguments:
  - send_html (bool): whether to send HTML email instead of plain text (default: False)
  - backup_host (str | None): non-SSL host to send from if SSL host fails
  - include_ssl_status (bool): whether to add line to body of sent emails indicating whether email was sent over SSL default: False)

- Additional methods:
  - setSubjectFormatter: sets formatter to use for record-based subject line
    - Params:
      - fmt (logging.Formatter)