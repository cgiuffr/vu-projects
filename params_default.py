import os
import logging

#
# Example record for report file formatting:
# {"Guid":"5A5D41DBFFA00A20E100800091640C0F","ProjectId":"R/003633","ProjectDescription":"REACT - Giuffrida"}

username = '<your_vunet-id_here>'
password = '<your_password_here>'

projects_url = 'https://api.vuweb.vu.nl/api/projectdetails/projects/'
reports_url = 'https://api.vuweb.vu.nl/api/projectdetails/reports/'

storage_dir = os.path.join(os.getcwd(), 'output')
storage_dir_cleanup = True
report_file = '{ProjectId} - {ProjectDescription}.xlsm'
report_zip_file = 'Projects_{username}_{date_sec}.zip'
log_level = logging.INFO

upload_hostname = '<your_hostname_here>' # or None for no remote upload
upload_ssh_port = 22
upload_username = username
upload_password = password
upload_hostdir  = '<your_hostdir_here>'
