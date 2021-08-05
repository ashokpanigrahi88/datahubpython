from django import forms
from common.models import CmnSysOptions


class SysOptionsForm(forms.ModelForm):

    class Meta:
        model = CmnSysOptions
        fields = ('consolidate_item_in_trans', 'smtp_from_address', 'smtp_domain', 'casetype', 'report_server_url',
                  'report_server_name', 'picture_type', 'picture_path', 'application_directory',
                  'country_code', 'currency_code', 'financial_year_start_date', 'ver_no', 'helpexec', 'helpfile',
                  'option_type', 'instance_name',
                  'batch_format', 'report_output_path', 'report_execution_method', 'smtp_server_name',
                  'company_logo', 'smtp_port', 'menu_color_scheme', 'enable_emailing', 'enable_notifications',
                  'sys_attribute3', 'sys_attribute2', 'sys_attribute1', 'sys_attribute4', 'sys_attribute5',
                  'dir_outbound', 'dir_inbound_backup', 'dir_tmp', 'dir_inbound', 'dir_outbound_backup',
                  'default_browser', 'back_office_url', 'licence_type', 'business_type', 'alternate_report_server',
                  'remote_report_url', 'alternate_report_url', 'install_type', 'mobile_url_homepage', 'mobile_url',
                  'db_string', 'external_mail_exe', 'smtp_password', 'smtp_user_name', 'email_bcc',
                  'email_cc', 'www_image_path', 'database_version', 'forms_version', 'enable_tparty_interface')