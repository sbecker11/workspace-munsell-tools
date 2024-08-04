from pathlib import Path
from hashlib import sha256
import pandas as pd

from constants import *

def create_js_file():
    js_file_path = Path(JS_FILENAME)
    
    # Check if file exists, and delete if it does
    if js_file_path.exists():
        js_file_path.unlink()

    # Create a new file
    js_file_path.touch()

def read_csv_lines():
    df = pd.read_csv(CSV_FILENAME)
    df = df.sort_values(by=COLUMN_SORT_ARRAY)

    # split into an array of lists
    lists = df.to_string(header=False,index=False,index_names=False).split('\n')

    # Adding a comma in between each value of list
    csv_lines = [','.join(ele.split()) for ele in lists]
    return csv_lines


# add a line to the js_file_path
def add_js_line(js_line):
    with open(JS_FILENAME,"a") as f:
        f.write(js_line)

# parse a csv_line to create a js_dict
def create_js_dict(csv_line):
    parts = csv_line.split(",")
    table_number = int(parts[0])
    page_hue_name = parts[1]
    value_row = int(parts[2])
    chroma_column = int(parts[3])
    r = int(parts[4])
    g = int(parts[5])
    b = int(parts[6])
    chipSize = 75
    chipMargin = 10
    max_value = 9
    y1 = (max_value - value_row)*(chipSize+chipMargin)+chipMargin
    y2 = y1 + chipSize
    x1 = (chroma_column//2-1)*(chipSize+chipMargin)+chipMargin
    x2 = x1 + chipSize
    color_key = f"{page_hue_name}-{value_row}-{chroma_column}"
    js_dict = {
        "x1": x1, "y1":y1, "x2":x2, "y2":y2,
        "table_number": table_number,
        "page_hue_name": page_hue_name, 
        "value_row": value_row, 
        "chroma_column": chroma_column,
        "color_key": color_key,
        "r": r, "g":g, "b":b 
    }
    return js_dict
    
def process_csv_lines(csv_lines):

    create_js_file()
    
    add_js_line("export const flatColorChips = [")
    
    js_lines_cnt = 0
    for csv_line in csv_lines:
        js_dict = create_js_dict(csv_line)
        js_line = "{ " + ', '.join(f"{key}: '{value}'" for key, value in js_dict.items()) + " },"
        add_js_line(js_line + "\n")
        js_lines_cnt += 1

    add_js_line("];")
    return js_lines_cnt

if __name__ == "__main__":
    csv_lines = read_csv_lines()
    print(f"csv_lines:{len(csv_lines)}")

    js_lines_cnt = process_csv_lines(csv_lines)
    print(f"js_lines:{js_lines_cnt}")
    
    print("done")
    