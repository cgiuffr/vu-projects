import os
import logging

username = '<your_vunet-id_here>'
password = '{prompt}' # or <your_password_here>

projects_url = 'https://stichting-vu.eu10.hanacloudservices.cloud.sap/sap/fpa/ui/app.html#/story2&/s2/60D8AD07B4DA7E8892E7E75B5F977C49/?mode=view'

storage_dir = os.path.join(os.getcwd(), 'output')
storage_dir_cleanup = True
report_zip_file = 'Projects_{username}_{date_sec}.zip' # or None (no .zip)
project_file = '{ProjectId} - Overview - {ProjectDescription}.csv' # or None (no project overviews)
personnel_file = '{ProjectId} - Personnel.csv' # or None (no personnel overviews)
expenses_file = '{ProjectId} - Expenses.csv' # or None (no expenses overviews)
force_per_project_reports = False
skip_closed_projects = True
csv_delimiter = ',' # or ';', '\t', ' ', '.', ':', '-'
log_level = logging.INFO
wait_secs = 30

upload_hostname = '<your_hostname_here>' # or None (no remote upload)
upload_ssh_port = 22
upload_username = username
upload_password = '{password}' # or {prompt} or <your_password_here>
upload_hostdir  = '<your_hostdir_here>'
