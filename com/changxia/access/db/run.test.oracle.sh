export PATH=$PATH:/opt/oracle/instantclient/bin
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/oracle/instantclient:/opt/oracle/instantclient/lib
export ORACLE_HOME=/opt/oracle/instantclient/network/admin
export TNS_ADMIN=${ORACLE_HOME}/network/admin
python  OracleHelper.py
