from django.utils.safestring import mark_safe


def ecommord_grid(p_colcontext:str = 'row.', p_footercontext:str = 'rowset_totals.'):
    header = """ <th>Number</th>  <th>Date</th>  <th>Store</th>  <th>Status</th>  <th>Type</th> <th>Payment Status</th>
                <th>First Name </th> <th>Last Name </th> <th>Phone </th> <th>email </th>  
                <th>Net </th> <th>Tax</th>  <th>Gross</th>  """
    columns = """ <td>{{row.orderno }}</td>   <td>{{row.orderdate|date:"SHORT_DATE_FORMAT"  }}</td>
            <td>{{row.storename}}</td>  <td>{{row.orderstatusinfoid }}</td> <td>{{row.ordertype }}</td>
            <td>{{row.paymentstatus }}</td> <td>{{row.customerfirstname }}</td> <td>{{row.customerlastname }}</td> 
            <td>{{row.customermobileno }}</td> <td>{{row.customeremail }}</td> 
            <td>{{row.nettotalamount }}</td>
            <td>{{row.taxamount }}</td> <td>{{row.grosstotalamount }}</td>  
             """
    totals = """ <td>Total</td> <td></td>  <td></td> <td></td> <td></td> <td></td> <td> </td><td> </td><td> </td><td> </td>
                                  <td>{{rowset_totals.net_total }}</td>
                                  <td>{{rowset_totals.vat_total }}</td>
                                  <td>{{rowset_totals.gross_total }}</td>"""
    return header, columns.replace('row.', p_colcontext), totals.replace('rowset_totals.', p_footercontext)


def ecommordline_grid(p_colcontext:str = 'row.', p_footercontext:str = 'rowset_totals.'):
    header = """ <th>Sl No</th>  <th>Item Number</th>  <th>Item Name</th>  <th>Base Price</th>  <th>Unit</th> <th>Qty</th>
                <th>Sub Total</th> <th>Tax Amount</th> <th>Tax Rate</th>  """
    columns = """ <td>{{row.sewrialno }}</td>   <td>{{row.sku}}</td>
            <td>{{row.productname}}</td>  <td>{{row.productbaseprice }}</td> <td>{{row.productqtytype }}</td>
            <td>{{row.productqtystep }}</td> <td>{{row.productsubtotal }}</td> <td>{{row.producttaxamount }}</td> 
             """
    totals = """ <td>Total</td> <td></td>  <td></td> <td></td> <td></td> <td></td> <td> </td><td> </td><td> 
                                  <td>{{rowset_totals.sub_total }}</td>
                                  <td>{{rowset_totals.vat_total }}</td>"""
    return header, columns.replace('row.', p_colcontext), totals.replace('rowset_totals.', p_footercontext)