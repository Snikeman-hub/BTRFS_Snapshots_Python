import os
import subprocess
import sys
import pickle
from datetime import datetime,timedelta
subvolume_location = sys.argv[1]
snapshot_loaction = sys.argv[2]
external_location = sys.argv[3]
frequenzy = sys.argv[4]
today=datetime.today()
today_print = today.strftime("%Y-%m-%d")
today_print = "2021-05-14"
wochentag = int(today.strftime("%w")) #Formatierung des Wochentages in eine Zahl fuer die If uebperuefung

#sudo btrfs subvolume snapshot /mnt/Private-Cloud/Dokumente /mnt/Private-Cloud/.snapshots/Dokumente_2022-05-10
snapshot_name = str
try:
        taken_snapshots = pickle.load(open( "taken_snapshots.p", "rb" ) )
        transfered_snapshots = pickle.load(open( "sent_snapshots.p", "rb" ) )
except FileNotFoundError:
        taken_snapshots = None 
        transfered_snapshots = None
def get_snapshot_name(source_subvolume):
        snapshot_tag = source_subvolume.split("/")
        while len(snapshot_tag) > 1:
                for entry in snapshot_tag:
                        if len(snapshot_tag) > 1:
                                snapshot_tag.pop(0)
                        else:
                                pass
        snapshot_tag = str(snapshot_tag).strip("[]'")
        snapshot_name =  str
        snapshot_name = "%s_%s" %(snapshot_tag,today_print)
        return snapshot_name, snapshot_tag, today_print

def take_snapshot(source_subvolume, destination_subvolume,):
        snapshot_name = get_snapshot_name(source_subvolume)[0]
        snapshot_tag = get_snapshot_name(source_subvolume)[1]
        snapshot_date = get_snapshot_name(source_subvolume)[2]
        take_snapshot_command = "sudo btrfs subvolume snapshot -r %s %s/%s" %(source_subvolume,destination_subvolume,snapshot_name)
        global taken_snapshots
        if taken_snapshots == None:
                taken_snapshots = {snapshot_tag:[snapshot_date]}
        elif snapshot_tag not in taken_snapshots:
                taken_snapshots = {snapshot_tag:[snapshot_date]}
        elif snapshot_date not in taken_snapshots[snapshot_tag]:
                taken_snapshots[snapshot_tag].append(snapshot_date)
        else:
                print("Snapshot '%s' already exists" %(snapshot_name))
                return False
        take_command = subprocess.run(['echo',take_snapshot_command], stdout = subprocess.PIPE,universal_newlines=True)
        take_command
        return take_command.stdout, taken_snapshots

def transfer_snapshot(source_subvolume, destination_subvolume,external_subvolume):
        # sudo btrfs send -p \
        # /mnt/Private-Cloud/.snapshots/Dokumente_2022-05-10\
        # /mnt/Private-Cloud/.snapshots/Dokumente_2022-05-10 | 
        # btrfs receive /mnt/Backup-Server/Private-Cloud/Dokumente
        snapshot_name = get_snapshot_name(source_subvolume)[0]
        snapshot_tag = get_snapshot_name(source_subvolume)[1]
        snapshot_date = get_snapshot_name(source_subvolume)[2]
        newest_snapshot_date = taken_snapshots[snapshot_tag][(len(taken_snapshots[snapshot_tag])-1)]
        newest_snapshot = "%s_%s" %(snapshot_tag,newest_snapshot_date)
        global transfered_snapshots
        if transfered_snapshots == None:
                transfered_snapshots = {snapshot_tag:[snapshot_date]}
        elif snapshot_tag not in transfered_snapshots:
                transfered_snapshots = {snapshot_tag:[snapshot_date]}
        elif snapshot_date not in transfered_snapshots[snapshot_tag]:
                transfered_snapshots[snapshot_tag].append(snapshot_date)
        else:
                print("Snapshot already on External Device")
                return False
        if len(taken_snapshots[snapshot_tag]) > 1:
                previous_snapshot_date = taken_snapshots[snapshot_tag][(len(taken_snapshots[snapshot_tag])-2)]
                previous_snapshot = "%s_%s" %(snapshot_tag,previous_snapshot_date)
                transfer_snapshot_command = "\
sudo btrfs send -p\ \n \
{subvolume}/{parental}\ \n \
{subvolume}/{newest}\ \n \
|btrfs receive {external_path}" \
.format(subvolume=destination_subvolume,parental=previous_snapshot,newest=newest_snapshot,external_path=external_subvolume)
                transfer_command = subprocess.run(['echo',transfer_snapshot_command], stdout = subprocess.PIPE,universal_newlines=True)
                transfer_command
                return transfer_command.stdout, transfered_snapshots
        else:
                transfer_snapshot_command = "sudo btrfs send {subvolume}/{snapshot} | btrfs receive {external_path}"\
                .format(subvolume=destination_subvolume,snapshot=newest_snapshot,external_path=external_subvolume)
                transfer_command = subprocess.run(['echo',transfer_snapshot_command], stdout = subprocess.PIPE,universal_newlines=True)
                transfer_command
                return transfer_command.stdout, transfered_snapshots

def purge_snapshot(source_subvolume, destination_subvolume,external_subvolume, frequenzy):
        snapshot_name = get_snapshot_name(source_subvolume)[0]
        snapshot_tag = get_snapshot_name(source_subvolume)[1]
        snapshot_date = get_snapshot_name(source_subvolume)[2]
        if frequenzy == "Daily":
                if len(taken_snapshots[snapshot_tag]) > 7:
                        calculate_oldest_snapshot = datetime.today() - timedelta(days=7)
                        oldest_snapshot = "%s_%s" %(snapshot_tag,calculate_oldest_snapshot.strftime("%Y-%m-%d"))
                        if calculate_oldest_snapshot.strftime("%Y-%m-%d") in taken_snapshots[snapshot_tag]:
                                purge_oldest_on_host = "sudo btrfs subvolume delete {destination}/{snapshot}".format(destination=destination_subvolume,snapshot=oldest_snapshot)
                                purge_oldest_on_external = "sudo btrfs subvolume delete {destination}/{snapshot}".format(destination=external_subvolume,snapshot=oldest_snapshot)
                                purge_on_host_command = subprocess.run(['echo',purge_oldest_on_host], stdout = subprocess.PIPE,universal_newlines=True)
                                purge_on_host_command
                                purge_on_external_command = subprocess.run(['echo',purge_oldest_on_external], stdout = subprocess.PIPE,universal_newlines=True)
                                purge_on_external_command
                                taken_snapshots[snapshot_tag].remove(calculate_oldest_snapshot.strftime("%Y-%m-%d"))
                                transfered_snapshots[snapshot_tag].remove(calculate_oldest_snapshot.strftime("%Y-%m-%d"))
                                return purge_on_host_command.stdout, purge_on_external_command.stdout, taken_snapshots, transfered_snapshots
                        else:
                                return False
                else:
                        return False
        elif frequenzy == "Weekly":
                if len(taken_snapshots[snapshot_tag]) > 4:
                        calculate_oldest_snapshot = datetime.today() - timedelta(days=28)
                        oldest_snapshot = "%s_%s" %(snapshot_tag,calculate_oldest_snapshot.strftime("%Y-%m-%d"))
                        if calculate_oldest_snapshot.strftime("%Y-%m-%d") in taken_snapshots[snapshot_tag]:
                        #keep last 7 Snapshots from today on
                        #calculate_latest_snapshot = datetime.today() - timedelta(days=0) #Berechne die Endzeit des Befehls, im Prinzip kommt hier Gestern als Datum heraus, bzw. Sonntag.
                        #Berechne die Startzeit des Befehls, im Prinzip kommt hier der Montag vor einer Woche als Datum heraus.
                                purge_oldest_on_host = "sudo btrfs subvolume delete {destination}/{snapshot}".format(destination=destination_subvolume,snapshot=oldest_snapshot)
                                purge_oldest_on_external = "sudo btrfs subvolume delete {destination}/{snapshot}".format(destination=external_subvolume,snapshot=oldest_snapshot)
                                purge_on_host_command = subprocess.run(['echo',purge_oldest_on_host], stdout = subprocess.PIPE,universal_newlines=True)
                                purge_on_host_command
                                purge_on_external_command = subprocess.run(['echo',purge_oldest_on_external], stdout = subprocess.PIPE,universal_newlines=True)
                                purge_on_external_command
                                taken_snapshots[snapshot_tag].remove(calculate_oldest_snapshot.strftime("%Y-%m-%d"))
                                transfered_snapshots[snapshot_tag].remove(calculate_oldest_snapshot.strftime("%Y-%m-%d"))
                                return purge_on_host_command.stdout, purge_on_external_command.stdout, taken_snapshots, transfered_snapshots
                        else:
                                return False
                else:
                        return False
        elif frequenzy == "Monthly":
                if len(taken_snapshots[snapshot_tag]) > 12:
                        calculate_oldest_snapshot = datetime.today() - timedelta(days=365)
                        oldest_snapshot = "%s_%s" %(snapshot_tag,calculate_oldest_snapshot.strftime("%Y-%m-%d"))
                        if calculate_oldest_snapshot.strftime("%Y-%m-%d") in taken_snapshots[snapshot_tag]:
                                purge_oldest_on_host = "sudo btrfs subvolume delete {destination}/{snapshot}".format(destination=destination_subvolume,snapshot=oldest_snapshot)
                                purge_oldest_on_external = "sudo btrfs subvolume delete {destination}/{snapshot}".format(destination=external_subvolume,snapshot=oldest_snapshot)
                                purge_on_host_command = subprocess.run(['echo',purge_oldest_on_host], stdout = subprocess.PIPE,universal_newlines=True)
                                purge_on_host_command
                                purge_on_external_command = subprocess.run(['echo',purge_oldest_on_external], stdout = subprocess.PIPE,universal_newlines=True)
                                purge_on_external_command
                                taken_snapshots[snapshot_tag].remove(calculate_oldest_snapshot.strftime("%Y-%m-%d"))
                                transfered_snapshots[snapshot_tag].remove(calculate_oldest_snapshot.strftime("%Y-%m-%d"))
                                return purge_on_host_command.stdout, purge_on_external_command.stdout, taken_snapshots, transfered_snapshots
                        return False
                else:
                        return False

#print_out = take_snapshot(subvolume_location, snapshot_loaction)
#print(print_out)
#transfer_snapshot(subvolume_location,snapshot_loaction,external_location)

#pickle.dump(taken_snapshots, open( "taken_snapshots.p", "wb" ) )
#pickle.dump(transfered_snapshots, open( "sent_snapshots.p", "wb" ) )

#print('DEBUG: Created Snapshots - ',taken_snapshots)
#print('DEBUG: Sent Snapshots - ',transfered_snapshots)

#purge_snapshot(subvolume_location,snapshot_loaction,external_location,frequenzy)

#print('DEBUG: Created Snapshots - ',taken_snapshots)
#print('DEBUG: Sent Snapshots - ',transfered_snapshots)