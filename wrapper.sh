while true; do timeout 601 python3 -u uploader.py | tee -a out; sleep 10; done
