from django.utils.safestring import mark_safe

TABLE_TEMPLATE = 'common/table_template.html'


general_exclude_list = ['delete_flag', 'created_by', 'creation_date', 'last_update_date','last_updated_by','record_status', 'update_source']

def filter_queryset(context, getrequest, qs, field_list):
    for field in field_list:
        if getrequest.get(field):
            context['search_field_dict'][field]['value'] = getrequest.get(field)
            filt = {'{0}__icontains'.format(field): getrequest.get(field)}
            qs = qs.filter(**filt)
        print(context['search_field_dict'][field])
    return context, qs


def formfilter_queryset(getrequest, qs, field_list, show_matches=False):
    for field in field_list:
        if getrequest.get(field):
            l0=len(qs)
            model_name = qs[0]._meta.model.__name__
            if qs[0]._meta.get_field(field).get_internal_type()=='ForeignKey':

                filt = {'{0}'.format(field): getrequest.get(field)}
            else:
                filt = {'{0}__icontains'.format(field): getrequest.get(field)}
            qs = qs.filter(**filt)
            if show_matches and len(qs)>0:
                print('{0} - Filtered {1} - Count {2} -> {3}'.format(model_name, field, l0, len(qs)))
    return qs

def get_new_template(template=TABLE_TEMPLATE):
    with open(template, 'r+') as file:
        base_html = file.read()
        file.close()
    return base_html

def build_table_body(instances,field_dict,date_fields):

    # Generating Headers
    thead = ''
    for f in field_dict.keys():
        thead += '    <th> {value} </th>    '.format(value=field_dict[f])

    # Generating Rows
    tbody = ''
    for instance in instances.values():
        tr = '<tr>    '
        for f in field_dict.keys():
            if f in date_fields:
                try:
                    tr += '    <td> {value} </td>    '.format(value=instance[f].strftime('%d-%m-%Y'))
                except:
                    tr += '    <td> {value} </td>    '.format(value=instance[f])
            else:
                tr += '    <td> {value} </td>    '.format(value=instance[f])
        tr += '    </tr>\n'
        tbody += tr

    return thead,tbody


def get_table_html(model, field_dict ={},
                   filter_dict={}, ordering=(), totals_list=[]):

    # Filtering the queryset
    if filter_dict:
        qs = model.objects.filter(**filter_dict)
    else:
        qs = model.objects.all()

    # Sorting the queryset
    if ordering:
        qs = qs.order_by(*ordering)

    if not field_dict:
        field_dict = {f.get_attname_column()[0]: f.verbose_name for f in model._meta.fields}

    # Change date-time formats
    date_fields = []
    for field in model._meta.fields:
        if field.name in field_dict.keys() and field.get_internal_type()=='DateTimeField':
            date_fields.append(field.name)
    print(date_fields)
    # Start a new blank template
    output_script = get_new_template()

    # # Get the table elements

    headers, rows = build_table_body(qs, field_dict, date_fields)

    # Replace in template
    output_script = output_script.replace('__HEADER__', headers)
    output_script = output_script.replace('__ROWS__', rows)

    # Add footer if given
    footer=''
    if totals_list:
        footer = """<tr><td colspan="{COLSLEN}"><strong>TOTALS</strong></td></tr>\n<tr>    """.format(
            COLSLEN=len(qs))
        for col in field_dict.keys():
            if col in totals_list:
                total = sum(list(map(lambda x: x[col], qs.values(col))))
                footer += '<td> {0} </td>    '.format(total)
            else:
                footer += '<td> {0} </td>    '.format('')
        footer += '</tr>'

    output_script = output_script.replace('__FOOTER__', footer)

    return mark_safe(output_script)