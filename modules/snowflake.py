from . import *
import snowflake.connector
import os
import json


class SnowflakeHandler:
    """
    This class is setup to do the following tasks:
        1) Create an excel workbook populated by two SQL queries.
        2) Run a headless chromedriver to upload the excel workbook to ShareFile.

    Prerequisites:
        1) You need to create a JSON formatted Environment Variable, named "SNOWFLAKE_KEY", with the following keys.
            1) USERNAME
            2) PASSWORD
            3) ACCOUNT
            4) WAREHOUSE
            5) DATABASE
        Please see Snowflake documentation for the definitions of the required fields.
    """
    new_account_sql_file = 'C:\\Users\\robert.anderson\\PycharmProjects\\' \
                           'UrgentFeedback\\SQL\\Filings\\FilingsNewAccountsList.sql'
    transfer_accounts_sql_file = 'C:\\Users\\robert.anderson\\PycharmProjects\\' \
                                 'UrgentFeedback\\SQL\\Filings\\SepTransferCases.sql'

    dl_dir = os.path.join(os.environ['userprofile'], 'Downloads')

    def __init__(self, console_output=False):
        self.console_output = console_output
        self.user = ''
        self.password = ''
        self.account = ''
        self.warehouse = ''
        self.database = ''
        self.temp_query = ''
        self.con = None
        self.cur = None
        self._set_credentials()
        # self._set_connection()
        # self._set_cursor()

    def _set_credentials(self):
        if self.console_output:
            p.pprint('Collecting Snowflake credentials form system environment...')
        snowflake_json = json.loads(os.environ['SNOWFLAKE_KEY'])
        self.user = snowflake_json['USERNAME']
        self.password = snowflake_json['PASSWORD']
        self.account = snowflake_json['ACCOUNT']
        self.warehouse = snowflake_json['WAREHOUSE']
        self.database = snowflake_json['DATABASE']
        if self.console_output:
            print('credentials have been collected and assigned')

    def set_con_and_cur(self):
        self.con = snowflake.connector.connect(
            user=self.user,
            password=self.password,
            account=self.account,
            warehouse=self.warehouse,
            database=self.database
        )
        self.cur = self.con.cursor()

    def close_con_and_cur(self):
        self.cur.close()
        self.con.close()
        self.cur = False
        self.con = False

    def run_query_file(self, file_path):
        """
        :param file_path: the path to the sql file that needs to be executed
        :return: A list of tuples containing the query result data.
        """
        if self.cur is not None:
            query_string = open(file_path, 'r').read()
            results = self.cur.execute(query_string)
            col_names = [x[0] for x in self.cur.description]
            extract = results.fetchall()
            return {'columns': col_names, 'results': extract}
        else:
            return 'self.cur evaluated to None'

    def run_query_string(self, query_string):
        """
        :param query_string: a string of sql
        :return: A list of tuples containing the query result data.
        """
        if self.cur is not None:
            results = self.cur.execute(query_string)
            data = results.fetchall()
            return data
        else:
            return 'self.cur evaluated to None'
