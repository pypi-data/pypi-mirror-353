from __future__ import annotations

import logging
import mimetypes
import platform
import smtplib
import ssl
import traceback
from email.message import EmailMessage
from logging.handlers import SMTPHandler
from pathlib import Path
from typing import Optional, Union

try:
    import keyring
except ImportError:
    pass

machine = platform.node().lower()


class Emailer:
    def __init__(
        self,
        secure_host: str,
        port: int,
        email_address: str,
        password: Optional[str] = None,
        user: Optional[str] = None,
        unsecure_host: str = "",
        use_keyring: bool = False,
        include_ssl_status: bool = False,
    ) -> None:
        """
        Connect to an email server and send emails over TLS using SSL

        params
        ------
        secure_host (str): name of host server
        port (int): host server port number
        email_address (str): email account to connect as
        password (str): password for email account; can omit to use stored password
                        from keyring (default: None)
        user (str): username for email account if different than email (default: None)
        unsecure_host (str): non-SSL backup host to connect to if primary connection
                             fails (default: "")
        use_keyring (bool): whether to fetch password from keyring (default: False)
        include_ssl_status (bool): whether to append email body with text indicating
                                   whether email was sent over SSL (secure_host) or
                                   not (unsecure_host); can be useful for debugging
                                   connection settings (default: False)

        methods
        -------
        send: sends email message
        """
        self.secure_host: str = secure_host
        self.include_ssl_status: bool = include_ssl_status
        self.bu_host: str = unsecure_host
        self.port: int = port
        self.email_address: str = email_address
        self.user: str = user or email_address
        self.password: str = password or ""
        if use_keyring:
            self.password = keyring.get_password(self.email_address, self.user) or ""
            pass

    def __send(
        self,
        to: Union[str, list[str]],
        subject: str,
        body: str,
        attachments=[],
        ignore_errors: bool = True,
        cc_list: list[str] = [],
        bcc_list: list[str] = [],
        html: bool = False,
        secure: bool = True,
    ) -> str:
        status_str: str = "SSL" if secure else "non-SSL backup host"
        newline: str = "\n"
        if self.include_ssl_status:
            if html:
                body += f"<p>Email sent over {status_str}</p>"
            else:
                body += f"{newline}{newline}*** Email sent over {status_str} ***"
        to = to if isinstance(to, str) else ",".join(to)

        smtp_server = self.secure_host if secure else self.bu_host
        msg = EmailMessage()
        if html:
            msg.set_content(body, subtype="html")
        else:
            msg.set_content(body)
        msg["Subject"] = subject
        msg["From"] = self.email_address
        msg["To"] = to
        if cc_list:
            msg["CC"] = ",".join(cc_list)
        if bcc_list:
            msg["BCC"] = ",".join(bcc_list)
        errors = "ignore" if ignore_errors else None
        for item in attachments:
            if (
                hasattr(item, "__iter__")
                and len(item) == 2
                and not isinstance(item, str)
            ):
                attachment, encoding = item
            else:
                attachment = item
                encoding = "utf-8"
            filename = Path(attachment).name
            mimetype, _ = mimetypes.guess_type(attachment)
            if mimetype is None:
                continue
            maintype, subtype = mimetype.split("/")
            readmode = "r" if maintype == "text" else "rb"
            if readmode == "rb":
                encoding = None
                errors = None
            kwargs = {"filename": filename}
            if maintype != "text":
                kwargs["maintype"] = maintype
                kwargs["subtype"] = subtype
            with open(attachment, readmode, encoding=encoding, errors=errors) as f:
                content = f.read()
                msg.add_attachment(content, **kwargs)  # type: ignore
        if secure:
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
        try:
            with smtplib.SMTP(smtp_server, self.port) as server:
                if secure:
                    server.starttls(context=context)
                    server.login(self.email_address, self.password)
                server.send_message(msg)
                return "success"
        except Exception as e:
            return f"{e}: {traceback.format_exc()}"

    def send(
        self,
        to,
        subject: str,
        body: str,
        attachments=[],
        ignore_attachment_errors: bool = True,
        cc_list: list[str] = [],
        bcc_list: list[str] = [],
        html: bool = False,
    ) -> str:
        """
        Sends STMP email. Attempts to send over TLS using SSL, then tries
        non-SSL backup server, if provided.

        params
        ------
        to (str|list[str]): email recipient(s)
        subject (str): email subject line
        body (str): body of email as text or HTML string
        attachments (list[str]|list[iter[str]]): list of paths to files to attach to email. Can
                                                 supply 2-length list or tuple of (path, encoding)
                                                 to specify which encoding to use for an
                                                 attachment, if other than UTF-8 (default: [])
        ignore_attachment_errors (bool): whether to ignore errors when adding attachments. If True,
                                         attached files will send with invalid characters excluded.
                                         If False, files with any invalid characters will throw error.
                                         (default: True)
        cc_list (list[str]): recipients to CC (default: [])
        bcc_list (list[str]): recipients to BCC (default: [])
        html (bool): whether to send body as HTML (default: False)

        returns
        -------
        response (str): "success" or error message
        """
        args = [to, subject, body]
        kwargs = {
            "attachments": attachments,
            "ignore_errors": ignore_attachment_errors,
            "cc_list": cc_list,
            "bcc_list": bcc_list,
            "html": html,
        }
        response = self.__send(*args, **kwargs)
        if response != "success":
            response = self.__send(*args, **kwargs, secure=False)
        return response


class EmailHandler(SMTPHandler):
    def __init__(
        self,
        mailhost,
        fromaddr: str,
        toaddrs,
        subject=None,
        credentials=None,
        secure=None,
        timeout: float = 5.0,
        send_html: bool = False,
        backup_host: str = "",
        include_ssl_status: bool = False,
    ) -> None:
        """
        Extends logging.handlers.SMTPHandler to send emails over TLS using SSL.
        Also adds the ability to generate subject line dynamically.

        params
        ------
        mailhost (tuple(str, int)): connection to email server (host_name, port_number)
        fromaddr (str): email address to send from
        toaddrs (str|list[str]): recipient(s)
        subject (str|None): subject line; can omit if setting via formatter (default: None)
        credentials (tuple(str, str)|None): username and password; can omit to fetch from keyring
        secure (tuple|None): only included to extend SMTPHandler; will be overwritten by
                             Emailer.send() (default: None)
        timeout (float): number of seconds to wait for response from server (default: 5.0)
        send_html (bool): whether to send email as HTML (default: False)
        backup_host: (str): non-SSL backup host to connect to if primary connection
                            fails (default: "")
        include_ssl_status (bool): whether to append email body with text indicating
                                   whether email was sent over SSL (secure_host) or
                                   not (unsecure_host); can be useful for debugging
                                   connection settings (default: False)

        methods
        -------
        setSubjectFormatter: set the subject line formatter
        getSubject: use subject formatter to create subject line for record to be logged
        emit: format the record and send it to the specified addressees.
        """
        super().__init__(
            mailhost, fromaddr, toaddrs, subject, credentials, secure, timeout
        )
        self.subject_formatter = None
        self.send_html = send_html
        self.emailer = Emailer(
            (
                self.mailhost.split(":")[0]
                if isinstance(self.mailhost, str)
                else self.mailhost[0]
            ),
            self.mailport or 0,
            self.fromaddr,
            password=credentials[1] if credentials else None,
            use_keyring=False if credentials else True,
            unsecure_host=backup_host,
            include_ssl_status=include_ssl_status,
        )

    def setSubjectFormatter(self, fmt: logging.Formatter):
        """
        Set the subject line formatter

        params
        ------
        fmt (logging.Formatter): formatter to be applied to EmailLogger
                                 subject line
        """
        self.subject_formatter = fmt

    def getSubject(self, record: logging.LogRecord):
        """
        Use subject formatter to create subject line for record to be logged

        params
        ------
        record (logging.LogRecord): record to be logged
        """
        if self.subject_formatter is None:
            return self.subject
        return self.subject_formatter.format(record)

    def emit(self, record: logging.LogRecord) -> None:
        """
        Format the record and send it to the specified addressees.

        params
        ------
        record (logging.LogRecord): record to be logged
        """
        try:
            result = self.emailer.send(
                self.toaddrs,
                self.getSubject(record),
                self.format(record),
                html=self.send_html,
            )
            if result != "success":
                print(result)
        except Exception:
            self.handleError(record)
