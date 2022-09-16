import os
import numpy as np
import pandas as pd
from django.conf import settings
import random
import time
from time import sleep
from datetime import date,  datetime, timedelta
import cx_Oracle as oracle
import logging
"""
Module is used for connecting to database
Ensure following environment variables are set 
Also this module assumes you are connecting to Oracle Database 
"""
def get_connection():
    try:
        DB_SERVER = os.environ.get('DJANGO_DB_HOST')
        DB_PORT = os.environ.get('DJANGO_DB_PORT')
        DB_SID = os.environ.get('DJANGO_DB')
        DB_USERNAME = os.environ.get('DJANGO_DB_USER')
        DB_PASSWORD = os.environ.get('DJANGO_DB_PWD')
        dsn_tns = oracle.makedsn(DB_SERVER, DB_PORT, DB_SID)
        print(dsn_tns)
        connection = oracle.connect(DB_USERNAME, DB_PASSWORD, dsn_tns)
        return connection
    except Exception as ex:
        logging.error(ex)

db_connection = get_connection()

def test_connection(p_conn = db_connection):
    try:
        cur = p_conn.cursor()
        cur.execute('select 1 from dual')
        return 'OK'
    except Exception as ex:
        print(ex)
        return ('FAILED:{}'.format(ex))
"""
separate function for each table
"""
BATCH_COMMIT_SIZE = 500
BASE_URL = 'https://server2.nuepos.co.uk/api/v1/'
API_KEY  = '97f84757-054a-4784-97df-e558290ee2ee'
USE_XML = 'false'

def tp_stock_columns():
    return ['PRODUCTGUID','STOREGUID','STORENAME','PRODUCTNAME',
                        'INTERNALREFERENCECODE','QUANTITY','LASTUPDATEDDATE','INTEGRATIONVALUE']

def f_insert_tpstocks(p_rows: [] = [], p_conn=db_connection):
    start = time.time()
    print('connection:', p_conn)
    try:
        cur = p_conn.cursor()

        cur.executemany("""insert into /*+ APPEND */ 
                        TP_STOCKS(PRODUCTGUID,STOREGUID,STORENAME,PRODUCTNAME,
                        INTERNALREFERENCECODE,QUANTITY,LASTUPDATEDDATE,INTEGRATIONVALUE) 
                        values(:1,:2,:3,:4,:5,:6,:7,:8)
                        """, p_rows, batcherrors=True)
        """
        cur.executemany(MERGE INTO  TP_STOCKS target
                         USING DUAL 
                         ON (target.productguid = :1  
                             AND target.storeguid = :2 )
                         WHEN MATCHED THEN
                         UPDATE 
                            set target.quantity = :6
                                ,target.lastupdateddate = :7
                                ,target.last_update_date = sysdate
                                ,target.status = 'NEW'
                         WHERE target.productguid = :1 
                         AND   target.storeguid = :2
                         WHEN NOT MATCHED THEN
                           INSERT (PRODUCTGUID,STOREGUID,STORENAME,PRODUCTNAME,
                           INTERNALREFERENCECODE,QUANTITY,LASTUPDATEDDATE,INTEGRATIONVALUE) 
                           values(:1,:2,:3,:4,:5,:6,:7,:8)
                           , p_rows, batcherrors=True)
        """
        p_conn.commit()
    except Exception as ex:
        print('insert tp stock',ex)
    end = time.time()


def csv_to_table(p_file, p_table_func, p_schema: {} = {}, p_date: [] = [], p_header: int = 0, p_commitsize=BATCH_COMMIT_SIZE):
    data_df = pd.read_csv(p_file, header=p_header, parse_dates=p_date, dtype=p_schema)
    data_df.columns = [c.upper() for c in data_df.columns]
    print(data_df.info(memory_usage=True))
    data_rows, data_cols = data_df.shape
    print('Number of rows', data_rows)
    print('Number of columns', data_cols)
    for from_row in range(0, data_rows, p_commitsize):
        to_row = (from_row + p_commitsize - 1)
        print(from_row, to_row)
        data_list = list(data_df.iloc[from_row:to_row, ].itertuples(index=False, name=None))
        print('datalist',data_list)
        p_table_func(data_list)


def http_to_table(p_endpoint, p_table_func, p_lastupdatedate=None, p_commitsize=BATCH_COMMIT_SIZE, p_date: [] = []):
    pagenumber = 0
    if p_lastupdatedate is None:
        lastupdatedate = (datetime.utcnow() - timedelta(minutes=15)).strftime('%Y-%m-%dT%H:%M:%S')
    else:
        lastupdatedate = p_lastupdatedate
    while True:
        data_df = pd.DataFrame()
        pagenumber += 1
        endpoint_url = "{}{}/?APIKey={}&UseXML={}&pageNumber={}&limit={}&LastUpdatedDate={}".format(
                            BASE_URL,
                            p_endpoint,
                            API_KEY,
                            USE_XML,
                            pagenumber,
                            BATCH_COMMIT_SIZE,
                            lastupdatedate)
        print(endpoint_url)
        data_df = pd.read_json(endpoint_url)
        if data_df.empty:
            print('exiting loop')
            break
        data_df.columns = [c.upper() for c in data_df.columns]
        if 'LASTUPDATEDDATE' in data_df.columns:
            data_df['LASTUPDATEDDATE'] = pd.to_datetime(data_df['LASTUPDATEDDATE'],infer_datetime_format=True)
        print(data_df.info(memory_usage=True))
        data_rows, data_cols = data_df.shape
        print('Number of rows', data_rows)
        print('Number of columns', data_cols)
        for from_row in range(0, data_rows, p_commitsize):
            to_row = (from_row + p_commitsize - 1)
            print(from_row, to_row)
            data_list = list(data_df.iloc[from_row:to_row, ].itertuples(index=False, name=None))
            p_table_func(data_list)



def load_data(p_lastupdatedate = None):
    http_to_table('products',f_insert_tpstocks,p_date=['LASTUPDATEDDATE'], p_lastupdatedate = p_lastupdatedate)

def schedule_load_data(p_interval:int = 15*60):
    while True:
        load_data()
        sleep(p_interval)
