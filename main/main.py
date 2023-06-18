import os
from pathlib import Path
import hashlib
import PySimpleGUI as sg
from send2trash import send2trash

def psg_setup():
    # Primary window used to select directory to be scanned for duplicate files
    layout = [
        [sg.Text('Select a folder to scan')],
        [sg.FolderBrowse(target='selected_folder')],
        [sg.Input(key='selected_folder')],
        [sg.Button('Scan'), sg.Button('Cancel')]
    ]
    
    window = sg.Window('File Deduplicator', layout, grab_anywhere=True)
    
    return window


def psg_scan_progress(file_num):
    # Simple progress bar to monitor scan progress
    layout = [
        [sg.Text('Scanning...')],
        [sg.ProgressBar(max_value=file_num, orientation='h', size=(20,20), key='-PBAR-')]
    ]
    
    window = sg.Window('Scan Progress', layout, grab_anywhere=True)
    
    return window


def psg_confirm(total_files):
    # Report how many duplicates have been found and removed
    layout = [
        [sg.Text(f'{total_files} files have been moved to the trash.')],
        [sg.Button('Confirm')]
    ]
    
    window = sg.Window('Duplicates Deleted', layout, grab_anywhere=True)
    
    return window


def hash_file(path):
    with open(path, 'rb') as f:
        hasher = hashlib.md5()
        blocksize = 65536
        buffer = f.read(blocksize)
        
        while len(buffer) > 0:
            hasher.update(buffer)
            buffer = f.read(blocksize)
    
        return hasher.hexdigest()


def main():
    window = psg_setup()
    while True:
        event, values = window.read()
        if event in (None, 'Cancel'):
            print(event, values)
            window.close()
            break
        
        if event in ('Scan'):
            # Gather the contents of our target folder
            file_lst = os.walk(values['selected_folder'])
            
            # Setup values for our progress bar
            scan_prog, total = 0, len(os.listdir(values['selected_folder']))
            
            # Setup our progress bar window
            prog_window = psg_scan_progress(total)
            progress_bar = prog_window['-PBAR-']

            unique_files = {}
            dupe_files = []
            
            # Loop over our target directory and resident files
            for root, _, files in file_lst:
                prog_window.read(timeout=0)  # Establish and update our progress bar

                for file in files:
                    # Update progress bar for each file
                    scan_prog += 1
                    progress_bar.update_bar(scan_prog, total)
                    
                    # Get the full file path and hash the file accordingly
                    file_path = Path(os.path.join(root, file))
                    file_hash = hash_file(file_path)
                    
                    # Add unique files to our unique_files Dict
                    # As duplicate files are encountered, add them to the dupe_file List
                    if file_hash not in unique_files:
                        unique_files[file_hash] = file_path
                    else:
                        dupe_files.append(file_path)
                        print(f"{file_path} appears to be a duplicate.")    
                        send2trash(file_path)
            
                prog_window.close()  # Close the progress bar window
            
            # Report how many files have been removed
            confirm_window = psg_confirm(len(dupe_files))
            event_conf, _ = confirm_window.read()
            
            if event_conf in ('Confirm'):
                confirm_window.close()


if __name__ == '__main__':
    main()