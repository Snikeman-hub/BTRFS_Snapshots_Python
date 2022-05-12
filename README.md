# BTRFS_Snapshots_Python
Script for take,transfer,purge Snapshots for BTRFS Filesysteme with Python
all 4 Files need to be in Script Dir! Root required, no password enter for sudo implemented

usage of take_snapshot.py
python3 <subvolume_location> <snapshot_location> 

Example Entry in Crontab for a Daily Snapshot
0 23 * * * python3 /usr/local/bin/take_snapshot.py /mnt/Private-Cloud/Gallery /mnt/Private-Cloud/Gallery/.snapshots > /home/take_snapshots.log 2>&1
