

KNOWN ISSUE:
On windows we have some error, just rerun it
We will fix if later

2019-08-13T22:05:18 : DEBUG    : MAP table [Parameters Extra] - Programs Read [VARCHAR] => Programs_Read
Traceback (most recent call last):
  File "access2ora.py", line 137, in <module>
    main()
  File "access2ora.py", line 130, in main
    generateTables(conn, mapping, table_column_dict, LOG)
  File "access2ora.py", line 96, in generateTables
    for column in cursor.columns(table=access_table_name):
UnicodeDecodeError: 'utf-16-le' codec can't decode bytes in position 80-81: illegal encoding

