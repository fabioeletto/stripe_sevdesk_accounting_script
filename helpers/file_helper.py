import os
import shutil

from helpers.constants import (
    ADDITIONAL_INFO_PAYOUT_FOLDER_PATH,
    ADDITIONAL_INFO_PAYOUT_FOLDER_NAME_PLACEHOLDER
)


class FileHelper:
    """Base file helper class"""
    @staticmethod
    def create_directory(path):
        """Static method to create a folder"""
        if not os.path.exists(path):
            os.makedirs(path)

    @staticmethod
    def read_from_file(path):
        """Static method to read from file (line by line)"""
        result = []
        if os.path.isfile(path):
            with open(path) as f:
                lines = f.readlines()
                for line in lines:
                    result.append(line.strip())
        return result

    @staticmethod
    def write_to_file(path, data):
        """Static method to write to file"""
        if os.path.isfile(path):
            with open(path, "a") as f:
                f.write(data)
        else:
            with open(path, "w") as f:
                f.write(data)

    @staticmethod
    def remove_recursiv_directory(path):
        """Static method to remove recursively a folder"""
        if(os.path.exists(path)):
            try:
                shutil.rmtree(path)
            except BaseException as e:
                print(f"Error while deleting {path} directory: {e}")

    @staticmethod
    def remove_file(path):
        """Static method to remove a file"""
        try:
            os.remove(path)
        except BaseException as e:
            print(f"Error while deleting {path} file: {e}")

    @staticmethod
    def create_additional_info_payout_directory(payout_name):
        path = ADDITIONAL_INFO_PAYOUT_FOLDER_PATH.replace(
            ADDITIONAL_INFO_PAYOUT_FOLDER_NAME_PLACEHOLDER,
            f"payout_{payout_name}"
        )
        FileHelper.create_directory(path)
        return path

    @staticmethod
    def create_refunds_log(refunds, payout_name):
        """Static method to create a log file of detected refunds in stripe payout"""
        path = FileHelper.create_additional_info_payout_directory(payout_name)
        if len(refunds) > 0:
            with open(
                f"{path}/refunds.txt", "w"
            ) as f:
                for refund in refunds:
                    f.write(f"{refund} \n")

    @staticmethod
    def create_other_resource_categories_log(categories, payout_name):
        """Static method to create a log file of detected other resource categories in stripe payout"""
        path = FileHelper.create_additional_info_payout_directory(payout_name)
        category_names = categories.keys()
        if len(category_names) > 0:
            for category_name in category_names:
                with open(
                    f"{path}/{category_name}.txt",
                    "w",
                ) as f:
                    for line in categories[category_name]["data"]:
                        f.write(f"{line} \n")

    @staticmethod
    def create_error_log(error_messages, payout_name):
        """Static method to create a log file of occured errors during the accounting process"""
        path = FileHelper.create_additional_info_payout_directory(payout_name)

        with open(f"{path}/errors.txt", "w") as f:
            for item in error_messages:
                f.write(f"{item} \n")
