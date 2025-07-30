import os
import csv
from datetime import datetime

def generate_timestamp():
    """
    Produces a timestamp in the form YYYY_MM-DD_hh_mm

    Returns:
        timestamp : str

    """
    return datetime.now().strftime("%Y_%m_%d_%H_%M")

def csv_filecheck(filename, path=None):
    """
    Check if a CSV file exists at a specified location.

    Parameters:
        filename (str): The name of the CSV file to check (e.g., 'data.csv').
        path (str, optional): The directory path where the file should be located.
            If None, the function defaults to the directory of the current script.

    Returns:
        bool: True if the file exists at the resolved location, False otherwise.
    """
    if path is None:
        path = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(path, filename)
    return os.path.isfile(file_path)

def csv_create(filename, header, path=None):
    """
    Create a CSV file with the given filename and header row, if it doesn't already exist.

    Parameters:
        filename (str): The name of the CSV file to create (e.g., 'data.csv').
        header (list): A list of column names to write as the header row.
        path (str, optional): The directory path where the file should be created.
            If None, defaults to the directory of the current script.

    Returns:
        str: The full path to the CSV file.
    """
    directory = path or os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(directory, filename)

    if csv_filecheck(filename, path):
        print(f"[Info] CSV file already exists: {file_path}")
        return file_path

    with open(file_path, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(header)

    print(f"[Success] CSV file created: {file_path}")
    return file_path

def csv_append_row(filename, row, path=None):
    """
    Append a single row of data to an existing CSV file.

    Parameters:
        filename (str): The name of the CSV file where the row should be appended.
        row (list): A list of values representing a single row to add to the file.
            The order and number of values should match the existing CSV header.
        path (str, optional): The directory path where the file is located.
            If None, defaults to the directory of the current script.

    Returns:
        None

    Notes:
        - If the file does not exist, this function will raise a FileNotFoundError.
        - Data is appended at the end of the file without modifying existing contents.
        - It is the caller’s responsibility to ensure the row structure matches the CSV.
    """
    directory = path or os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(directory, filename)

    with open(file_path, mode="a", newline='') as file:
        writer = csv.writer(file)
        writer.writerow(row)

def csv_append_data(filename, data, path=None):
    """
    Append multiple rows of data to an existing CSV file.

    Parameters:
        filename (str): The name of the CSV file where the data should be appended.
        data (list of list): A list of rows, where each row is a list of values.
            Each row should match the column structure of the existing CSV file.
        path (str, optional): The directory path where the file is located.
            If None, defaults to the directory of the current script.

    Returns:
        None

    Notes:
        - If the file does not exist, this function will raise a FileNotFoundError.
        - All rows in 'data' are appended in the order they appear in the list.
        - It is the caller’s responsibility to ensure each row has the correct format.
    """
    directory = path or os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(directory, filename)

    with open(file_path, mode="a", newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)

def csv_open(filename, path=None):
    """
    Open and read the contents of a CSV file, returning all rows as a list.

    Parameters:
        filename (str): The name of the CSV file to open and read.
        path (str, optional): The directory path where the file is located.
            If None, defaults to the directory of the current script.

    Returns:
        list: A list of rows from the CSV file, where each row is a list of string values.

    Notes:
        - If the file does not exist, this function will raise a FileNotFoundError.
        - The entire contents of the CSV are loaded into memory.
        - Prints the contents to the terminal row by row.
    """
    directory = path or os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(directory, filename)

    with open(file_path, mode="r", newline='') as file:
        reader = csv.reader(file)
        contents = list(reader)

    print(f"Contents of '{file_path}':")
    for row in contents:
        print(row)

    return contents

def markdown_create(functions, filename, path=None):
    """
    Writes a Markdown file containing a list of function names and their descriptions.

    Parameters:
        functions (list of tuple): List of (function_name, docstring) pairs.
        path (str): Directory where the Markdown file will be saved.
        filename (str): Name of the Markdown file (e.g., 'FUNCTIONS.md').

    Behavior:
        - Creates the directory if it doesn't exist.
        - Overwrites the file if it already exists.
    """
    os.makedirs(path, exist_ok=True)  # Create directory if it doesn't exist
    output_path = os.path.join(path, filename)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Function Reference\n\n")
        for name, doc in functions:
            f.write(f"## `{name}`\n\n")
            f.write(f"{doc.strip()}\n\n")

def data_row_exists(contents, new_row, column=0):
    """
    Check if the specified column of `new_row` matches the same column of any row in `contents`.

    Parameters:
        new_row (list): A list representing the row to check.
        contents (list of lists): The existing rows to search within, where each row is a list.
        column (int, optional): The index of the column to compare. Defaults to 0.

    Returns:
        tuple: (exists, index, matched_row)
            exists (bool): True if a matching value is found in the specified column, else False.
            index (int or None): The index of the matching row in `contents` if found, else None.
            matched_row (list or None): The matched row from `contents` if found, else None.

    Notes:
        - Matching is based on the value in the specified column.
        - Assumes `new_row` and each row in `contents` have enough columns to access the specified index.
        - Raises IndexError if `column` is out of range for any row.
    """
    key = new_row[column]
    for i, row in enumerate(contents):
        if row and row[column] == key:
            return True, i, row
    return False, None, None

def data_exact_row_exists(contents, new_row, case_sensitive=False, type_sensitive=False):
    """
    Check if a fully identical row exists in `contents`, with options for case and type sensitivity.

    Parameters:
        new_row (list): A list representing the row to check.
        contents (list of lists): The existing rows to search within, where each row is a list.
        case_sensitive (bool, optional): If True, string comparisons are case-sensitive. Defaults to False.
        type_sensitive (bool, optional): If True, type mismatches cause non-match. Defaults to False.

    Returns:
        tuple: (exists, matched_indices)
            exists (bool): True if one or more matches are found based on the given sensitivity options.
            matched_indices (list): A list of indices in `contents` where rows match `new_row` based on sensitivity.

    Notes:
        - Matching requires the same number of elements in each row.
        - If `case_sensitive` is False, string comparisons are case-insensitive.
        - If `type_sensitive` is False, values with equal string representations are considered equal.
    """


    matched_indices = [i for i, row in enumerate(contents) if data_rows_match(row, new_row, case_sensitive==case_sensitive, type_sensitive=type_sensitive)]
    exists = len(matched_indices) > 0
    return exists, matched_indices

def data_rows_match(row1, row2, case_sensitive=False, type_sensitive=False):
    """
    Compares two rows (lists, tuples, etc.) element-wise to determine if they match.

    Parameters:
        row1 (iterable): The first row to compare.
        row2 (iterable): The second row to compare.
        case_sensitive (bool): If True, string comparisons are case-sensitive.
                               If False (default), strings are compared case-insensitively.
        type_sensitive (bool): If True, values are compared with type sensitivity (e.g., 1 != "1").
                               If False (default), values are converted to strings before comparison.

    Returns:
        bool: True if the rows match element-wise according to the specified sensitivity flags,
              False otherwise.
    """
    if len(row1) != len(row2):
        return False
    for v1, v2 in zip(row1, row2):
        if type_sensitive:
            if v1 != v2:
                return False
        else:
            s1, s2 = str(v1), str(v2)
            if case_sensitive:
                if s1 != s2:
                    return False
            else:
                if s1.lower() != s2.lower():
                    return False
    return True

def data_remove_rows(contents, indices):
    """
    Remove multiple rows from contents based on a list of indices.

    Parameters:
        contents (list of lists): The CSV data as a list of rows.
        indices (list or set of int): Indices of rows to remove.

    Returns:
        list: New list with specified rows removed.

    Notes:
        - Indices that are out of range are ignored.
        - The order of remaining rows is preserved.
    """
    indices_set = set(indices)  # For faster lookup
    return [row for i, row in enumerate(contents) if i not in indices_set]



