from __future__ import print_function
import pyodbc
from pprint import pprint
import re
import cx_Oracle
import logging
import os
from datetime import datetime
import config
import argparse
#################################################################################################################################
#List of names of Access tables to process from file
table_list = config.table_list

#################################################################################################################################
def logger_setup(logdir):

   logger = logging.getLogger(__name__)
   logger.setLevel(logging.DEBUG)

   debuglog = logging.FileHandler(os.path.join(logdir, datetime.now().strftime('%Y-%m-%d.log')))

   debuglog.setLevel(logging.DEBUG)
   debuglog.setFormatter(
       logging.Formatter("%(asctime)s : %(levelname)-8s : %(message)s", "%Y-%m-%dT%H:%M:%S"))
#        logging.Formatter("%(asctime)s : %(levelname)-8s : %(prefix)-22s : %(message)s", "%Y-%m-%dT%H:%M:%S"))
   logger.addHandler(debuglog)

   console = logging.StreamHandler()
   console.setLevel(logging.DEBUG)
   console.setFormatter(
       logging.Formatter("%(asctime)s : %(levelname)-8s : %(message)s", "%Y-%m-%dT%H:%M:%S"))
#        logging.Formatter("%(asctime)s : %(levelname)-8s : %(prefix)-22s : %(message)s", "%Y-%m-%dT%H:%M:%S"))
   logger.addHandler(console)

   return logger
#################################################################################################################################
def generate_sql(table_name, table_column_dict, LOG):
    LOG.info ("Generating SQL for table %s" % (table_name))
    ret_sql = 'insert into %s (' % (table_name)
    ret_sql_footer = 'values('
    fields_list = table_column_dict.get(table_name)
    cnt = 1
    for column_name in fields_list:
        if cnt > 1:
            ret_sql_footer += ','
            ret_sql += ','
        ret_sql_footer += ':' + str(cnt)
        ret_sql += column_name
        cnt+=1
    ret_sql += ') '
    ret_sql_footer += ')'
    ret_sql = ret_sql + ret_sql_footer
    LOG.debug( "SQL: %s" % (ret_sql))
    return ret_sql
#################################################################################################################################
def push2Ora(conn, mapping, table_column_dict, LOG):
    ora_connection = cx_Oracle.connect(config.oracle['username'], config.oracle['password'], config.oracle['url'], encoding="UTF-8")
    cursor = conn.cursor()
    for access_table_name in table_list:
        access_sql = ' select * from "%s"' %(access_table_name)
        LOG.debug ('MS Access SQL is : %s' %(access_sql) )
        rows = []
        for access_row in cursor.execute ( access_sql):
            rows.append(access_row)
        ora_cursor = ora_connection.cursor()
        LOG.debug("Truncating table %s" % (mapping[access_table_name]))
        truncate_sql =  'truncate table %s' % (mapping[access_table_name])
        ora_cursor.execute(truncate_sql)
        # let's generate insert statement  in order to bulk insert later
        # we want to generate sql for bulk insert
        sql = generate_sql(mapping[access_table_name], table_column_dict, LOG)
        ora_cursor.prepare(sql)
        LOG.info ("We will insert %d records to table %s" % (len(rows), mapping[access_table_name]))
        ora_cursor.executemany(None, rows)
        ora_connection.commit()
        LOG.debug("Commiting changes to DB")

    cursor.close()
    ora_connection.close()

#################################################################################################################################
def generateTables(conn, mapping, table_column_dict, LOG):
# generating: SQL for table creation, mapping between old and new tble names and dictionary with new table name and columns 
# we will match datatypes in next version of this script as for now let's just user Varchar2(2000)
    cursor = conn.cursor()
    table_sql = ''
    for access_table_name in table_list:
        LOG.debug("Working with table %s for mapping and columns info" % (access_table_name))
        new_table_name = re.sub('[^0-9a-zA-Z]+', '_', access_table_name)
        mapping [access_table_name] = new_table_name
        table_sql += 'create table ' + new_table_name + '\n('
        LOG.debug ('Table Mapping %s => %s' % (access_table_name, new_table_name))
        column_count = 0
        column_names = []
        for column in cursor.columns(table=access_table_name):
            new_column_name = re.sub('[^0-9a-zA-Z]+', '_', column.column_name)
            if new_column_name[-1] == '_':
                new_column_name = new_column_name[0:-1].strip()
            LOG.debug ('MAP table [%s] - %s [%s] => %s'%(access_table_name, column.column_name, column.type_name, new_column_name))
            column_names.append(new_column_name)
            if column_count >0:
                table_sql += ',\n\t'
            table_sql += '\t' + new_column_name + ' varchar2(2000)' 
            column_count += 1
        table_sql += ');\n\n'        
        table_column_dict [new_table_name] = column_names
    cursor.close()   
    LOG.debug ("Table creation scripts, writing to file")    
    f = open ('./sqls/create_tables.sql', 'w+')
    f.write(table_sql)
    f.close()
#################################################################################################################################
def main():
    parser = argparse.ArgumentParser ("Access DB to Oracle migrator")
    parser.add_argument("--sql_only", help='Mode, sql is for generation sqls only and data is for inserting data into oracle', action="store_true")
    args = parser.parse_args()

    LOG = logger_setup("logs")  
    MDB = config.access['file_location']
    conn = pyodbc.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=%s;uid=%s;pwd=%s' % (MDB, config.access['username'], config.access['password']))
    # set connection encoding since in other case it will fail to get field name
    conn.setencoding('utf-8')
    #cursor = conn.cursor()
    # this is mapping between "Access table name" and "Oracle table name"
    mapping = {}
    # dict for oracle table -> columns 
    # each new oracle table will have set of fields as list
    table_column_dict = {}
    generateTables(conn, mapping, table_column_dict, LOG)
    if not args.sql_only:
        push2Ora(conn, mapping, table_column_dict, LOG)
    conn.close()

#################################################################################################################################~
if __name__ == '__main__':
    main()
