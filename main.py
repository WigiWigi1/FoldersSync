import shutil
import sys
import os
import logging
import argparse
from datetime import datetime
from time import sleep

# Setting up logger

logger = logging.getLogger('')
logger.setLevel(logging.DEBUG)
now = datetime.now()

# Handler for logging to the console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Handler for logging to a file
file_handler = logging.FileHandler(filename="Log" + now.strftime("%d-%m-%Y") + ".log", mode='a')
file_handler.setLevel(logging.DEBUG)

# Formatting messages
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Adding handlers
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# Function to check if folder exist and logging
def folder_exist(folder_path):
    if not os.path.isdir(folder_path):
        logging.error(f"Folder does not exist: \'{folder_path.title()}\'")
        logging.info("-----Application Finished-----")
        raise argparse.ArgumentTypeError(f"The folder path '{folder_path}' does not exist.")
    return folder_path

# Creating file path
# Note: Filepath would be created according to the OS path format
def create_file_path(directory, filename):
    return os.path.join(directory, filename)


# def get_file_list(folder):
#     return os.listdir(folder)


# Copying file from source to destination folder
def copy_file(file_name, source_folder, destination_folder):
    source_path = create_file_path(source_folder, file_name)
    destination = create_file_path(destination_folder, file_name)

# Trying to keep file attributes with copy2
    shutil.copy2(source_path, destination)
    logging.info(f'File \'{file_name}\' copied to destination folder \'{destination_folder}\'')

# Delete file
def delete_file(file_name, folder):
    file_path = create_file_path(folder, file_name)
    os.remove(file_path)
    logging.info(f'File "{file_name}" was deleted from \'{folder}\' folder')

# Delete folder
def delete_dir(folder, parent_dir):
    folder_path = os.path.join(parent_dir, folder)
    shutil.rmtree(folder_path)
    logging.info(f'Folder "{folder}" was deleted from \'{parent_dir}\' folder')

# Getting File Attributes into list
def get_file_attributes(file_name, path):
    file_attributes_list = {}

    stat_info = os.stat(create_file_path(path, file_name))

    file_attributes_list['file_name'] = file_name
    file_attributes_list['file_size'] = stat_info.st_size
    file_attributes_list['file_attributes'] = stat_info.st_mode
    file_attributes_list['file_device'] = stat_info.st_dev
    return file_attributes_list


# Main function of program
def process_folder(source_folder, target_folder):
    # Getting list of files from both folders
    master_file_list = os.listdir(source_folder)
    replica_file_list = os.listdir(target_folder)

# Checking if all files which are in Master folder are in Replica folder, if not - copy
    for file in master_file_list:
        if os.path.isfile(create_file_path(source_folder, file)):
            master_file_attributes = get_file_attributes(file, source_folder)
            try:
                target_file_attributes = get_file_attributes(file, target_folder)

            except FileNotFoundError:
                copy_file(file, source_folder, target_folder)
                target_file_attributes = get_file_attributes(file, target_folder)

            if master_file_attributes != target_file_attributes:
                copy_file(file, source_folder, target_folder)

# Creating element if it is folder and if it is not in target
        elif os.path.isdir(create_file_path(source_folder, file)):

            # Making directory if it does not exist
            if not os.path.exists(create_file_path(target_folder, file)):
                os.mkdir(create_file_path(target_folder, file))
                logging.info(f'Folder \'{file}\' has been created')

                master_path = create_file_path(source_folder, file)
                replica_path = create_file_path(target_folder, file)
                process_folder(master_path, replica_path)

            else:
                master_path = create_file_path(source_folder, file)
                replica_path = create_file_path(target_folder, file)
                process_folder(master_path, replica_path)
        else:
            pass

# Checking if there are any files/folders in target folder which do not exist in source folder, if any - delete
    for file in replica_file_list:
        if os.path.isfile(create_file_path(target_folder, file)):
            try:
                get_file_attributes(file, source_folder)
            except FileNotFoundError:
                delete_file(file, target_folder)
        if os.path.isdir(create_file_path(target_folder, file)):
            try:
                get_file_attributes(file, source_folder)
            except FileNotFoundError:
                delete_dir(file, target_folder)


# def validate_folder_path(path):
#     if not os.path.isdir(path):
#         raise argparse.ArgumentTypeError(f"The folder path '{path}' does not exist.")
#     return path

# Parsing arguments from command line using argparse external library
def parse_arguments():
    # Create the argument parser
    parser = argparse.ArgumentParser(description="Processing arguments to application, they can be -master/-m, -replica/-r "
                                                 "and -syncinterval", add_help=False)

    # Define the arguments
    parser.add_argument("-master", "-m", required=True,type=folder_exist, help="Path to the Source folder")
    parser.add_argument("-replica", "-r", required=True, type=folder_exist, help="Path to the Target folder")
    parser.add_argument("-syncinterval", "-sync", required=False, type=int, default=5,
                        help="Setting up sync interval. Is optional. Default value is 5 minutes")
    parser.add_argument('-help', '-h', action='help',default=argparse.SUPPRESS, help="HELP")

    # Parse the arguments
    try:
        args = parser.parse_args()
    except argparse.ArgumentTypeError:
        logging.info("-----Application Finished-----")
        sys.exit(2)

    # Initialize variables
    folder_master = None
    folder_replica = None

    # Check if the arguments are provided and assign the values
    if args.master:
        folder_master = args.master
        logging.info(f"Master folder set to: {folder_master}")

    if args.replica:
        folder_replica = args.replica
        logging.info(f"Replica folder set to: {folder_replica}")

    if args.syncinterval:
        syncinterval = args.syncinterval
        logging.info(f"Sync interval is set to: {syncinterval}")

    # if args.help:
    #     logging.info(f"Arguments can be used -master/-m for setting up Master folder "
    #                  "-replica/-r for setting up replica folder"
    #                  "and -sync for setting up sync interval")

    # Return the values of the folders
    return folder_master, folder_replica, syncinterval


# Block that I started to develop to fulfill the requirement of periodically synchronization through TaskManager
# But I think this is not the best approach as the application can be just dropped because of non-existing package or
# similar issue, that's why I thought not to use this approach

# def create_launch_cmd_win(period):
#     taskname = " /TN RunPythonSync "
#     py_parameters = " ".join(sys.argv)
#     time_period = " /MO " + str(period)
#     launch_line = (
#             "schtasks /Create /SC MINUTE " + time_period + taskname + "/TR " + "\" python " + py_parameters + "\"" +
#             " /ST 12:00")
#     return launch_line
#
#
# def create_launch_cmd_linux(period):
#     pwd = "ls $PWD/main.py"
#     launch_line = period + " * * * * /usr/bin/python3 " + pwd
#
#     return launch_line

# Potentially I can create bat file in order to activate venv for python and to pass there all attributes for
# application, but this is another workaround that I can guess

def main():
    while True:
        try:
            logging.info("-----Application Started-----")

            # Reading arguments from command line
            folder_master, folder_replica, sync_period = parse_arguments()

            # Doing main actions - copying, creating, deleting
            process_folder(folder_master, folder_replica)

            # Once sync completed - giving to user more details
            logging.info(
                f'Sync Completed - No more sync needed between '
                f'\'{folder_master.title()}\' and \'{folder_replica.title()}\' '
                f'folders')
            logging.info("-----Application Finished-----")

            # Using sleep method to address the sync_period
            sleep(sync_period * 60)

        except KeyboardInterrupt:
            sys.exit()

        except FileNotFoundError:
            sleep(sync_period * 60)
            pass


main()