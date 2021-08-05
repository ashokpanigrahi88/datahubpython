from common import (dbfuncs, commonutil)

def get_rowset(p_namedquery:{}, p_param:[], p_rowprefix:str = 'row', **kwargs):
    sql = str()
    sql  = p_namedquery['sql']
    header  = p_namedquery['header']
    dispcolumns  = p_namedquery['columns']
    sql = sql.format(*p_param)
    rows = dbfuncs.exec_sql(sql)
    tableheader = ' '.join(map(str, ["<th>{}</th>\n".format(i) for i in header ]))
    tablecolumns  = ' '.join(map(str, ["<td>{{ "+"{}.{}".format(p_rowprefix, i) +" }}</td>\n" for i in dispcolumns ]))
    print(sql,tableheader, tablecolumns, rows)
    return rows , tableheader, tablecolumns

Q_GETBATCHITEMS = {'sql': """ Select Item_Id, Item_Number, Item_Name , Batch_ID
                From Inv_Item_BATCH_LINES_VA
                Where Batch_ID = {}""",
                'header': ['Item Number','Item Name','Batch Id','Item Id'],
                'columns': ['ITEM_NUMBER','ITEM_NAME','BATCH_ID','ITEM_ID']
        }


Q_APINVHEADER = {'sql': """ Select Item_Id, Item_Number, Item_Name , Batch_ID
                From Inv_Item_BATCH_LINES_VA
                Where Batch_ID = {}""",
                'header': ['Item Number','Item Name','Batch Id','Item Id'],
                'columns': ['ITEM_NUMBER','ITEM_NAME','BATCH_ID','ITEM_ID']
        }