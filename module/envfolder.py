import os
from datetime import datetime

def create_dated_path(base_path, filename, extension="json"):
    """Create a dated folder path and ensure it exists.
    
    Args:
        base_path (str): Base directory path (e.g. 'assets/json/converted')
        filename (str): Name of the file without extension
        extension (str): File extension without dot (default: 'json')
        
    Returns:
        str: Complete file path including dated folder and file
    """
    tanggal_hari_ini = datetime.now().strftime('%Y-%m-%d')
    folder_path = f'{base_path}/{tanggal_hari_ini}'
    result_path = f'{folder_path}/{filename}.{extension}'

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        
    return result_path

def json_converted(json_file):
    """Get path for converted JSON file in assets folder."""
    return create_dated_path('assets/json/converted', json_file)
    
def read_json(json_file):
    """Get path for reading JSON file from assets folder."""
    return create_dated_path('assets/json/converted', json_file)

def write_json_data_bot(report_filename):
    """Get path for bot data JSON file in reports folder."""
    return create_dated_path('report/json', report_filename)

def write_json_data_summary(report_filename):
    """Get path for summary JSON file in reports folder."""
    return create_dated_path('report/json', report_filename)

def write_json_chart(report_filename):
    """Get path for chart JSON file in reports folder."""
    return create_dated_path('report/json', report_filename)

def calculate(report_filename):
    """Get path for calculation results JSON file in reports folder."""
    return create_dated_path('report/json', report_filename)

def log(report_filename, id_test):
    """Get path for log file with test ID."""
    return create_dated_path('log', f'{report_filename}-{id_test}', 'log')
    
def report_html(report_filename):
    """Get path for HTML report file."""
    return create_dated_path('report/html', report_filename, 'html')

def report_screenshoot(id_test):
    """Get path for screenshot directory with test ID.
    
    Creates both the date-based folder and a subfolder for the specific test.
    """
    tanggal_hari_ini = datetime.now().strftime('%Y-%m-%d')
    folder_path = f'report/screenshoot/{tanggal_hari_ini}'
    result_path = f'{folder_path}/{id_test}'
    
    for path in [folder_path, result_path]:
        if not os.path.exists(path):
            os.makedirs(path)
    
    return result_path