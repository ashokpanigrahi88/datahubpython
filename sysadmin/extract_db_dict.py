import os
from django.db import (connection, connections)
from django.conf import settings
from sysadmin import intf_config
from common import (commonutil,sysutil,dbfuncs)
from common.models import CmnUsers
import numpy as np
import pandas  as pd
import csv

DEFAULT_PARAMS = {
    'UPDATES_DIR' :  os.path.join(settings.ADMIN_SCRIPTS_DIR,'updates\\'),
    'UPGRADE_DIR'  : os.path.join(settings.ADMIN_SCRIPTS_DIR,'upgrade\\'),
    'ACTIVE_DIR'  : os.path.join(settings.ADMIN_SCRIPTS_DIR,'upgrade\\'),
    'TABLE_COLUMNS_FILE' : 'table_columns.csv',
    'VIEW_COLUMNS_FILE' : 'view_columns.csv',
    'SEQUENCES_FILE' : 'sequences.csv',
    'INDEXES_FILE' : 'indexes.csv',
    'CONSTRAINTS_FILE' : 'constraints.csv',
    'TRIGGERS_FILE' : 'triggers.csv',
    'ALLOBJECTS_FILE' : 'allobjects.csv',
    'ALLSOURCES_FILE' : 'allsources.csv',
    'VIEWS_FILE' : 'views.csv',
    #extract database columns
    #currently query is specific to oracle database
    'API_EXTRACT_DATA' : [('api_modules_v','cmn_modules.txt'),
                ('api_menus_v','cmn_menus.txt'),
                ('api_functions_v','cmn_functions.txt'),
                ('api_parameters_v','cmn_params.txt'),
                ('api_reports_v','cmn_reports.txt'),
                ('api_repparams_v','cmn_repparams.txt'),
                ('api_lookuptypes_v','cmn_lookuptypes.txt'),
                ('api_lookupcodes_v','cmn_lookupcodes.txt'),
                ('api_profiles_v','cmn_Profiles.txt'),
                ('api_privileges_v','cmn_Privileges.txt'),
                ('api_responsibility_v','cmn_resp.txt'),
                ('api_userresp_v','cmn_userresp.txt'),
                ('api_menuresp_v','cmn_menuresp.txt'),
                ('api_navigations_v','cmn_navigations.txt'),
                ('api_syscontrols_v','sys_controls.txt'),
                ('api_sysprograms_v','sys_dfltprogs.txt'),
                ('api_mailmerge_v','cmn_mailmerge.txt'),
                ('api_jobs_v','sys_jobs.txt'),
                ('api_attachments_v','sys_attachments.txt'),
                ('api_notifevents_v','sys_notifevents.txt')],
    'EXTRACT_SETUP_DATA': [('cmn_modules_v', 'cmn_modules.csv'),
                         ('cmn_menus_v', 'cmn_menus.csv'),
                         ('cmn_functions_v', 'cmn_functions.csv'),
                         ('cmn_parameters_v', 'cmn_params.csv'),
                         ('cmn_reports_v', 'cmn_reports.csv'),
                         ('cmn_report_parameters_v', 'cmn_repparams.csv'),
                         ('cmn_lookup_types_v', 'cmn_lookuptypes.csv'),
                         ('cmn_lookup_codes_v', 'cmn_lookupcodes.csv'),
                         ('cmn_profiles_v', 'cmn_Profiles.csv'),
                         ('cmn_privileges_v', 'cmn_Privileges.csv'),
                         ('cmn_responsibilities_v', 'cmn_resp.csv'),
                         ('cmn_user_responsibilities_v', 'cmn_userresp.csv'),
                         ('cmn_menu_responsibilities_v', 'cmn_menuresp.csv'),
                         ('cmn_navigations_v', 'cmn_navigations.csv'),
                         ('sys_controls_v', 'sys_controls.csv'),
                         ('sys_programs_v', 'sys_dfltprogs.csv'),
                         ('cmn_mailmerge_v', 'cmn_mailmerge.csv'),
                         ('sys_jobs_v', 'sys_jobs.csv'),
                         ('sys_attachments_v', 'sys_attachments.csv'),
                         ('sys_notification_events_v', 'sys_notifevents.csv')]
}

def get_param_value(p_key):
    try:
        return DEFAULT_PARAMS[p_key]
    except:
        return ""

def set_active_directory(p_key:str = 'UPDATES_DIR'):
        DEFAULT_PARAMS['ACTIVE_DIR'] = DEFAULT_PARAMS[p_key]


def get_active_directory(p_key: str = 'ACTIVE_DIR'):
    return DEFAULT_PARAMS['ACTIVE_DIR']

def set_file_path(p_filename,p_directory = None):
    if commonutil.hasstrvalue(p_directory):
        return "{}{}".format(get_param_value(p_directory),p_filename)
    else:
        return "{}{}".format(get_active_directory(),p_filename)

def read_file(p_filename:str):
    filename = set_file_path(p_filename)
    filedata = ""
    with open(filename) as file:
        filedata = file.read()
    return filedata

def read_meta_data( p_index_col, p_filename):
    filename = set_file_path(p_filename)
    data = pd.read_csv(filename,index_col=p_index_col)
    print(data)
    return data

def extract_meta_data(p_sql, p_index_col, p_filename, p_file):
    data = pd.read_sql(p_sql,connection,index_col=p_index_col)
    filename = set_file_path(p_filename)
    print(filename)
    if p_file:
        data = data.astype(str)
        data.to_csv(filename)
    return data


def extract_setup_data(p_view, p_filename, p_file):
    p_sql  = "Select * from {}".format(p_view)
    data = pd.read_sql(p_sql,connection)
    data = data.fillna('None').astype(str)
    filename = set_file_path(p_filename)
    print(filename)
    if p_file:
        np.savetxt(filename,data.values, fmt='%s')
    return data

def extract_table_data(p_view, p_filename, p_file):
    p_sql  = "Select * from {}".format(p_view)
    data = pd.read_sql(p_sql,connection)
    data = data.astype(str).fillna('')
    filename = set_file_path(p_filename)
    print(filename)
    if p_file:
        data.to_csv(filename)
    return data

def extract_columns(p_tabtype:str ='TABLE',
                    p_table:str ="",
                    p_filename:str = get_param_value('TABLE_COLUMNS_FILE'),
                    p_file:bool = True):
    sql = """select tname object_name,  cname column_name, coltype data_type,
            nvl(To_Char(Decode(coltype,'NUMBER',Precision,width)),'10') data_width,
            nvl(To_Char(Decode(coltype,'NUMBER',Scale,Precision)),'0') data_precision,
            defaultval , decode(nulls,'NULL','True','False') nullable , user datasource
          from col
          Where tName in (Select tname From tab Where tabType = '{}'
                              And tName Not Like 'SNAP$%'
                              And tName Not Like 'MLOG$_%'
                              And tName Not Like 'MVW_%'
                              and tname not like 'BIN$%')
            order by tname,colno
            """.format(p_tabtype)
    return extract_meta_data(sql,'OBJECT_NAME',p_filename,p_file)

def extract_constraints(p_table:str ="",
                        p_filename:str = get_param_value('CONSTRAINTS_FILE'),
                        p_file:bool =True):
    sql = """ select c.CONSTRAINT_NAME, Decode(c.CONSTRAINT_TYPE,'P','PRIMARY KEY','R','FOREIGN KEY','C','CHECK'
                             ,'U','UNIQUE') CONSTRAINT_TYPE,c.TABLE_NAME,
                      c.SEARCH_CONDITION,Nvl(c.R_CONSTRAINT_NAME,'NOVALUE') ref_pk
                      ,Nvl(c.DELETE_RULE,'NO ACTION') Delete_Rule,
                              Decode(c.Constraint_Type,'P',1,'R',3,'C',4,'U',2) COrderby ,
                            cons_col.cons_cols, rcons_col.table_name ref_table ,
                            rcons_col.cons_cols ref_columns, user datasource
               From   User_Constraints c,
                ( select c1.constraint_name, replace(min(Decode(c1.Position,1,c1.column_name,null))||'~'||
                      min(Decode(c1.Position,2,c1.column_name,null))||'~'||
                      min(Decode(c1.Position,3,c1.column_name,null))||'~'||
                      min(Decode(c1.Position,4,c1.column_name,null)) ||'~'||
                      min(Decode(c1.Position,5,c1.column_name,null)) ||'~'||
                      min(Decode(c1.Position,6,c1.column_name,null)) ||'~'||
                      min(Decode(c1.Position,7,c1.column_name,null)) ||'~'||
                      min(Decode(c1.Position,8,c1.column_name,null)) ||'~'||
                      min(Decode(c1.Position,9,c1.column_name,null)),'~~') cons_cols
               from user_cons_columns c1
               Group by c1.constraint_name ) cons_col  ,   
                ( select rc1.constraint_name, rc1.table_name, replace(min(Decode(rc1.Position,1,rc1.column_name,null))||'~'||
                      min(Decode(rc1.Position,2,rc1.column_name,null)) ||'~'||
                      min(Decode(rc1.Position,3,rc1.column_name,null)) ||'~'||
                      min(Decode(rc1.Position,4,rc1.column_name,null)) ||'~'||
                      min(Decode(rc1.Position,5,rc1.column_name,null)) ||'~'||
                      min(Decode(rc1.Position,6,rc1.column_name,null)) ||'~'||
                      min(Decode(rc1.Position,7,rc1.column_name,null))||'~'||
                      min(Decode(rc1.Position,8,rc1.column_name,null)) ||'~'||
                      min(Decode(rc1.Position,9,rc1.column_name,null)),'~~') cons_cols
               from user_cons_columns rc1
               Group by rc1.constraint_name, rc1.TABLE_NAME ) rcons_col
               Where  c.Constraint_Type in ('P','R','C','U')
               And    c.Constraint_Name Not Like 'SYS_C%'
               and    c.Constraint_Name Not Like 'BIN$%'
               and    c.Constraint_name = cons_col.constraint_name (+) 
               and    c.r_Constraint_name = rcons_col.constraint_name (+) 
               Order By 7
             """
    return extract_meta_data(sql,'CONSTRAINT_NAME',p_filename,p_file)

def extract_sequences(p_sequence:str ="",
                      p_filename:str = get_param_value('SEQUENCES_FILE'),
                      p_file:bool = True):
    sql = """select  s.sequence_name,s.min_value,s.max_value,s.increment_by, user datasource
                    from user_sequences s  order by s.sequence_name
            """
    return extract_meta_data(sql,'SEQUENCE_NAME',p_filename,p_file)


def extract_triggers(p_trigger:str ="",
                     p_filename:str = get_param_value('TRIGGERS_FILE'),
                     p_file:bool = True):
    sql = """Select t.trigger_name, t.trigger_type, t.triggering_event,t.base_object_type,t.table_name, 
            t.referencing_names,
            t.trigger_body, user datasource
            From User_Triggers t
            """
    return extract_meta_data(sql,'TRIGGER_NAME',p_filename,p_file)


def extract_source(p_name:str ="",
                   p_filename:str = get_param_value('ALLSOURCES_FILE') ,
                   p_file:bool = True):
    sql = """select Name,Type,Line,Text, user datasource
            from user_source 
            order by  name, type, line 
            """
    return extract_meta_data(sql,'NAME',p_filename,p_file)

def extract_views(p_name:str ="",p_filename:str = get_param_value('VIEWS_FILE') ,
                  p_file:bool = True):
    sql = """select view_name,text, text_length,user datasource  
                from user_views 
                Order By 1
            """
    return extract_meta_data(sql,'VIEW_NAME',p_filename,p_file)

def extract_allobjects(p_objectname:str ="",
                       p_filename:str = get_param_value('ALLOBJECTS_FILE'),
                       p_file:bool = True):
    sql = """  select Object_name, Object_type, last_ddl_Time, user datasource
                  from user_objects 
                  Where object_type not in ('LOB')
                  order by 2,1
            """
    return extract_meta_data(sql,'OBJECT_NAME',p_filename,p_file)

def extract_indexes(p_indexname:str ="",
                    p_filename:str = get_param_value('INDEXES_FILE'),
                    p_file:bool = True):
    sql = """  select i.Index_Name, i.Index_Type,i.Table_Name,i.Table_Type,i.Tablespace_Name, 
                indcol.ind_cols, user datasource
               From   User_Indexes i,
                ( select c1.index_name, replace(min(Decode(c1.column_Position,1,c1.column_name,null))||'~'||
                      min(Decode(c1.column_Position,2,c1.column_name,null))||'~'||
                      min(Decode(c1.column_Position,3,c1.column_name,null))||'~'||
                      min(Decode(c1.column_Position,4,c1.column_name,null)) ||'~'||
                      min(Decode(c1.column_Position,5,c1.column_name,null))||'~'||
                      min(Decode(c1.column_Position,6,c1.column_name,null)) ||'~'||
                      min(Decode(c1.column_Position,7,c1.column_name,null)) ||'~'||
                      min(Decode(c1.column_Position,8,c1.column_name,null))||'~'||
                      min(Decode(c1.column_Position,9,c1.column_name,null)),'~~') ind_cols
               from user_ind_columns c1
               Group by c1.index_name ) indcol   
               Where i.index_name = indcol.index_name 
              order by i.Table_name,i.index_name
            """
    return extract_meta_data(sql,'INDEX_NAME',p_filename,p_file)

def extract_metadata_all(p_file:bool = True):
    data = extract_columns('TABLE',p_filename=get_param_value('TABLE_COLUMNS_FILE'), p_file=p_file)
    data = extract_columns('VIEW',p_filename=get_param_value('VIEW_COLUMNS_FILE'), p_file=p_file)
    data = extract_sequences(p_file=p_file)
    data = extract_constraints(p_file=p_file)
    data = extract_allobjects(p_file=p_file)
    data = extract_indexes(p_file=p_file)
    data = extract_triggers(p_file=p_file)
    data = extract_source(p_file=p_file)
    data = extract_views(p_file=p_file)

def read_indexes(p_filename:str = 'indexes.csv'):
    data = read_meta_data('INDEX_NAME','indexes.csv')


def read_metadata_all(p_file:bool = True):
    #data = extract_columns('TABLE',p_filename='table_columns',p_file=p_file)
    #data = extract_columns('VIEW',p_filename='view_columns',p_file=p_file)
    #data = extract_sequences(p_file=p_file)
    #data = extract_constraints(p_file=p_file)
    #data = extract_allobjects(p_file=p_file)
    indexes = read_indexes()
    #data = extract_triggers(p_file=p_file)
    #data = extract_source(p_file=p_file)
    #data = extract_views(p_file=p_file)


def extract_setupdata_all(p_file:bool = True):
    for view, file in get_param_value('API_EXTRACT_DATA'):
        data =  extract_setup_data(view, file, p_file=p_file)
    for view, file in get_param_value('EXTRACT_SETUP_DATA'):
        data =  extract_table_data(view, file, p_file=p_file)


def read_setupdata_all(p_apply:bool = False):
    try:
        for view, file in et_param_value('API_EXTRACT_DATA'):
            try:
                print('reading:',file)
                data =  read_file(file)
                data = data.replace('END;','\n NULL;\n END;')
                if p_apply:
                    if commonutil.hasstrvalue(data):
                        if 'cmn_lookupcodes' in file:
                            for block in data.split('\n/'):
                                try:
                                    if len(block) > 30:
                                        dbfuncs.exec_plsqlblockraw(block)
                                except:
                                    print('FAILED:*****',block)
                        else:
                            dbfuncs.exec_plsqlblockraw(data)
                    else:
                        print('data',data)
            except:
                print('execustion failed:',data)
    except:
        print('failed:')

def get_datawitdh(p_datatype,p_datawidth, p_precision):
    if p_datatype == 'NUMBER':
        return '({},{})'.format(p_datawidth,p_precision)
    if 'CHAR' in p_datatype:
        return '({})'.format(p_datawidth)
    return ''

def get_nullable(p_val):
    if not p_val or p_val == 'False':
       return 'NOT NULL'
    return 'NULL'

def get_defaultval(p_val):
    if p_val == 'None':
        return ''
    if commonutil.hasstrvalue(p_val):
        return "default {}".format(p_val)
    return ''

def write_ddl(p_lines:[], p_mode:str = 'w',
              p_filename:str = 'missing_objects.sql',
              p_directory = 'UPGRADE_DIR'):
    filenaame = set_file_path(p_filename,p_directory)
    with open(filenaame, p_mode) as file:
       file.writelines(p_lines)

def check_tables(p_compare:bool = True, p_filemode ='w'):
    filename = get_param_value('TABLE_COLUMNS_FILE')
    sourcefile = set_file_path(filename,'UPDATES_DIR')
    print(sourcefile)
    destfile = set_file_path(filename,'UPGRADE_DIR')
    lines = []
    data = pd.read_csv(sourcefile,index_col='OBJECT_NAME').astype(str)
    if data.empty:
        return False
    data.drop(columns=['DATASOURCE'],inplace=True)
    tablemissing = 1
    prevtable = ""
    cols = 0
    for table_name, val  in data.iterrows():
        val = dict(val)
        val['OBJECT_NAME'] = table_name
        defaultval = val['DEFAULTVAL']
        if 'NEXTVAL' in defaultval:
            defaultval = '.'.join(defaultval.split('.')[1:])
            val['DEFAULTVAL'] = defaultval
        column_name = val['COLUMN_NAME']
        datatype  = val['DATA_TYPE']
        datawidth = val['DATA_WIDTH']
        dataprecision = val['DATA_PRECISION']
        datawidth = get_datawitdh(datatype,datawidth,dataprecision)
        nullable = val['NULLABLE']
        nullable = get_nullable(nullable)
        defaultval = get_defaultval(defaultval)
        if prevtable != table_name:
            cols = 0
            if tablemissing == 0:
                line = ');\n'
                lines.append(line)
            if p_compare:
                tablemissing = dbfuncs.is_db_object_exists(table_name)
            else:
                tablemissing = 0
            prevtable = table_name
            if tablemissing == 0:
                line = 'create table {} (\n'.format(table_name)
                lines.append(line)
        if tablemissing == 0:
            if cols == 0:
                comma = ''
            else:
                comma = ','
            line = """{} {} {}{} {} {}\n""".format(
               comma, column_name,datatype, datawidth, nullable, defaultval)
            cols += 1
            lines.append(line)
        else:
            currcoldef = dbfuncs.get_col_def(table_name,column_name)
            if not currcoldef == val:
                #add alter table statement
                line = """Alter Table {} modify({} {}{} {} {});\n""".format(
                    table_name,column_name,datatype, datawidth, nullable, defaultval)
                lines.append(line)
    if len(lines) > 0 and tablemissing == 0:
        lines.append(');\n')
    write_ddl(lines,p_filemode)
    return True

def check_sequences(p_compare:bool = True,p_filemode ='w'):
    filename = get_param_value('SEQUENCES_FILE')
    sourcefile = set_file_path(filename,'UPDATES_DIR')
    print(sourcefile)
    lines = []
    data = pd.read_csv(sourcefile,index_col='SEQUENCE_NAME').astype(str)
    if data.empty:
        return False
    for object_name, val  in data.iterrows():
        val = dict(val)
        if p_compare:
            objectmissing = dbfuncs.is_db_object_exists(object_name)
        else:
            objectmissing = 0
        if objectmissing == 0:
            line = "create sequence {} MINVALUE {} MAXVALUE {} INCREMENT BY {}   ;\n".format(
                object_name,val['MIN_VALUE'],val['MAX_VALUE'],val['INCREMENT_BY'])
            lines.append(line)
    write_ddl(lines,p_filemode)
    return True

def check_missingobjects(p_compare:bool = True,p_filemode ='w'):
    filename = get_param_value('ALLOBJECTS_FILE')
    sourcefile = set_file_path(filename,'UPDATES_DIR')
    lines = []
    data = pd.read_csv(sourcefile,index_col='OBJECT_NAME').astype(str)
    if data.empty:
        return False
    for object_name, val  in data.iterrows():
        val = dict(val)
        if p_compare:
            objectmissing = dbfuncs.is_db_object_exists(object_name)
        else:
            objectmissing = 0
        if objectmissing == 0:
            line = "-- {}  {} {}   -- missing;\n".format(
                object_name,val['OBJECT_TYPE'],val['LAST_DDL_TIME'])
            lines.append(line)
    write_ddl(lines,p_filemode)
    return True

def check_constraints(p_compare:bool = True,p_filemode ='w'):
    filename = get_param_value('CONSTRAINTS_FILE')
    sourcefile = set_file_path(filename,'UPDATES_DIR')
    print(sourcefile)
    lines = []
    data = pd.read_csv(sourcefile,index_col='CONSTRAINT_NAME').astype(str)
    if data.empty:
        return False
    for object_name, val  in data.iterrows():
        val = dict(val)
        if p_compare:
            objectmissing = dbfuncs.is_constraint_exists(object_name)
        else:
            objectmissing = 0
        if objectmissing == 0:
            #CONSTRAINT_NAME,CONSTRAINT_TYPE,TABLE_NAME,SEARCH_CONDITION,REF_PK,DELETE_RULE,CORDERBY,CONS_COLS,REF_TABLE,REF_COLUMNS,DATASOURCE
            if val['CONSTRAINT_TYPE'] == 'FOREIGN':
                line = "alter table {} add constraint {} \n {} ( {}) REFERENCES {}({}) ON DELETE {};\n".format(
                    val['TABLE_NAME'], object_name,val['CONSTRAINT_TYPE'],val['CONS_COLS'], val['REF_TABLE'],
                    val['REF_COLUMNS'],val['DELETE_RULE']
                     )
            else:
                line = "alter table {} add constraint {} \n {}( {}) ;\n".format(
                    val['TABLE_NAME'], object_name,val['CONSTRAINT_TYPE'], val['CONS_COLS']
                )
            lines.append(line.replace('~',',').replace(',)',')'))
    write_ddl(lines,p_filemode)
    return True

def check_indexes(p_compare:bool = True,p_filemode ='w'):
    filename = get_param_value('INDEXES_FILE')
    sourcefile = set_file_path(filename,'UPDATES_DIR')
    print(sourcefile)
    lines = []
    data = pd.read_csv(sourcefile,index_col='INDEX_NAME').astype(str)
    if data.empty:
        return False
    for object_name, val  in data.iterrows():
        val = dict(val)
        if p_compare:
            objectmissing = dbfuncs.is_db_object_exists(object_name)
        else:
            objectmissing = 0
        if objectmissing == 0:
            line = "create index  {} on {} ( {}) tablespace {} ;\n".format(
                     object_name,val['TABLE_NAME'], val['IND_COLS'], val['TABLESPACE_NAME']
                )
            lines.append(line.replace('~',',').replace(',)',')'))
    write_ddl(lines,p_filemode)
    return True

def generate_views(p_compare:bool = True,p_filemode ='w'):
    filename = get_param_value('VIEWS_FILE')
    sourcefile = set_file_path(filename,'UPDATES_DIR')
    lines = []
    data = pd.read_csv(sourcefile,index_col='VIEW_NAME').astype(str)
    if data.empty:
        return False
    for object_name, val  in data.iterrows():
        val = dict(val)
        if p_compare:
            objectmissing = dbfuncs.is_db_object_exists(object_name)
        else:
            objectmissing = 0
        if objectmissing == 0:
            line = "create or eplace view   {} as  \n {} ;\n".format(
                     object_name,val['TEXT']
                )
            lines.append(line)
    write_ddl(lines,p_filemode)
    return True


def generate_sources(p_compare:bool = True, p_objectType:str = 'PACKAGE', p_filemode ='w'):
    filename = get_param_value('ALLSOURCES_FILE')
    sourcefile = set_file_path(filename,'UPDATES_DIR')
    lines = []
    data = pd.read_csv(sourcefile,index_col='NAME').astype(str)
    if data.empty:
        return False
    data = data[data.TYPE == p_objectType]
    for object_name, val  in data.iterrows():
        val = dict(val)
        if p_compare:
            objectmissing = dbfuncs.is_db_object_exists(object_name)
        else:
            objectmissing = 0
        if objectmissing == 0:
            if val['LINE'] == '1':
                line = "\n/  \nshow error\n\ncreate or replace  {}".format(
                     val['TEXT']
                )
            else:
                line = "{}".format(val['TEXT'])
            lines.append(line)
    lines.append("\n/\nShow Error\n\n")
    write_ddl(lines,p_filemode)
    return True


def generate_db_script(p_compare:bool = True):
    check_missingobjects(p_compare,'w')
    check_sequences(p_compare,'a')
    check_tables(p_compare,'a')
    check_constraints(p_compare,'a')
    check_indexes(p_compare,'a')
    generate_sources(p_compare,'PACKAGE','a')
    generate_sources(p_compare,'PROCEDURE','a')
    generate_sources(p_compare,'FUNCTION','a')
    generate_views(p_compare,'a')
    generate_sources(p_compare,'PACKAGE BODY','a')
    generate_sources(p_compare,'TRIGGER','a')