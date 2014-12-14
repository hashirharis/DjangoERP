REM mysql -u root -ppassword < sql/createschema.sql
del database\br
python manage.py syncdb --noinput
python manage.py loaddata ./import-data/import/storegroup.yaml
python manage.py loaddata ./import-data/import/store.json
python manage.py loaddata ./import-data/import/productcategory.json
python manage.py loaddata ./import-data/import/brand.json
python manage.py loaddata ./import-data/import/product.json
python manage.py loaddata ./import-data/import/producttags.yaml
python manage.py loaddata ./import-data/import/postcode.json
python manage.py loaddata ./import-data/import/customer.json
python manage.py loaddata ./import-data/import/paymentmethod.yaml
python manage.py importwarranties
python manage.py initstores

SET /P ANSWER=Do you want to load testdata (Y/N)?
if /i {%ANSWER%}=={y} (goto :yes)
if /i {%ANSWER%}=={yes} (goto :yes)
exit /b 0

:yes
python manage.py loaddata ./import-data/import/testdata/terminal.json
python manage.py loaddata ./import-data/import/testdata/sale.json
python manage.py loaddata ./import-data/import/testdata/salesline.json
python manage.py loaddata ./import-data/import/testdata/saleinvoice.json
python manage.py loaddata ./import-data/import/testdata/saleinvoiceline.json
python manage.py loaddata ./import-data/import/testdata/salespayment.json
python manage.py loaddata ./import-data/import/testdata/tester.json
exit /b 0