cd atdb
python manage.py collectstatic --settings atdb.settings.dev

cd ..
xcopy atdb d:\vagrant\myATDB\repository\backend\atdb /s /e /y
xcopy atdb_services d:\vagrant\myATDB\repository\backend\atdb_services /s /e /y
rmdir d:\vagrant\myATDB\repository\backend\atdb\taskdatabase\migrations /s /q
xcopy atdb\atdb\static d:\vagrant\myATDB\repository\my_static_files /s /e /y