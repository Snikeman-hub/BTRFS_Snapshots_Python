from btrfs_snapshots import take_snapshot
import pickle
import sys
from datetime import datetime,timedelta
subvolume_location = sys.argv[1]
snapshot_loaction = sys.argv[2]
#external_location = sys.argv[3]
#frequenzy = sys.argv[4]
try:
        taken_snapshots = pickle.load(open( "taken_snapshots.p", "rb" ) )
except FileNotFoundError:
        taken_snapshots = False
print_out = take_snapshot(subvolume_location,snapshot_loaction,taken_snapshots)
try:
        taken_snapshots = print_out[1]
        print(type(taken_snapshots))
        print(print_out[0])
        print(print_out[1])
        if type(taken_snapshots) == dict:
                pickle.dump(taken_snapshots, open( "taken_snapshots.p", "wb" ) )
        else:
                pass
except TypeError:
        print(print_out[1])
        pass