#!/bin/sh

# data_monitor looks for new tasks and dataproducts in the specified dir and adds them to ATDB
python atdb_service.py -o data_monitor --dir ~/my_datawriter --interval 30 --alta_host acc --user atdb --password V5Q3ZPnxm3uj &

# start_ingest looks for 'valid' tasks and then starts the ingest to ALTA.
python atdb_service.py -o start_ingest --interval 30 --alta_host acc --user atdb --password V5Q3ZPnxm3uj -v &

# ingest_monitor looks if 'ingesting' tasks and dataproducts have arrived in ALTA, and when found sets their status in ATDB to 'archived'
python atdb_service.py -o ingest_monitor --interval 30 --alta_host acc --user atdb --password V5Q3ZPnxm3uj -v &

# python atdb_service.py -o delete_taskid --taskid 180223003_IMG --atdb_host test --alta_host acc