**PURPOSE**:

Be able to copy data from MSAccess file to oracle (one time or on permanent basis).
Oracle and MSAccess configuration are in config file.
Set of Access table names are in the same file.
This script can also create SQL for oracle DB (just varchar2(2000) columns for now.





**KNOWN ISSUE:**
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

