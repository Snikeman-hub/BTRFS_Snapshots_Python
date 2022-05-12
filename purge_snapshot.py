from btrfs_snapshots import purge_snapshot
import pickle
import sys
from datetime import datetime,timedelta
subvolume_location = sys.argv[1]
snapshot_loaction = sys.argv[2]
external_location = sys.argv[3]
frequenzy = sys.argv[4]
#today=datetime.today()
#today_print = today.strftime("%Y-%m-%d")
#today_print = "2022-05-12"
try:
        taken_snapshots = pickle.load(open( "taken_snapshots.p", "rb" ) )
        transfered_snapshots = pickle.load(open( "sent_snapshots.p", "rb" ) )
except FileNotFoundError:
        taken_snapshots = False 
        transfered_snapshots = False
print_out = purge_snapshot(subvolume_location, snapshot_loaction,external_location,taken_snapshots,transfered_snapshots,frequenzy)
try:
        taken_snapshots = print_out[2]
        transfered_snapshots = print_out[3]
        print(print_out[0])
        print(print_out[1])
        print(print_out[2])
        print(print_out[3])
        if type(taken_snapshots) == dict:
                pickle.dump(taken_snapshots, open( "taken_snapshots.p", "wb" ) )
        if type(transfered_snapshots) == dict:
                pickle.dump(transfered_snapshots, open( "sent_snapshots.p", "wb" ) )
except TypeError:
        print(print_out[1])
        pass