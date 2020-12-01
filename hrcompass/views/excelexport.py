################################################
#
# These view is for the excel export
#
################################################

from hrcompass.models import Client, Task, Status, Kind, AuthUser
from django_otp.decorators import otp_required
import datetime
import io
import xlsxwriter
from django.http import HttpResponse


@otp_required
def writetoexcel(task_data, client=None):
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet_s = workbook.add_worksheet("Summary")

    # excel styles
    title = workbook.add_format({
        'bold': True,
        'font_size': 14,
        'align': 'center',
        'valign': 'vcenter'
    })
    header = workbook.add_format({
        'bg_color': '#F7F7F7',
        'color': 'black',
        'align': 'center',
        'valign': 'top',
        'border': 1
    })
    cell = workbook.add_format({
        'align': 'left',
        'valign': 'top',
        'text_wrap': True,
        'border': 1
    })
    cell_center = workbook.add_format({
        'align': 'center',
        'valign': 'top',
        'border': 1
    })
    format = workbook.add_format({
        'num_format': 'd-m-yyyy',
        'border': 1
        })
    # write title
    today = datetime.datetime.now()
    format_date = today.strftime("%d-%m-%Y %H:%M:%S")
    title_text = u"{0} {1}".format("Task overview", format_date)
    # merge cells
    worksheet_s.merge_range('B2:J2', title_text, title)

    '''
    # write header
    worksheet_s.write(4, 0, "Client Name", header)
    worksheet_s.write(4, 1, "Project Number", header)
    worksheet_s.write(4, 2, "Task", header)
    worksheet_s.write(4, 3, "Invoiced", header)
    worksheet_s.write(4, 4, "Startdate", header)
    worksheet_s.write(4, 5, "Duedate", header)
    worksheet_s.write(4, 6, "Status", header)
    worksheet_s.write(4, 7, "Kind", header)
    worksheet_s.write(4, 8, "Employee", header)
    '''

    # column widths
    description_col_width = 10
    observations_col_width = 25

    # add data to the table
    client = Client.objects.all()
    status = Status.objects.all()
    users = AuthUser.objects.all()
    kinds = Kind.objects.all()
    tasks = Task.objects.select_related('client', 'task_status', 'task_name').prefetch_related('members')
    i = 1
    for task in tasks:
        row = 4 + i
        invoiced_full = task.invoiced
        if invoiced_full is not None:
            invoiced = invoiced_full.strftime("%d-%m-%Y")
        else:
            invoiced = ""
        startdate_full = task.startdate
        if startdate_full is not None:
            startdate = startdate_full.strftime("%d-%m-%Y")
        else:
            startdate = ""
        duedate_full = task.duedate
        if duedate_full is not None:
            duedate = duedate_full.strftime("%d-%m-%Y")
        else:
            duedate = ""
        worksheet_s.write_string(row, 1, task.client.client_name, cell)
        worksheet_s.write_string(row, 2, task.client.project_number, cell)
        worksheet_s.write_string(row, 3, task.task_name.name, cell)
        
        worksheet_s.write(row, 4, invoiced, format)
        worksheet_s.write(row, 5, startdate, format)
        worksheet_s.write(row, 6, duedate, format)
        worksheet_s.write_string(row, 7, task.task_status.status, cell)
        worksheet_s.write_string(row, 8, task.task_name.task_kind.kind, cell)
        for person in task.members.all():
            worksheet_s.write_string(row, 9, person.username, cell)
        i = i + 1
    #add table
    worksheet_s.add_table('B5:J' + str(i+4), {'columns':[{'header': 'Client Name'},
                                                {'header': 'Project Number'},
                                                {'header': 'Task'},
                                                {'header': 'Invoiced'},
                                                {'header': 'Startdate'},
                                                {'header': 'Duedate'},
                                                {'header': 'Status'},
                                                {'header': 'Kind'},
                                                {'header': 'Employee'},]})
    # Change column width
    worksheet_s.set_column('B:B', 22) # Client Name column
    worksheet_s.set_column('C:C', 16) # project Number column
    worksheet_s.set_column('D:D', 30) # Task Name column
    worksheet_s.set_column('E:E', 11) # Invoiced column
    worksheet_s.set_column('F:F', 11) # Startdate column
    worksheet_s.set_column('G:G', 11) # Duedate column
    worksheet_s.set_column('H:H', 16) # Task Status column
    worksheet_s.set_column('J:I', 9) # Task Kind column
    worksheet_s.set_column('J:J', 11) # Employee column

    # Charts
    worksheet_c = workbook.add_worksheet("Charts")
    worksheet_d = workbook.add_worksheet("Chart Data")
    bar_chart = workbook.add_chart({'type': 'column'})
    bar_chart.add_series({
        'name': 'Tasks',
        'values': '=Chart Data!${0}${1}:${0}${2}'.format(chr(ord('A') + 1+ 1), 1, 1),
        'categories': '=Chart Data!${0}${1}:${0}${2}'.format(chr(ord('A') + 1), 1, 1),
        'data_labels': {'value': True, 'num_format': u'#0 "km/h"'}
    })
    bar_chart.set_title({'name': "Progress Bar"})

    worksheet_c.insert_chart('B20', bar_chart, {'x_scale': 1, 'y_scale': 1})

    # Rewind the buffer.
    workbook.close()
    output.seek(0)

    # Set up the Http response.
    filename = 'Hrcompass_data.xlsx'
    response = HttpResponse(
        output,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=%s' % filename
    
    return response