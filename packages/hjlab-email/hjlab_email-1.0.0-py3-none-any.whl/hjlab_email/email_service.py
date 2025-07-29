import os
import asyncio
import aiosmtplib
import logging
import re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

logger = logging.getLogger(__name__)  # Create a logger instance for the current module


def is_valid_email(email: str) -> bool:
    """
    Checks if the given string is a valid email address format.
    Args:
        email (str): The email address string to validate.
    Returns:
        bool: True if valid, False otherwise.
    """
    # Simple email validation regex (does not fully comply with RFC 5322, but usable for general cases)
    return re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email) is not None


class EmailService:
    """
    A class to manage email sending.
    Encapsulates SMTP server settings and sending functionality.
    """

    def __init__(self, server: str, port: int, email: str, password: str):
        """
        Initializes the EmailService.
        Directly accepts SMTP server, port, sender email address, and password as arguments.

        Args:
            server (str): SMTP server address (e.g., 'smtp.naver.com').
            port (int): SMTP server port (e.g., 587).
            email (str): Sender's email address.
            password (str): Sender's email password.
        """
        self.smtp_server: str = server
        self.smtp_port: int = port
        self.sender_email: str = email
        self.sender_password: str = password
        self._smtp_client: aiosmtplib.SMTP | None = None
        self._connection_lock = asyncio.Lock()
        logger.debug(
            f"EmailService initialized: {self.sender_email} ({self.smtp_server}:{self.smtp_port})"
        )

    async def __aenter__(self):
        """Called when entering the asynchronous context manager."""
        logger.debug("EmailService async context entered.")
        # The _connect_and_login call happens inside send_email when needed,
        # so no explicit connection attempt is required here.
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Called when exiting the asynchronous context manager."""
        logger.debug("EmailService async context exited. Closing connection if open.")
        await self.close_connection()
        if exc_val:  # If an exception occurred
            logger.error(f"EmailService context exited with an exception: {exc_val}")
            # Return False to re-raise the exception. Returning True suppresses the exception.
            return False
        return True  # Return True if no exception occurred

    async def _connect_and_login(self) -> tuple[aiosmtplib.SMTP | None, str]:
        """
        Connects to the SMTP server and logs in.
        If already connected, reuses the existing connection without reconnecting.
        Uses asyncio.Lock to prevent multiple tasks from attempting simultaneous connections.

        Returns:
            tuple[aiosmtplib.SMTP | None, str]: The connected SMTP client object and a message.
                                                   Returns None and an error message on connection failure.
        """
        async with self._connection_lock:
            if self._smtp_client and self._smtp_client.is_connected:
                logger.debug("Already connected to SMTP server. Reusing existing connection.")
                return self._smtp_client, "Already connected to SMTP server."

            try:
                logger.info(f"Attempting to connect to SMTP server: {self.smtp_server}:{self.smtp_port}")
                self._smtp_client = aiosmtplib.SMTP(
                    hostname=self.smtp_server,
                    port=self.smtp_port,
                    start_tls=True,  # Port 587 uses STARTTLS.
                    timeout=10,
                )
                await self._smtp_client.connect()
                logger.info("Successfully connected to SMTP server. Attempting to log in...")
                await self._smtp_client.login(self.sender_email, self.sender_password)
                logger.info("SMTP login successful.")
                return self._smtp_client, "SMTP connection and login successful."
            except aiosmtplib.SMTPAuthenticationError as e:
                self._smtp_client = None  # Reset client on connection failure
                auth_error_msg = f"SMTP authentication error: {e}. Please check your Naver SMTP settings and credentials."
                logger.error(auth_error_msg)
                return None, auth_error_msg
            except aiosmtplib.SMTPException as e:
                self._smtp_client = None  # Reset client on connection failure
                smtp_error_msg = f"SMTP error: {e}"
                logger.error(smtp_error_msg)
                return None, smtp_error_msg
            except Exception as e:
                self._smtp_client = None  # Reset client on connection failure
                unexpected_error_msg = f"An unexpected error occurred: {e}"
                logger.exception(unexpected_error_msg)
                return None, unexpected_error_msg

    async def send_email(
            self,
            recipients: str | list[str],
            subject: str,
            body_text: str | None = None,
            body_html: str | None = None,
            cc_recipients: str | list[str] | None = None,
            bcc_recipients: str | list[str] | None = None,
            attachments: list[dict[str, str]] | None = None,
            max_retries: int = 1,
            retry_delay_seconds: int = 5,
    ) -> tuple[bool, str]:
        """
        Asynchronously sends an email.

        This method sends an email with a text or HTML body and attachments
        to the specified recipients. It retries the sending process up to a
        specified number of times if it fails. It also performs basic validation
        of email addresses.

        NOTE: The current design of the `send_email` method handles most foreseeable
         failure scenarios internally and returns a clean (success status, message)
         tuple to the caller. Therefore, wrapping `send_email` calls in try/except
         blocks is generally not necessary. Checking the returned boolean value is sufficient.

        Args:
            recipients (str | list[str]): Email recipient address(es) (single string or list).
            subject (str): Email subject.
            body_text (str | None): Plain text email body. If used with body_html, body_html takes precedence.
            body_html (str | None): HTML formatted email body.
            cc_recipients (str | list[str] | None): Carbon Copy (CC) recipient address(es) (single string or list).
            bcc_recipients (str | list[str] | None): Blind Carbon Copy (BCC) recipient address(es) (single string or list).
                                                     BCC recipients do not appear in the 'To' or 'Cc' fields.
            attachments (list[dict[str, str]] | None): List of attachments. Each item is a dictionary
                                                      of the form {"path": "file_path", "filename": "filename_to_attach"}.
                                                      If 'filename' is not provided, the filename from 'path' will be used.
            max_retries (int): Maximum number of retries if email sending fails. Default is 1.
            retry_delay_seconds (int): Delay in seconds between retries. Default is 5 seconds.

        Returns:
            tuple[bool, str]:
                - First element (bool): True if email sent successfully, False otherwise.
                - Second element (str): Message regarding the sending result (success or reason for failure).

        Raises:
            FileNotFoundError: May occur if an attachment file path is invalid.
            Exception: May occur during file reading or other unexpected errors.
        """
        if not all([self.smtp_server, self.sender_email, self.sender_password]):
            logger.error(
                "SMTP server, sender email, or password is not set."
            )
            return (
                False,
                "SMTP server, sender email, or password is not set.",
            )

        _recipients = [recipients] if isinstance(recipients, str) else recipients
        _cc_recipients = (
            [cc_recipients] if isinstance(cc_recipients, str) else cc_recipients
        )
        _bcc_recipients = (
            [bcc_recipients] if isinstance(bcc_recipients, str) else bcc_recipients
        )

        if not _recipients:
            logger.warning(
                "No recipient email address specified. Cannot send email."
            )
            return False, "No recipient email address specified."

        # Email validity check
        all_addressees = _recipients + (_cc_recipients or []) + (_bcc_recipients or [])
        for addr in all_addressees:
            if not is_valid_email(addr):
                logger.error(f"Invalid email address format: '{addr}'. Email sending aborted.")
                return False, f"Invalid email address format: '{addr}'."

        msg = MIMEMultipart()
        msg["Subject"] = subject
        msg["From"] = self.sender_email
        msg["To"] = ", ".join(_recipients)

        if _cc_recipients:
            msg["Cc"] = ", ".join(_cc_recipients)

        # Body processing
        if body_html:
            content_part = MIMEText(body_html, "html")
            msg.attach(content_part)
            logger.debug("HTML body added.")
        elif body_text:
            content_part = MIMEText(body_text, "plain")
            msg.attach(content_part)
            logger.debug("Plain text body added.")
        else:
            content_part = MIMEText("", "plain")
            msg.attach(content_part)
            logger.debug("No body content, adding empty body.")

        if attachments:
            for attachment_info in attachments:
                attachment_path: str | None = attachment_info.get("path")
                attachment_filename: str | None = attachment_info.get("filename")
                if not attachment_path:
                    logger.error("Attachment information is missing 'path'.")
                    return False, "Attachment information is missing 'path'."

                try:
                    with open(attachment_path, "rb") as f:
                        attachment_part = MIMEApplication(f.read())
                        filename_to_use = (
                            attachment_filename
                            if attachment_filename
                            else os.path.basename(attachment_path)
                        )
                        attachment_part.add_header(
                            "Content-Disposition",
                            "attachment",
                            filename=filename_to_use,
                        )
                        msg.attach(attachment_part)
                        logger.debug(
                            f"Attachment '{filename_to_use}' ({attachment_path}) added."
                        )
                except FileNotFoundError:
                    logger.error(
                        f"Attachment file '{attachment_path}' not found."
                    )
                    return False, f"Attachment file {attachment_path} not found."
                except Exception as e:
                    logger.exception(
                        f"An error occurred while attaching file '{attachment_path}': {e}"
                    )
                    return (
                        False,
                        f"An error occurred while attaching file {attachment_path}: {e}",
                    )

        logger.info(f"Starting email sending attempt (Recipients: {_recipients}, Subject: {subject})")
        # Retry loop
        for attempt in range(max_retries + 1):
            success, message = False, "Email sending failed."
            try:
                smtp_client_instance, connect_message = await self._connect_and_login()
                if smtp_client_instance is None:
                    message = f"SMTP connection or login failed: {connect_message}"
                    if attempt < max_retries:
                        logger.warning(
                            f"Email sending failed (Attempt {attempt + 1}/{max_retries + 1}, Subject: {subject}): {message}. Retrying in {retry_delay_seconds} seconds..."
                        )
                        await asyncio.sleep(retry_delay_seconds)
                        self._smtp_client = (
                            None  # Reset client on connection failure to force re-connection
                        )
                        continue
                    else:
                        logger.error(f"Email sending final failure (Subject: {subject}): {message}")
                        return False, message

                all_recipients_for_smtp = _recipients[:]
                if _cc_recipients:
                    all_recipients_for_smtp.extend(_cc_recipients)
                if _bcc_recipients:
                    all_recipients_for_smtp.extend(_bcc_recipients)

                await smtp_client_instance.send_message(
                    msg, sender=self.sender_email, recipients=all_recipients_for_smtp
                )
                success, message = True, "Email sent successfully!"
                logger.info(f"Email sent successfully (Recipients: {_recipients}, Subject: {subject}).")
                return success, message

            except aiosmtplib.SMTPException as e:
                message = f"SMTP sending error: {e}"
                logger.error(f"SMTP sending error occurred (Subject: {subject}): {e}")
                self._smtp_client = None  # Explicitly reset client
            except Exception as e:
                message = f"An unexpected error occurred: {e}"
                logger.exception(f"An unexpected error occurred during email sending (Subject: {subject}): {e}")
                self._smtp_client = None  # Explicitly reset client

            if attempt < max_retries:
                logger.warning(
                    f"Email sending failed (Attempt {attempt + 1}/{max_retries + 1}, Subject: {subject}): {message}. Retrying in {retry_delay_seconds} seconds..."
                )
                await asyncio.sleep(retry_delay_seconds)
            else:
                logger.error(f"Email sending final failure (Subject: {subject}): {message}")

        return success, message

    async def close_connection(self):
        """
        Closes the SMTP connection if it is active.
        """
        if self._smtp_client and self._smtp_client.is_connected:
            await self._smtp_client.quit()
            self._smtp_client = None
            logger.info("SMTP connection closed.")
        else:
            logger.debug("No active SMTP connection to close.")