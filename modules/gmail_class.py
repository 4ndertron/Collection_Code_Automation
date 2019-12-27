import pickle
import os
import base64
import mimetypes
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from apiclient import errors


class Gmail:
    def __init__(self):
        self.project_path = os.path.join(os.environ['userprofile'], 'PycharmProjects', 'Collection Code Automation')
        self.SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
        self.creds = None
        self.user_id = os.environ['gmail_id']
        self.pickle_path = os.path.join(self.project_path, 'creds', 'token.pickle')
        self.creds_path = os.path.join(self.project_path, 'creds', 'credentials.json')
        self._set_service()

    def _set_service(self):
        if os.path.exists(self.pickle_path):
            with open(self.pickle_path, 'rb') as token:
                self.creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.creds_path, self.SCOPES)
                self.creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(self.pickle_path, 'wb') as token:
                pickle.dump(self.creds, token)

        self.service = build('gmail', 'v1', credentials=self.creds)

    def test_dirs(self):
        print(self.creds_path + ' exists = ' + str(os.path.isfile(self.creds_path)))
        print(self.pickle_path + ' exists = ' + str(os.path.isfile(self.pickle_path)))

    def _create_message(self, sender, to, subject, message_text):
        message = MIMEText(message_text)
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject
        # previous line:
        # return {'raw': base64.urlsafe_b64encode(message.as_string())}
        # caused error:
        # TypeError: a bytes-like object is required, not 'str'
        # Solution url:
        # https://stackoverflow.com/questions/43352496/gmail-api-error-from-code-sample-a-bytes-like-object-is-required-not-str
        return {'raw': base64.urlsafe_b64encode(message.as_string().encode()).decode()}

    def _create_message_with_attachment(self, sender, to, subject, message_text, file):
        message = MIMEMultipart()
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject

        msg = MIMEText(message_text)
        message.attach(msg)

        content_type, encoding = mimetypes.guess_type(file)

        if content_type is None or encoding is not None:
            content_type = 'application/octet-stream'
        main_type, sub_type = content_type.split('/', 1)
        if main_type == 'text':
            fp = open(file, 'rb')
            msg = MIMEText(fp.read(), _subtype=sub_type)
            fp.close()
        elif main_type == 'image':
            fp = open(file, 'rb')
            msg = MIMEImage(fp.read(), _subtype=sub_type)
            fp.close()
        elif main_type == 'audio':
            fp = open(file, 'rb')
            msg = MIMEAudio(fp.read(), _subtype=sub_type)
            fp.close()
        else:
            fp = open(file, 'rb')
            msg = MIMEBase(main_type, sub_type)
            msg.set_payload(fp.read())
            fp.close()
        filename = os.path.basename(file)
        msg.add_header('Content-Disposition', 'attachment', filename=filename)
        message.attach(msg)

        return {'raw': base64.urlsafe_b64encode(message.as_string().encode()).decode()}

    def test_draft_creation(self, user_id, message_body):
        try:
            message = message_body
            draft = self.service.users().drafts().create(userId=user_id, body=message).execute()

            print('Draft id: %s\nDraft message: %s' % (draft['id'], draft['message']))

            return draft
        except errors.HttpError as error:
            print(f'An error occurred: {error}')
            return None

    def test_email_send(self, user_id, message):
        try:
            message = (self.service.users().messages().send(userId=user_id, body=message).execute())
            print(f'Message Id: {message["id"]}')
            return message
        except errors.HttpError as error:
            print(f'An error occurred: {error}')

    def send_email(self, to, subject, email_body, file=None):
        try:
            if file is None:
                new_message = self._create_message(sender=self.user_id,
                                                   to=to,
                                                   subject=subject,
                                                   message_text=email_body)
            else:
                new_message = self._create_message_with_attachment(sender=self.user_id,
                                                                   to=to,
                                                                   subject=subject,
                                                                   message_text=email_body,
                                                                   file=file)
            self.test_email_send(self.user_id, message=new_message)
        except errors.HttpError as error:
            print(f'Error received:\n{error}')
