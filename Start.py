#! python
import os
import csv
from modules.gmail_class import Gmail
from modules.snowflake import SnowflakeHandler
import datetime as dt


def main():
    file_name = 'account_collection_codes_'
    file_date = dt.date.today().strftime('%m.%d.%Y')
    file_format = '.csv'
    mail_to = ['robert.anderson@vivintsolar.com',
               # 'ryan.schield@vivintsolar.com',
               'tyler.anderson1@vivintsolar.com',
               'Sera.Goodnight@genpact.com',
               'Elijah.Rhoads@genpact.com'
               ]
    mail_subject = 'Collection Code Changes, ' + file_date
    mail_body = 'Hello,\n\nAttached is a list of accounts that need to have their collection codes changed.'
    mail = Gmail()
    sf = SnowflakeHandler(console_output=True)
    sf.set_con_and_cur()
    attachment_data = sf.run_query_file(os.path.join(mail.project_path, 'sql', 'day_query.sql'))
    attachment_file = os.path.join(mail.project_path, 'code_change_results', file_name + file_date + file_format)
    with open(attachment_file, 'w', newline='') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(attachment_data['columns'])
        csv_writer.writerows(attachment_data['results'])
    sf.close_con_and_cur()
    mail.test_dirs()
    mail.send_email(to=','.join(mail_to),
                    subject=mail_subject,
                    email_body=mail_body,
                    file=attachment_file)


if __name__ == '__main__':
    main()
