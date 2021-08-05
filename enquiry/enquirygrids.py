from django.utils.safestring import mark_safe


def supplier_grid(p_colcontext:str = 'row.', p_footercontext:str = 'rowset_totals.'):
    header  = """   <th> Number</th> <th>Name</th> <th>Contact Name1</th> <th>Contact Name2</th> 
                <th>Address</th> <th> City</th> <th>PostCode </th> 
                <th>Phone </th>  <th>Email </th>
              <th>Date Cahnged </th>"""

    columns = """   <td> <a href={% url 'enquiry:supplierdrilldown' %}?supplier_id={{row.supplier_id}}>{{row.supplier_number}}</a>
                           {% if row.noof_orders %}
                            <a href={% url 'enquiry:posum' %}?supplier_id={{row.supplier_id}}>PO({{ row.noof_orders }})</a>
                            {% endif %}
                        {% if row.noof_goodsins %}
                         <a href={% url 'enquiry:grnsum' %}?supplier_id={{row.supplier_id}}>GoodsIn({{ row.noof_goodsins }})</a>
                         {% endif %}
                        {% if row.noof_invocies %}
                         <a href={% url 'enquiry:apinvoicesum' %}?supplier_id={{row.supplier_id}}>Inv({{ row.noof_invoices }})</a>
                         {% endif %}
                    </td>
            <td>{{row.supplier_name }}</td> <td>{{row.contact_name1 }}</td> <td>{{row.contact_name2 }}</td>
             <td>{{row.address_line1 }}</td>  <td>{{row.city }}</td>  <td>{{row.post_code }}</td>
             <td>{{row.phone1 }}</td> <td>{{row.emaill }}</td>          
            <td>{{row.last_update_date|date:"SHORT_DATE_FORMAT"  }}</td>
            """
    totals = ""
    return header, columns.replace('row.', p_colcontext), totals.replace('rowset_totals.', p_footercontext)

def po_grid(p_colcontext:str = 'row.', p_footercontext:str = 'rowset_totals.'):
    header = """      <th>Number</th>
                        <th>Date</th>
                        <th>Status</th>
                        <th>Type</th>
                        <th>Supplier </th>
                        <th>Location </th>
                        <th>Net </th>
                        <th>Vat</th>
                        <th>Gross</th>
                        <th>Weight</th>
                        <th>Volume</th>
                        <th>Ingredient</th>"""
    columns = """   
       <td> <a href={% url 'enquiry:posum' %}?po_header_id={{row.po_header_id}}>{{row.po_number}}</a></td>
            <td>{{row.order_status_date|date:"SHORT_DATE_FORMAT"  }}</td>
            <td>{{row.order_status }}</td>
            <td>{{row.po_type }}</td>
            <td>{{row.sup_supplier_id.supplier_name }}</td>
            <td>{{row.shipto_location_id.location_name }}</td>
            <td>{{row.net_total }}</td>
            <td>{{row.vat_total }}</td>
            <td>{{row.gross_total }}</td>
            <td>{{row.weight_total }}</td>
            <td>{{row.volume_total }}</td>
            <td>{{row.ingredient_total }}</td>
            """
    totals = """   
            <td>Total</td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td>{{row.net_total }}</td>
            <td>{{row.vat_total }}</td>
            <td>{{row.gross_total }}</td>
            <td>{{row.weight_total }}</td>
            <td>{{row.volume_total }}</td>
            <td>{{row.ingredient_total }}</td>
            """
    return header, columns.replace('row.', p_colcontext), totals.replace('rowset_totals.', p_footercontext)

def poline_grid(p_colcontext:str = 'row.', p_footercontext:str = 'rowset_totals.'):
    header = """   <th> ID</th>
                            <th> Sl No </th>
                             <th> Item Number </th>
                             <th> Item Name</th>
                             <th> Sup Code </th>
                              <th> Case Size  </th>
                               <th> Unit CP </th>
                               <th> Case CP </th>
                              <th> Tax Rate </th>
                             <th> Qty Cases </th>
                              <th> Qty Ordered </th>
                             <th> Qty Goodsin </th>
                            <th> Qty Balance </th>
                             <th> Net Price </th>
                            <th> Tax Price </th>
                           <th> Weight Total </th>
                            <th> Volume Total </th>
                            """
    columns =  """  <td> {{ row.po_line_id }}</td>
                            <td> {{ row.sl_no }}</td>
                             <td> {{ row.item_id.item_number }}</td>
                             <td> {{ row.item_name }}</td>
                             <td> {{ row.supplier_product_code }}</td>
                            <td> {{ row.case_size }}</td>
                            <td> {{ row.unit_cp }}</td>
                            <td> {{ row.case_cp }}</td>
                            <td> {{ row.tax_rate }}</td>
                             <td> {{ row.qty_ordred_cases }}</td>
                             <td> {{ row.qty_ordered_units }}</td>
                              <td> {{ row.qty_goodsin  }}</td>
                             <td> {{ row.qty_balance }}</td>
                              <td> {{ row.net_price }}</td>
                             <td> {{ row.tax_Price }}</td>
                            <td> {{ row.weight_total }}</td>
                             <td> {{ row.volume_total }}</td> """
    totals =""" <td>Totals</td>
                            <td> </td>
                             <td> </td>
                             <td> </td>
                             <td> </td>
                            <td> </td>
                            <td></td>
                            <td></td>
                            <td> </td>
                             <td> {{ rowset_totals.qty_ordred_cases }}</td>
                             <td> {{ rowset_totals.qty_ordered_units }}</td>
                              <td> {{ rowset_totals..qty_goodsin  }}</td>
                             <td> {{ rowset_totals.qty_balance }}</td>
                              <td> {{ rowset_totals.net_price }}</td>
                             <td> {{ rowset_totals.tax_Price }}</td>
                            <td> {{ rowset_totals.weight_total }}</td>
                             <td> {{ rowset_totals.volume_total }}</td>
                             """
    return header, columns.replace('row.', p_colcontext), totals.replace('rowset_totals.', p_footercontext)

def grn_grid(p_colcontext:str = 'row.', p_footercontext:str = 'rowset_totals.'):
    header =  """ <th>Number</th>
                        <th>Date</th>
                        <th>Status</th>
                        <th>Supplier </th>
                        <th>Location </th>
                        <th>PO </th>
                        <th>Net </th>
                        <th>Vat</th>
                        <th>Gross</th>
                        <th>Weight</th>
                        <th>Volume</th>
                        <th>Ingredient</th>"""
    columns =  """   
       <td> <a href={% url 'enquiry:grnsum' %}?grn_id={{row.grn_id}}>{{row.grn_number}}</a></td>
            <td>{{row.grn_status_date|date:"SHORT_DATE_FORMAT"  }}</td>
            <td>{{row.grn_status }}</td>
            <td>{{row.sup_supplier_id.supplier_name }}</td>
            <td>{{row.shipto_location_id.location_name }}</td>
       <td> <a href={% url 'enquiry:posum' %}?po_header_id={{row.po_header_id}}>{{row.po_header_id}}</a></td>
            <td>{{row.net_total }}</td>
            <td>{{row.vat_total }}</td>
            <td>{{row.gross_total }}</td>
            <td>{{row.weight_total }}</td>
            <td>{{row.volume_total }}</td>
            <td>{{row.ingredient_total }}</td>
            """
    totals = """   
            <td>Total</td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td>{{rowset_totals.net_total }}</td>
            <td>{{rowset_totals.vat_total }}</td>
            <td>{{rowset_totals.gross_total }}</td>
            <td>{{rowset_totals.weight_total }}</td>
            <td>{{rowset_totals.volume_total }}</td>
            <td>{{rowset_totals.ingredient_total }}</td>
            """
    return header, columns.replace('row.', p_colcontext), totals.replace('rowset_totals.', p_footercontext)

def apinv_grid(p_colcontext:str = 'row.', p_footercontext:str = 'rowset_totals.'):
    header = """ <th>Number</th> <th>Sup Invoice</th>  <th>Date</th>  <th>Recieved on</th>  <th>Status</th> <th>Type</th>
                <th>Supplier </th>  <th>Net </th> <th>Vat</th>  <th>Gross</th> <th>Paid</th> <th>Balance</th> """
    columns = """ <td>{{row.invoice_number }}</td>  <td>{{row.voucher_num }}</td>  <td>{{row.invoice_status_date|date:"SHORT_DATE_FORMAT"  }}</td>
            <td>{{row.invoice_received_date|date:"SHORT_DATE_FORMAT" }}</td>  <td>{{row.invoice_status }}</td>
            <td>{{row.invoice_type }}</td> <td>{{row.sup_supplier_id.supplier_name }}</td> <td>{{row.net_total }}</td>
            <td>{{row.vat_total }}</td> <td>{{row.gross_total }}</td>  <td>{{row.paid_total }}</td>
             <td>{{row.balance_total }}</td>"""
    totals = """ <td>Total</td> <td></td>  <td></td> <td></td> <td></td> <td></td> <td> </td>
                                  <td>{{rowset_totals.net_total }}</td>
                                  <td>{{rowset_totals.vat_total }}</td>
                                  <td>{{rowset_totals.gross_total }}</td>
                                  <td>{{rowset_totals.paid_total }}</td>
                                  <td>{{rowset_totals.balance_total }}</td>"""
    return header, columns.replace('row.', p_colcontext), totals.replace('rowset_totals.', p_footercontext)

def apinvline_grid(p_colcontext:str = 'row.', p_footercontext:str = 'rowset_totals.'):
    header =  """  <th> Sl No </th> <th> Inv Number </th>  <th> Description </th> <th> Tax Rate </th>
              <th> Unit </th> <th> Qty </th>  <th> Price </th> <th> Net </th> <th> Tax </th> <th> Total </th>"""
    columns =  """ <td>{{row.sl_no }}</td> <td>{{row.invoice_id.invoice_number }}</td> <td>{{row.description }}</td>
                <td>{{row.tax_rate }}</td> <td>{{row.unit }}</td> <td>{{row.qty_invoiced_units }}</td>  <td>{{row.invoice_amount_exl_tax }}</td>
                    <td>{{row.net_amount }}</td>
                    <td>{{row.tax_amount }}</td>
                     <td>{{row.total_line_amount }}</td> """
    totals = """ <td>Totals</td>
                <td></td>
                <td></td>
                <td></td>
                <td></td>
                <td>{{rowset_totals.qty_invoiced_units }}</td>
                <td>{{rowset_totals.invoice_amount_exl_tax }}</td>
                <td>{{rowset_totals.net_amount }}</td>
                <td>{{rowset_totals.tax_amount }}</td>
                <td>{{rowset_totals.total_line_amount }}</td>"""
    return header, columns.replace('row.', p_colcontext), totals.replace('rowset_totals.', p_footercontext)

def pmnt_grid(p_colcontext:str = 'row.', p_footercontext:str = 'rowset_totals.'):
    header =  """ <th> Mehod </th>
                    <th> Status </th> 
                    <th> Date </th> 
                    <th> Amount </th> 
                    """
    columns =  """<td> {{ row3.pmnt_method_id.pmnt_method }}</td> <td> {{ row3.payment_line_status }} </td>
                                        <td> {{ row3.payment_line_status_date|date:"SHORT_DATE_FORMAT"   }}</td>
                                        <td> {{ row3.payment_amount }}</td>                                        """
    totals = ""
    return header, columns.replace('row.', p_colcontext), totals.replace('rowset_totals.', p_footercontext)


def arinv_grid(p_colcontext:str = 'row.', p_footercontext:str = 'rowset_totals.'):
    header  = """ <th>Invoice Number</th> <th>Date</th>  <th>Status</th> <th>Type</th>
              <th>Location</th> <th>Customer Name </th> <th>Cust Number </th> <th>Order ID </th> <th>Net </th>
            <th>Vat</th> <th>Gross</th> <th>Paid</th> <th>Balance</th> """
    columns   = """   <td>   <a href={% url 'enquiry:arinvoicesum' %}?invoice_header_id={{row.invoice_header_id}}>{{row.invoice_number }}</td>
    <td>{{row.invoice_status_date|date:"SHORT_DATE_FORMAT"  }}</td>
            <td>{{row.invoice_status }}</td> <td>{{row.invoice_type }}</td>  <td>{{row.shipfrom_location_id }}</td>
            <td><a href={% url 'enquiry:customerdrilldown' %}?customer_id={{row.customer_id.customer_id }}>{{row.customer_id }} </td>
             <td>{{row.customer_id.customer_number }}</td>
            <td>  {% if row.order_header_id %}
                <a href={% url 'enquiry:salesordersum' %}?order_header_id={{row.order_header_id }}>{{row.order_header_id }}</a> 
                {% endif %}
                </td>
            <td>{{row.net_total }}</td>  <td>{{row.vat_total }}</td> <td>{{row.gross_total }}</td> <td>{{row.paid_amount }}</td>
            <td>{{row.balance_total }}</td>"""
    totals  = """  <td>Total</td>  <td></td>   <td></td>  <td></td>   <td></td> <td></td> <td></td>
                        <td></td>
                        <td>{{rowset_totals.net_total }}</td>
                        <td>{{rowset_totals.vat_total }}</td>
                        <td>{{rowset_totals.gross_total }}</td>
                        <td>{{rowset_totals.paid_amount }}</td>
                        <td>{{rowset_totals.balance_total }}</td>"""
    return header, columns.replace('row.', p_colcontext), totals.replace('rowset_totals.', p_footercontext)


def arinvline_grid(p_colcontext:str = 'row.', p_footercontext:str = 'rowset_totals.'):
    header = """   <th> Sl No </th>
                             <th> Inv Number </th>
                             <th> Item Number </th>
                             <th> Item Name </th>
                             <th> Tax Rate </th>
                             <th> Qty </th>
                             <th> Price </th>
                             <th> Net </th>
                             <th> Tax </th>
                             <th> Total </th>"""
    columns = """ <td>{{row2.sl_no }}</td>
    <td>{{row2.invoice_header_id.invoice_number }}</td>
    <td>{{row2.item_id.item_number}}</td>
    <td>{{row2.item_name }}</td>
    <td>{{row2.tax_rate }}</td>
    <td>{{row2.qty_invoiced_units }}</td>
    <td>{{row2.invoice_unit_sp }}</td>
    <td>{{row2.net_amount }}</td>
    <td>{{row2.tax_amount }}</td>
    <td>{{row2.total_line_amount }}</td> """
    totals  = """ <td>Totals</td>
                <td></td>
                <td></td>
                <td></td>
                <td></td>
                <td>{{rowset2_totals.qty_invoiced_units }}</td>
                <td>{{rowset2_totals.invoice_unit_sp }}</td>
                <td>{{rowset2_totals.net_amount }}</td>
                <td>{{rowset2_totals.tax_amount }}</td>
                <td>{{rowset2_totals.total_line_amount }}</td>"""
    return header, columns.replace('row.', p_colcontext), totals.replace('rowset_totals.', p_footercontext)

def customer_grid(p_colcontext:str = 'row.', p_footercontext:str = 'rowset_totals.'):
    header  = """   <th>Customer Number</th> <th>Customer Name</th> <th>First Name</th> <th>Last Name</th>
                <th>Bill Address</th> <th>Bill City</th> <th>Bill PostCode </th> <th>Ship Address</th>
                <th>Ship City</th> <th>Ship PostCode</th> <th>Phone </th>  <th>Email </th>
              <th>Date Cahnged </th>"""

    columns = """   <td> <a href={% url 'enquiry:customerdrilldown' %}?customer_number={{row.customer_number}}>{{row.customer_number}}</a>
                           {% if row.noof_orders %}
                            <a href={% url 'enquiry:salesordersum' %}?customer_id={{row.customer_id}}>Ord({{ row.noof_orders }})</a>
                            {% endif %}
                        {% if row.noof_invoices %}
                         <a href={% url 'enquiry:arinvoicesum' %}?customer_id={{row.customer_id}}>Inv({{ row.noof_invoices }})</a>
                         {% endif %}
                    </td>
            <td>{{row.customer_name }}</td> <td>{{row.contact_forename }}</td> <td>{{row.contact_lastname }}</td>
             <td>{{row.billto_address_line1 }}</td>  <td>{{row.billto_city }}</td>  <td>{{row.billto_post_code }}</td>
            <td>{{row.shipto_address_line1 }}</td> <td>{{row.shipto_city }}</td> <td>{{row.shipto_post_code }}</td>
            <td>{{row.phone1 }}</td> <td>{{row.emaill }}</td>          
            <td>{{row.last_update_date|date:"SHORT_DATE_FORMAT"  }}</td>
            """
    totals = ""
    return header, columns.replace('row.', p_colcontext), totals.replace('rowset_totals.', p_footercontext)

def arorder_grid(p_colcontext:str = 'row.', p_footercontext:str = 'rowset_totals.'):
    header = """ <th>ID</th> <th>Order Number</th> <th>Date</th>  <th>Status</th>  <th>Location</th>
                <th>Customer Name </th> <th>Customer PO </th> <th> Net </th>  <th> Vat </th> """
    columns  = """               
                <td> <a href={% url 'enquiry:salesordersum' %}?order_header_id={{row.order_header_id}}>{{row.order_header_id}}</a>  </td>
                    <td>  <a href={% url 'enquiry:salesordersum' %}?order_number={{row.order_number }}>{{row.order_number }}</a> </td>
                    <td>{{row.order_status_date|date:"SHORT_DATE_FORMAT"  }}</td>
                    <td>
                {% if row.order_status == "INVOICED" %}
                    <a href={% url 'enquiry:arinvoicesum' %}?order_header_id={{row.order_header_id}}>{{row.order_status }}</a>
                    {% else %}
                    {{row.order_status }}
                    {% endif %}
                    </td>
            <td>{{row.shipfrom_location_id }}</td>
            <td>             <a href={% url 'enquiry:customerdrilldown' %}?customer_id={{row.customer_id.customer_id }}>{{row.customer_id }} </td>
            <td>{{row.customer_po_number }}</td>
    <td>{{row.net_total }}</td>
    <td>{{row.vat_total }}</td>
            """
    totals  = """ <td>Total</td>  <td></td> <td> </td>   <td> </td> <td> </td> <td> </td> <td></td>       
                <td>{{rowset_totals.net_total }}</td>
                <td>{{rowset_totals.vat_total }}</td>"""
    return header, columns.replace('row.', p_colcontext), totals.replace('rowset_totals.', p_footercontext)


def arorderline_grid(p_colcontext:str = 'row.', p_footercontext:str = 'rowset_totals.'):
    header = """ <th>ID</th> <th>Date</th> <th>Item Number </th> <th>Item Name </th>
                    <th>Line Status </th>    <th> Qty Ordered </th> <th> Qty Picked </th>
                         <th> Price </th>  <th> Net </th>  <th> Total </th> """
    columns  = """             
               <td> <a href={% url 'enquiry:salesorderlines' %}?order_line_id={{row.order_line_id}}>{{row.order_line_id}}</a></td>
                   <td>{{row.order_line_status_date|date:"SHORT_DATE_FORMAT"  }}</td>
            <td>{{row.item_id.item_number}}</td>
            <td>{{row.item_name }}</td>
            <td>{{row.order_line_status }}</td>
            <td>{{row.qty_picked_units }}</td>
            <td>{{row.qty_userpicked_units }}</td>
            <td>{{row.order_unit_sp }}</td>
            <td>{{row.net_amount }}</td>
            <td>{{row.total_line_amount }}</td> """

    totals = """  <td>Total</td> 
                    <td></td>
                    <td> </td>
                    <td></td>
                    <td></td>        
            <td>{{rowset_totals.qty_picked_units }}</td>
            <td>{{rowset_totals.qty_userpicked_units }}</td>
            <td>{{rowset_totals.order_unit_sp }}</td>
            <td>{{rowset_totals.net_amount }}</td>
            <td>{{rowset_totals.total_line_amount }}</td></td>"""
    return header, columns.replace('row.', p_colcontext), totals.replace('rowset_totals.', p_footercontext)


def arorderpick_grid(p_colcontext: str = 'row.', p_footercontext: str = 'rowset_totals.'):
    header = """ <th> Order Line </th> <th> Status Date </th>  <th> Item Number </th> 
                                <th> Item Name </th>  <th> From Location </th> 
                                <th> From Sub Location </th>   <th> Quantity </th> 
                                <th> Status </th> 
                                """
    columns =  """ <td> <a href={% url 'enquiry:salesorderlines' %}?order_line_id={{row.order_line_id}}>{{row.order_line_id}}</a></td>
              <td> {{ row.picklist_status_date|date:"SHORT_DATE_FORMAT"   }}
            </td> <td> {{ row.item_id.item_number }} </td>
            <td> {{ row.item_id.item_name }} </td><td> {{ row.location_id.location_name }} </td>
            <td> {{ row.sub_location_id.sub_location }} </td><td> {{ row.quantity}} </td>
            <td> {{ row.picklist_status }} </td></td>
                                                """
    totals = ""
    return header, columns.replace('row.', p_colcontext), totals.replace('rowset_totals.', p_footercontext)


def commoditycode_grid(p_colcontext:str = 'row.', p_footercontext:str = 'rowset_totals.'):
    header = """ <th> Commodity Code</th><th>Item Number</th><th>Item Name</th><th>Qty Invoiced</th>
        <th>Net Total </th><th>Net Weight</th><th>Net Volume</th><th>Region Code</th>
        <th>Invoice Number</th><th>Invoice Date</th>
        <th>Country</th><th>Customer Name</th>"""
    columns  = """
                <td> {{ row.commodity_code }} </td> <td> {{ row.item_number }} </td> 
                <td> {{ row.item_name }} </td> <td> {{ row.qty_invoiced_units }} </td>
                 <td> {{ row.net_total_after_discount  }} </td>
           <td> {{ row.netweight }} </td> <td> {{ row.netvolume}} </td> <td> {{ row.country_region_code}} </td>
           <td> <a href={% url 'enquiry:arinvoicesum' %}?invoice_header_id={{row.invoice_header_id }}>{{ row.invoice_number }}</a>
            </td> <td> {{ row.invoice_status_date|date:"SHORT_DATE_FORMAT"   }} </td>
          <td> {{ row.billto_country_code }} </td> <td>
           <a href={% url 'enquiry:customerdrilldown' %}?customer_id={{row.customer_id }}>{{ row.customer_name }}   </td>
            """
    totals  = ""
    return header, columns.replace('row.', p_colcontext), totals.replace('rowset_totals.', p_footercontext)


def invreqh_grid(p_colcontext:str = 'row.', p_footercontext:str = 'rowset_totals.'):
    header = """
                <th>ID</th> <th>Number</th> <th>Requested By</th> <th>PickedBy By</th> 
                    <th>Requested On</th> <th>Picked On </th> 
                    <th>Received On</th> <th>Phase Code</th><th>Status</th>  <th>Picked Location</th> <th>Requested Location</th> 
                    <th>Batch Name</th> <th> Type</th> <th>Category</th> <th>Source</th>
                <th>Notes</th> <th>Need By</th>   
                """
    columns  = """
        <td>  <a href={% url 'enquiry:reqsum' %}?requisition_id={{row.requisition_id}}> {{ row.requisition_id }} </a> </td>
         <td> {{ row.requisition_number }} </td> <td> {{ row.requested_by_name }} </td> 
                <td> {{ row.picked_by_name }} </td> <td> {{ row.requisition_date|date:"SHORT_DATE_FORMAT"   }} </td> 
            <td> {{ row.picked_date|date:"SHORT_DATE_FORMAT"   }} </td> 
             <td> {{ row.received_date|date:"SHORT_DATE_FORMAT"   }} </td> 
            <td> {{ row.requisition_phase_code }} </td> <td> {{ row.requisition_status   }} </td>
             <td> {{ row.from_location_id }} </td> <td> {{ row.to_location_id }} </td>
             <td> {{ row.batch_name }} </td> <td> {{ row.requisition_type }} </td>
             <td> {{ row.requisition_category }} </td> <td> {{ row.requisition_source }} </td> 
             <td> {% if row.orig_sys_source == "SALESORDER" %}
                     <a href={% url 'enquiry:salesordersum' %}?order_header_id={{row.orig_sys_ref}}>  {{ row.description }} </a>   
                    {% else %}
                     {{ row.description }}
                    {% endif %}
            </td>
             <td> {{ row.need_by_date|date:"SHORT_DATE_FORMAT"   }} </td>             
            """
    totals  = ""
    return header, columns.replace('row.', p_colcontext), totals.replace('rowset_totals.', p_footercontext)


def itemsearch_grid(p_colcontext:str = 'row.', p_footercontext:str = 'rowset_totals.'):
    header  = """   <th> Number</th> <th>Name</th> <th>SAL?le</th> <th>Pur?</th> 
                <th>Val?</th> <th> Supplier</th> <th>Category </th> 
                <th>Last Bought </th>  <th>Last Sold </th>
              <th>Min </th> <th>Max </th> <th> Status </th>"""

    columns = """   <td> <a href={% url 'inventory:itemsearch' %}?item_id={{row.item_id}}>{{row.item_number}}</a>
                    </td>
            <td>{{row.item_name }}</td> <td>{{row.saleable }}</td> <td>{{row.purchaseable }}</td>
             <td>{{row.valuable }}</td>  <td>{{row.sup_supplier_id.supplier_name }}</td>  <td>{{row.iic_category_id.category_name }}</td>
             <td>{{row.item_status.last_bought_date|date:"SHORT_DATE_FORMAT"  }}</td> 
             <td>{{row.item_statuses.last_sold_date|date:"SHORT_DATE_FORMAT"  }}</td>          
            <td>{{row.min_qty  }}</td>
            <td>{{row.max_qty  }}</td> <td> {{ row.item_status }} </td>
            """
    totals = ""
    return header, columns.replace('row.', p_colcontext), totals.replace('rowset_totals.', p_footercontext)

def get_grid(p_context:str , p_colcontext:str = 'row.', p_footercontext:str = 'rowset_totals.'):
    try:
        header = mark_safe(ENQUIRY_GRIDS["{}_{}".format(p_context,'HEADER')])
        columns  = mark_safe(ENQUIRY_GRIDS["{}_{}".format(p_context,'COLUMNS')])
        footer  =  mark_safe(ENQUIRY_GRIDS["{}_{}".format(p_context,'FOOTER')])
        return header, columns.replace('row.', p_colcontext), footer.replace('rowset_totals.', p_footercontext)
    except Exception as ex:
        print(ex)
        return "", "", ""

ENQUIRY_GRIDS = {
    'DBNHEADER_HEADER' : """    
                        <th>Number</th>
                        <th>Supplier Name</th>
                        <th>Supplier Number</th>
                        <th>Date</th>
                        <th>Status</th>
                        <th>Settled by</th>
                        <th>Settled On </th>
                        <th>Location</th>
                        <th>Delivery Note</th>
                        <th>Net</th>
                        <th>Vat </th>
                        <th>Total </th>""",
    'DBNHEADER_COLUMNS': """    
       <td> <a href={% url 'enquiry:dbnotesum' %}?dbnote_number={{row.dbnote_number}}>{{row.dbnote_number}}</a></td>
            <td>{{row.sup_supplier_id.supplier_name}}</td>       
             <td>{{row.sup_supplier_id.supplier_number}}</td>       
            <td>{{row.dbnote_status_date|date:"SHORT_DATE_FORMAT"  }}</td>   
            <td>{{row.dbnote_status  }}</td>   
            <td>{{row.settled }}</td>       
            <td>{{row.dbnote_settled_on }}</td>       
            <td>{{row.shipto_location_id.location_name }}</td>
            <td>{{row.delivery_note_refe }}</td>
            <td>{{row.net_total }}</td>
            <td>{{row.vat_total }}</td>
            <td>{{row.gross_total }}</td>   """,
    'DBNHEADER_FOOTER': """
                        <td>Total</td>
                        <td></td>
                        <td></td>
                        <td></td>
                        <td></td>
                        <td></td>
                        <td></td>
                        <td></td>
                        <td></td>
                        <td>{{rowset_totals.net_total }}</td>
                        <td>{{rowset_totals.vat_total }}</td>
                        <td>{{rowset_totals.gross_total }}</td>""",
    'DBNLINE_HEADER': """<th> Sl No </th>
                                            <th> DB Number </th>
                                            <th> Item Number </th>
                                            <th> Item Name </th>
                                            <th> Qty Ord </th>
                                            <th> Qty Del </th>
                                            <th> Qty Goodsin</th>
                                            <th> Qty Inv </th>
                                            <th> Qty DbNote </th>
                                            <th> Cost  </th>
                                            <th> Invoiced </th>
                                            <th> Net </th>
                                            <th> Tax </th>
                                            <th> Total </th> """,
    'DBNLINE_COLUMNS': """ <td>{{row.sl_no }}</td>
                   <td>{{row.dbnote_id.dbnote_number }}</td>
                   <td>{{row.item_id.item_number}}</td>
                   <td>{{row.item_name }}</td>
                   <td>{{row.qty_ordered_units }}</td>
                   <td>{{row.qty_delivered_units }}</td>
                   <td>{{row.qty_received_units }}</td>
                   <td>{{row.qty_invoiced_units }}</td>
                   <td>{{row.qty_dbnote_units }}</td>
                   <td>{{row.unit_cp }}</td>
                   <td>{{row.invoiced_price }}</td>
                   <td>{{row.net_price }}</td>
                   <td>{{row.tax_price }}</td>
                   <td>{{row.total_price }}</td>  """,
    'DBNLINE_FOOTER': """ <td>Total</td>
                   <td></td>
                   <td></td>
                   <td></td>
                   <td>{{rowset_totals.qty_ordered_units }}</td>
                   <td>{{rowset_totals.qty_delivered_units }}</td>
                   <td>{{rowset_totals.qty_received_units }}</td>
                   <td>{{rowset_totals.qty_invoiced_units }}</td>
                   <td>{{rowset_totals.qty_dbnote_units }}</td>
                   <td>{{ rowset_totals.unit_cp }}</td>
                   <td>{{rowset_totals.invoiced_price }}</td>
                   <td>{{rowset_totals.net_price }}</td>
                   <td>{{rowset_totals.tax_price }}</td>
                   <td>{{rowset_totals.total_price }}</td>""",
    #-----------------------------------------------------------------
    'REQH_HEADER' : """
                <th>ID</th> <th>Number</th> <th>Requested By</th> <th>PickedBy By</th> 
                    <th>Requested On</th> <th>Picked On </th> 
                    <th>Received On</th> <th>Phase Code</th><th>Status</th>  <th>Picked Location</th> <th>Requested Location</th> 
                    <th>Batch Name</th> <th> Type</th> <th>Category</th> <th>Source</th>
                <th>Notes</th> <th>Need By</th>   
                """,
    'REQH_COLUMNS' : """
        <td>  <a href={% url 'enquiry:reqsum' %}?requisition_id={{row.requisition_id}}> {{ row.requisition_id }} </a> </td>
         <td> {{ row.requisition_number }} </td> <td> {{ row.requested_by_name }} </td> 
                <td> {{ row.picked_by_name }} </td> <td> {{ row.requisition_date|date:"SHORT_DATE_FORMAT"   }} </td> 
            <td> {{ row.picked_date|date:"SHORT_DATE_FORMAT"   }} </td> 
             <td> {{ row.received_date|date:"SHORT_DATE_FORMAT"   }} </td> 
            <td> {{ row.requisition_phase_code }} </td> <td> {{ row.requisition_status   }} </td>
             <td> {{ row.from_location_id }} </td> <td> {{ row.to_location_id }} </td>
             <td> {{ row.batch_name }} </td> <td> {{ row.requisition_type }} </td>
             <td> {{ row.requisition_category }} </td> <td> {{ row.requisition_source }} </td> 
             <td> {% if row.orig_sys_source == "SALESORDER" %}
                     <a href={% url 'enquiry:salesordersum' %}?order_header_id={{row.orig_sys_ref}}>  {{ row.description }} </a>   
                    {% else %}
                     {{ row.description }}
                    {% endif %}
            </td>
             <td> {{ row.need_by_date|date:"SHORT_DATE_FORMAT"   }} </td>             
            """,
    'REQH_FOOTER' : "",
    #----------------------------------------------------
    'REQLINE_HEADER': """<th> Sl No </th>
                                            <th> Req Number </th>
                                            <th> Item Number </th>
                                            <th> Item Name </th>
                                            <th> Qty Req </th>
                                            <th> Qty Fulfill</th>
                                            <th> Qty Received </th>
                                            <th> Qty Balance </th>
                                            <th> Need by  </th>
                                            <th> Priority </th>
                                            <th> Notes</th>
                                            <th> Status </th>""",
    'REQLINE_COLUMNS': """ <td>{{row.sl_no }}</td>
                   <td>{{row.requisition_id.requisition_number }}</td>
                   <td>{{row.item_id.item_number}}</td>
                   <td>{{row.item_id.item_name }}</td>
                   <td>{{row.qty_requested_units }}</td>
                   <td>{{row.qty_fulfilled_units }}</td>
                   <td>{{row.qty_received_units }}</td>
                   <td>{{row.qty_balance_units }}</td>
                   <td>{{row.need_by_date }}</td>
                   <td>{{row.priority_code }}</td>
                   <td>{{row.description }}</td>
                   <td>{{row.requisition_line_status }}</td>
                              """,
    'REQLINE_FOOTER': """ <td>Total</td>
                   <td></td>
                   <td></td>
                   <td></td>
                   <td>{{rowset_totals.qty_requested_units }}</td>
                   <td>{{rowset_totals.qty_fulfilled_units }}</td>
                   <td>{{rowset_totals.qty_received_units }}</td>
                   <td>{{rowset_totals.qty_balance_units }}</td>
                   <td></td>
                   <td></td>
                   <td></td>
                   <td></td>""",
    #-----------------------------------------------------------------

    # ----------------------------------------------------
    'SAGEQUERY_HEADER': """<th>ID</th> <th>Type</th> <th>Date</th>
        <th>Account Ref</th> <th>Account Code</th> <th>Net Amount </th> <th>Tax Amount</th> <th>Xchange Rate</th>
          <th> Trans Reference</th> <th>Payment Method</th> <th>Create by</th> 
          <th>Account Name</th> <th>Source</th> <th>Additional Details </th>
          """,

    'SAGEQUERY_COLUMNS': """<td> {{ row.trans_id }} </td> <td> {{ row.trans_type }} </td> 
                <td> {{ row.report_date|date:"SHORT_DATE_FORMAT"  }} </td>
                 <td> {{ row.account_ref }} </td> <td> {{ row.gl_code }} 
                </td> <td> {{ row.net_amount }} </td> <td> {{ row.tax_amount }} </td> 
                    <td> {{ row.exchange_rate }} </td> <td> {{ row.trans_reference }} </td> <td> {{ row.payment_method }} </td> 
                <td> {{ row.operatorname }} </td> <td> {{ row.account_name }} </td> 
                    <td> {{ row.trans_source }} </td> <td> {{ row.extra_reference }} </td></td>
                          """,
    'SAGEQUERY_FOOTER': """ """,

    # ----------------------------------------------------
    'SUBCAT_HEADER': """<th>Cat ID</th> <th>Category</th> <th>Sub Cat ID</th> <th>Sub Category</th> <th>Code</th> <th>BIN</th> <th>Markup</th> 
                <th>Snapshot</th> <th>Key Words</th> <th>Picture Name</th> 
                <th>Amazon %</th> <th>ebay %</th> <th>Description</th>
                 <th>Freetext1</th> <th>Freetext2 </th>
      """,

    'SUBCAT_COLUMNS': """<td>
     <a href={% url 'enquiry:itemcategory' %}?category_id={{ row.iic_category_id.category_id }}> {{ row.iic_category_id.category_id }} </a>  </td>
    <td> {{ row.iic_category_id.category_name }} </td>
     <td> <a href={% url 'enquiry:itemcategory' %}?sub_category_id={{ row.sub_category_id }} > {{ row.sub_category_id }} </a>  </td>
     <td> {{ row.sub_category_name }} </td> <td> {{ row.sub_category_code }}
      </td> <td> {{ row.bin_identifier }} </td> <td> {{ row.sub_category_markup }} </td> 
      <td> {{ row.take_snapshot }} </td> <td> {{ row.key_words }} </td> <td> {{ row.picturename }} </td>
       <td> {{ row.amazon_percent }} </td> <td> {{ row.ebay_percent }} </td> <td> {{ row.description }} </td> 
       <td> {{ row.attribute1 }} </td> <td> {{ row.attribute2 }} </td>
                      """,
    'SUBCAT_FOOTER': """ """,

    # ----------------------------------------------------
    'ITEMTRANSHIST_HEADER': """<th>Location ID</th>  <th>Date</th> 
     <th>From Sub Location</th>  <th> - Qty</th>  <th>To Sub Location</th><th>+ Qty</th>
            <th>Source</th> <th>Item Name </th> <th>Item number</th> 
          <th>Seq</th>  
            <th>Info1 </th>
            <th>Source Type</th>  <th>Info2</th>
                                            """,
    'ITEMTRANSHIST_COLUMNS': """<td> {{ row.location_name }} </td>    
                         <td> {{ row.report_date }} </td>                 
                         <td> {{ row.from_sub_location }} </td>  
                         
                         <td> {% if row.debit_quantity %}
                            {{ row.debit_quantity }}
                             {% endif %}
                             </td>
                          <td> 
                             {{ row.to_sub_location }}
                            
                              </td>  
                        <td> {% if row.credit_quantity %}
                         {{ row.credit_quantity }}
                            {% endif %} </td>
                         </td><td> {{ row.trans_source }} </td> 
                      </td><td> {{ row.item_name }} </td> 
                      <td> {{ row.item_number }}
                        <td> {{ row.trans_seq }} </td>    
                        
                       <td> {{ row.source_info1 }} </td>
          <td> {{ row.source_type }} </td> 
           <td> {{ row.source_info2 }} </td>
                  """,
    'ITEMTRANSHIST_FOOTER': """ """,

    # ----------------------------------------------------
    'ITEMINSUBLOC_HEADER': """  <th>Location</th>
                            <th>Sub Location</th>
                            <th>Quantity </th>
                            <th>Subloc Group</th>
                            <th>SubLoc Type</th>
                            <th>Item Number </th>
                            <th>Item Name </th>
                            <th>Actions </th>
                                        """,
    'ITEMINSUBLOC_COLUMNS': """ <td>{{row.location_id.location_name }}</td>
                <td>{{row.sub_location_id.sub_location }}</td>
                <td>{{row.quantity }}</td>
                <td>{{row.sub_location_id.sub_loc_group_code }}</td>
                <td>{{row.sub_location_id.sub_location_type}}</td>
                <td>{{row.item_id.item_number }}</td>
                <td>{{row.item_id.item_name }}</td>
                <td> <a href={% url 'enquiry:iteminlocation' %}?location={{ row.location_id.location_id }}>Loc Stock </a></td>
              """,
    'ITEMINSUBLOC_FOOTER': """ """,

    # ----------------------------------------------------
    'ITEMADJUST_HEADER': """  <th>Location</th>
                        <th>Sub Location</th>
                        <th>Item Number </th>
                        <th>Quantity </th>
                        <th>Date</th>
                        <th>Batch</th>
                        <th>Item Name </th>
                        <th>Reason</th>
                        <th>Adjusted By</th>
                                    """,
    'ITEMADJUST_COLUMNS': """<td> {{row.location_name}} </td> <td> {{row.sub_location_name}} </td> 
                    <td> {{row.item_number }} </td> 
                <td> {{row.qty_adjusted }} </td> 
                <td> {{ row.report_date }} </td > 
                <td> {{row.batch_name }} </td >
                <td> {{row.item_name  }} </td> 
                <td> {{row.reason_desc }} </td>
                <td> {{row.operatorname }} </td>
          """,
    'ITEMADJUST_FOOTER': """ """,

    # ----------------------------------------------------
    'MOVEMENT_HEADER': """  <th> ID </th>  
                    <th> Type </th> 
                    <th> Status </th> 
                    <th> Date </th> 
                    <th>  Item Number </th> 
                    <th>  Item Name </th> <th>From Location </th> <th>  From Sub Loc </th> <th>  Qty </th>
                    <th> To Location </th> <th> To Sub Loc </th>
                      <th> Qty GoodsIn </th> <th>  Qty Rejected</th> 
                     <th>  Batch </th> <th> Rejection Reason </th> 
                     <th>   Notes </th>
                                """,
    'MOVEMENT_COLUMNS': """ <td> 
     <a href={% url 'enquiry:itemmovements' %}?movement_id={{ row.iimh_item_movement_header_id.item_movement_header_id }}>
      {{ row.iimh_item_movement_header_id.item_movement_header_id }} </a>  
     </td>  
    <td> {{row.iimh_item_movement_header_id.movement_type }} </td> 
    <td> {{row.iimh_item_movement_header_id.header_movement_status }} </td> 
    <td> {{row.iimh_item_movement_header_id.header_movement_status_date }} </td> 
    <td> {{  row.iim_item_id.item_number }} </td> 
    <td> {{  row.iim_item_id.item_name }} </td> <td> {{  row.location_id }} </td> <td> {{  row.sub_location_id }} 
     <td> {{  row.quantity }} </td>
    </td> <td> {{  row.to_location_id }} </td> <td> {{  row.to_sub_location_id }}</td>
     <td> {{  row.qty_goodsin }} </td> <td> {{  row.qty_rejected }} </td> 
     <td> {{row.iimh_item_movement_header_id.batch_name }}  </td> <td> {{  row.reason_for_rejection }} </td> 
     <td> {{  row.notes }} </td>

      """,
    'MOVEMENT_FOOTER': """ """,
    # ----------------------------------------------------
    'STKTAKE_HEADER': """ 
                    <th> Type </th>  
                    <th> Location </th>  
                   <th> Sub Location </th> 
                   <th> Date </th> 
                   <th> Stk Take Name </th> 
                   <th>  Item Number </th> 
                   <th>  Item Name </th> 
                   <th>Was InStock </th> <th> Qty Counted </th> <th>  Qty diff </th>
                   <th> %diff </th> <th> Batch Name </th>
                     <th> Category </th> <th>  Sub Category</th> 
                    <th> Reason </th> 
                               """,
    'STKTAKE_COLUMNS': """ <td> {{ row.stktake_type  }} 
     <td> {{ row.location_name }} </td> <td> {{ row.sub_location_name }} </td> 
    <td> {{ row.report_date|date:"SHORT_DATE_FORMAT" }} </td> <td> {{ row.stktake_name }} </td>
     <td> {{ row.item_number }} </td> <td> {{ row.item_name }} </td> 
     <td> {{ row.qty_instock }} </td> <td> {{ row.qty_counted }}
      </td> <td> {{ row.diffqty }} </td> <td> {{ row.percentagediff }} </td>
       <td>  <a href={% url 'enquiry:stktakesum' %}?item_count_header_id={{ row.item_count_header_id }}>{{ row.batch_name }} </td> 
       <td> {{ row.category_name }} </td>
       <td> {{ row.sub_category_name }} </td> <td> {{ row.reason_name }} </td> 
     """,
    'STKTAKE_FOOTER': """ """,

    # ----------------------------------------------------
    'ITEMSTATUS_HEADER': """ 
                <th> Item Number</th>  
                <th> Item Name</th>  
               <th> Supplier </th> 
               <th> Category </th> 
               <th> sub Category </th> 
               <th>  InStock </th> 
               <th>  TotalSold </th> <th>  SoldY-1</th> <th>  SoldY-2</th>  <th>  SoldY-3</th>  <th>  SoldY-4</th> 
               <th>  TotalPO </th> <th>  PoY-1</th> <th>  PoY-2</th>  <th>  PoY-3</th>  <th>  PoY-4</th> 
               <th> SalYTD</th> <th> Sal This Month </th> <th> Sal Last Month </th>
               <th> Sal Last 3Month</th> <th>Sal Last 6Month </th>
                 <th> Sal Last 9Month </th> 
                           """,
    'ITEMSTATUS_COLUMNS': """ <td> {{ row.item_number }} </td> <td> {{ row.item_name }} </td> <td> {{ row.supplier_name }} 
    </td> <td> {{ row.category }} </td> <td> {{ row.subcategory }} </td>
      <td> {{ row.in_stock }} </td>  <td> {{ row.total_sold }} </td>  
     <td> {{ row.Last_year1_sales_qty }} </td> <td> {{ row.Last_year2_sales_qty }} </td> 
     <td> {{ row.Last_year3_sales_qty }} </td> <td> {{ row.Last_year4_sales_qty }} </td> 
     <td> {{ row.ytd_purchase_qty }} </td> 
     <td> {{ row.Last_year1_purchase_qty }} </td> <td> {{ row.Last_year2_purchase_qty }} </td> 
     <td> {{ row.Last_year3_purchase_qty }} </td> <td> {{ row.Last_year4_purchase_qty }} </td> 
     <td> {{ row.ytd }} </td> <td> {{ row.thismonth }} </td> <td> {{ row.lastmonth }} 
     </td> <td> {{ row.last3month }} </td> <td> {{ row.last6month }} </td> <td> {{ row.last9month }} </td>

 """,
    'ITEMSTATUS_FOOTER': """ """,
}

