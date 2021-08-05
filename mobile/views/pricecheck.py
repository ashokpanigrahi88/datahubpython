from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from mobile.forms import PriceCheckForm
from common import dbfuncs as dbfunc
from common.models import (InvItemMasters)


# specific to this view



@method_decorator(login_required, name='dispatch')
class PriceCheckView(TemplateView):
        template_name = 'mobile/pricecheck.html'
        context_object_name = 'form'
        itemdict = {}

        def get(self, request, *args, **kwargs):
            return super(PriceCheckView, self).get(request, *args, **kwargs)

        def get_queryset(self):
            pass

        def get_context_data(self, **kwargs):
            context = super(PriceCheckView, self).get_context_data(**kwargs)
            f_itemnumber = self.request.GET.get('item_number')
            f_fuzzysearch = self.request.GET.get('fuzzy_search')
            page = self.request.GET.get('page')
            userid = self.request.user.user_id
            items = None
            item = None
            sublocstock = None
            itemsinpo = None
            itemsallocated = None
            lookuptype  = 'MOBILE_DEFAULTS';
            businessunit = self.request.user.bu_id
            context['businessunit'] = businessunit
            context['form'] = PriceCheckForm()
            if f_itemnumber is not None:
                #rows = rows.filter(lookup_type__icontains=f_nm)
                pass
            if f_fuzzysearch == 'Y' and f_itemnumber is not None:
                f_fuzzysearch = dbfunc.get_fuzzyserch(f_itemnumber)
                sql =   """ Select Mobile_Pkg.Get_ImageTag(Picturename3) Picturename3,
                        Item_Number ,
                        Inv_Pkg.Get_SuBin(Item_Id) SuBin,Item_Name,
                  	    ItemStatus_Pkg.GetQtyInStock(item_id) instock                    
                        From inv_Item_Masters_v  Where {0}  Order By Item_Name""".format(f_fuzzysearch)
                print(sql)
                items = dbfunc.exec_sql(sql)

            if f_fuzzysearch == 'N' and f_itemnumber is not None:
                item = InvItemMasters.objects.all().filter(item_number__exact=f_itemnumber)
                if not item:
                    context['errormessage'] = 'Item does not exist or Invalid: '+f_itemnumber
                    return context
                item = item[0]
                print('item', item)
                self.itemdict['SUBIN'] = dbfunc.select_sqlfunc('Inv_Pkg.GetSUIDByItemID({0})'.format(item.item_id))
                self.itemdict['SUID'] = dbfunc.select_sqlfunc('Inv_Pkg.GetSUIDByItemID({0})'.format(item.item_id))
                self.itemdict['LOCATION_ID'] = dbfunc.select_sqlfunc(
                                'Mobile_Pkg.Get_LocationIdByUserId({0})'.format(userid)
                                    )
                self.itemdict['SUBLOCATION_ID'] = dbfunc.select_sqlfunc(
                    """Location_Pkg.Get_ItemDefSubLocByGroup({0},{1})""".format(self.itemdict['LOCATION_ID'],item.item_id))

                self.itemdict['SUBLOCATION'] = dbfunc.select_sqlfunc(
                                    "INV_Pkg.GetSubLocationName( {0})".format(self.itemdict['SUBLOCATION_ID']))

                self.itemdict['PRICETYPE'] = dbfunc.get_lookupattribute(lookuptype,'PC:PRICETYPE',1,'EXLTAX')
                if dbfunc.get_lookupattribute(lookuptype,'PC:PB',1,'YES') == 'YES':
                    self.itemdict['PBTEXT'] = dbfunc.exec_str_func('Price_Pkg.Get_PriceBreakText',
                                             [item.ipbh_price_break_id,item.item_id,self.itemdict['SUID'],1,1])

                if self.request.user.customer_id is not None:
                    self.itemdict['PRICE'] = dbfunc.select_sqlfunc(
                        'Price_Pkg.Get_ItemCustomerSp({0),{1})'.format(item.item_id,self.request.user.customer_id)
                    )
                if dbfunc.get_lookupattribute(lookuptype, 'PC:PRICE1', 1, 'YES') == 'YES':
                    self.itemdict['PRICE1_IN'] , self.itemdict['PRICE1_EX']  \
                        = dbfunc.get_itemprice(1,self.itemdict['SUID'] )
                if dbfunc.get_lookupattribute(lookuptype, 'PC:PRICE2', 2, 'YES') == 'YES':
                    self.itemdict['PRICE2_IN'] , self.itemdict['PRICE2_EX']  \
                        = dbfunc.get_itemprice(2,self.itemdict['SUID'] )
                if dbfunc.get_lookupattribute(lookuptype, 'PC:PRICE3', 3, 'YES') == 'YES':
                    self.itemdict['PRICE3_IN'] , self.itemdict['PRICE3_EX']  \
                        = dbfunc.get_itemprice(3,self.itemdict['SUID'] )
                if dbfunc.get_lookupattribute(lookuptype, 'PC:PRICE4', 1, 'YES') == 'YES':
                    self.itemdict['PRICE4_IN'] , self.itemdict['PRICE4_EX']  \
                        = dbfunc.get_itemprice(4,self.itemdict['SUID'] )
                if dbfunc.get_lookupattribute(lookuptype, 'PC:PRICE5', 1, 'YES') == 'YES':
                    self.itemdict['PRICE5_IN'] , self.itemdict['PRICE5_EX']  \
                        = dbfunc.get_itemprice(5,self.itemdict['SUID'] )
                if dbfunc.get_lookupattribute(lookuptype, 'PC:RETAILPRICE', 1, 'YES') == 'YES':
                    sql =  """ SELECT Price_Exltax, Price_Inctax
                              FROM  Inv_Item_Sales_Units
                              WHERE Su_ID = {0}""".format(self.itemdict['SUID'])
                    results = dbfunc.exec_sql(sql,'dict',1)
                    self.itemdict['RETPRICE_IN'] = results[1]
                    self.itemdict['RETPRICE_EX'] = results[0]
                if dbfunc.get_lookupattribute(lookuptype, 'PC:FLAGS', 1, 'YES') == 'YES':
                    self.itemdict['ITEMFLAGS'] =  """ PUR={0} , SAL={1}, RES={2}, 
                                            ENF REORD QTY={3}, STATUS={4}""".format(item.purchaseable, item.saleable,
                                                       item.reservable,
                                                        item.enforce_reorder_qty.replace('','N'),
                                                       item.item_status)

                if dbfunc.get_lookupattribute(lookuptype, 'PC:INSTOCK', 1, 'YES') == 'YES':
                    self.itemdict['INSTOCK'] = dbfunc.select_sqlfunc(
                        'Itemstatus_Pkg.GetQtyinStock({0})'.format(item.item_id)
                    )

                if dbfunc.get_lookupattribute(lookuptype, 'PC:SUBLOCSTOCK', 1, 'YES') == 'YES':
                    sql = """ SELECT l.Location_Name,
                            s.Sub_Location,i.Quantity, Sfn_Divide(i.Quantity,ii.case_unit) Qty_Cases, 
                            i.Min_Qty, i.max_qty, 
                            Mobile_Pkg.StarSubLocation('{0}',S.Sub_Location,s.Sub_Loc_Group_code) GroupCode
                        FROM  inv_item_sub_Locations_V i, Inv_Sub_Locations s, inv_locations l,Inv_Item_Masters ii 
                        WHERE s.Sub_Location_ID = i.Sub_Location_Id  
                        and s.IL_Location_Id = l.Location_Id 
                        and i.Quantity <> 0   and   s.Include_stock = 'Y'
                        AND   i.item_Id  = ii.item_id  
                        AND   i.Item_Id = {1}  order by 1,2""".format(self.itemdict['SUBLOCATION'], item.item_id)
                    sublocstock = dbfunc.exec_sql(sql,'dict')

                if dbfunc.get_lookupattribute(lookuptype, 'PC:ITEMINPO', 1, 'YES') == 'YES':
                    sql = """    Select Sum(Qty_Balance)
                                From    Rep_ItemInPo_V
                                Where  Item_ID = {0}""".format(item.item_id)
                    results = dbfunc.exec_sql(sql, 'dict',1)
                    self.itemdict['POBLANCE_QTY'] = results[0]
                    sql = """ Select PO_Number, Order_status_Date,LinePromised_Date,
                                    LineNeedBy_Date, Qty_Balance 
                             From REP_ITEMINPO_V 
                            Where Item_Id = {0} order by 1,2""".format(item.item_id)
                    itemsinpo = dbfunc.exec_sql(sql, 'dict')

                if dbfunc.get_lookupattribute(lookuptype, 'PC:ITEMINPO', 1, 'YES') == 'YES':
                    sql = """    Select Sum(Qty_PickOutstanding_Units)
                                From    REP_ITEMALLOCATED_V
                                Where  Item_ID = {0}""".format(item.item_id)
                    results = dbfunc.exec_sql(sql, 'dict',1)
                    self.itemdict['SOALLOC_QTY'] = results[0]
                    sql = """ SELECT Order_Number, Order_status_Date,Order_Type, 
                            Qty_Ordered_Units, Qty_PickOutstanding_Units,
                            sfn_divide(Qty_Ordered_Units,case_Unit) qty_orered_cases,
                            sfn_divide(Qty_PickOutstanding_Units,case_Unit) qty_PickOutstanding_cases
                            From REP_ITEMALLOCATED_V 
                            Where Item_Id = {0} order by 2,1""".format(item.item_id)
                    itemsallocated = dbfunc.exec_sql(sql, 'dict')
            self.itemdict['itemnumber'] = f_itemnumber
            self.itemdict['fuzzysearch'] = f_fuzzysearch
            context['itemdict'] = self.itemdict
            context['rows'] = items
            context['item'] = item
            context['rowset2'] = sublocstock
            context['rowset3'] = itemsinpo
            context['rowset4'] = itemsallocated
            return context

