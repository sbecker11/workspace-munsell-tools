import re
import pandas as pd
import openpyxl
from create_js_color_chips import create_js_file

from constants import *

# read_lines_from_excel_spreadsheet
# parse the lines into pages and tables
# parse each 'Hue Name' table into V,C,R,G,B values
# output the result to a csv file
# create a javascript file that can be rendered by 
# the workspace-rolodex project


def quintext_to_quindict(quintext):
    match = re.search(r'(\d+) (\d+) (\d+) (\d+) (\d+)', quintext)
    if match:
        return {"V":int(match.group(1)), "C":int(match.group(2)), "R":int(match.group(3)), "G":int(match.group(4)), "B":int(match.group(5))}
    else:
        return None

def df_dump(df):
    df = df.sort_values(by=["Table Number", "V", "C"])
    df = df.reset_index(drop=True)
    for i, row in enumerate(df.itertuples(index=False), start=1):
        print(f'Row {i}:', row)

def parse_pages(lines):
    df_list = []
    page_dfs = []
    table_number = None
    hue = None
    author_name = None
    copyright_year = None
    page_number = None

    df = pd.DataFrame()

    for line in lines:
        if len(line.strip()) == 0:
            continue
        elif line.strip().startswith('CONVERSIONS'):
            continue
        if line.strip().startswith('CONVERSIONS'):
            continue
        elif line.strip().startswith('PAUL CENTORE'):
            continue
        elif line.strip().startswith('V C sRGB'):
            continue
        elif line.strip().startswith('Table'):
            match = re.search(r'Table (\d+): Munsell to sRGB Conversions for Hue (.+)', line)
            if match:
                table_number = int(match.group(1))
                hue = match.group(2)
                if not df.empty:
                    df['Table Number'] = table_number
                    df['Hue Name'] = hue
                    page_dfs.append(df)
                    df = pd.DataFrame()
        elif re.search(r'^c (\d+) Paul Centore (\d+)$', line) or re.search(r'^(\d+) c (\d+) Paul Centore$', line):
            match1 = re.search(r'^c (\d+) Paul Centore (\d+)$', line)
            match2 = re.search(r'^(\d+) c (\d+) Paul Centore$', line)
            if match1:
                copyright_year = int(match1.group(1))
                author_name = "Paul Centore"
                page_number = int(match1.group(2))
            elif match2:
                page_number = int(match2.group(1))
                copyright_year = int(match2.group(2))
                author_name = "Paul Centore"
            for df in page_dfs:
                # hue_name = df["Hue Name"].iloc[0]
                # if hue_name == "5.0B":
                #     df_dump(df)
                df['Author Name'] = author_name
                df['Copyright Year'] = copyright_year
                df['Page Number'] = page_number

            df_list.extend(page_dfs)
            print(f"{len(df_list)} page:{page_number}")
            page_dfs = []
        else:
            line = line.replace(',', ' ').replace('[', ' ').replace(']', ' ')
            words = line.split()
            for i in range(0, len(words), 5):
                quintext = ' '.join(words[i:i+5])
                quindict = quintext_to_quindict(quintext)
                if quindict is not None:
                    df = pd.concat([df, pd.DataFrame([quindict])])


    return df_list

def read_lines_from_excel_spreadsheet(workbook_file, sheet_name):
    # Load the workbook
    workbook = openpyxl.load_workbook(workbook_file)
    
    # Get the sheet named 'munsell2rgb'
    sheet = workbook[sheet_name]
    
    # Read the lines from the first column
    lines = [cell.value for cell in sheet['A'] if cell.value is not None]
    
    return lines

def main():
    lines = read_lines_from_excel_spreadsheet(EXCEL_FILENAME, MUNSELL2RGB_SHEET)
    
    # parse the lines into one dataframe per table
    df_list = parse_pages(lines)
    
    # Print the number of dataframes
    print(f"parsed {len(df_list)} tables")
    
    # Print the first and last rows of each dataframe
    for df in df_list:
        page_number = df['Page Number'].iloc[0]
        table_number = df['Table Number'].iloc[0]
        hue_name = df['Hue Name'].iloc[0]
        num_rows = len(df)
        print(f"Page Number: {page_number}, Table Number: {table_number}, Hue Name: {hue_name}, Number of Rows: {num_rows}")
    
    # Combine all dataframes into one for exporting to a CSV file
    final_df = pd.concat(df_list)
    
    # Sort by these columns
    final_df = final_df.sort_values(by=COLUMN_SORT_ARRAY)

    # Choose order of columns to keep
    final_df = final_df[COLUMN_KEEP_ARRAY]

    # save to local csv file
    final_df.to_csv(CSV_FILENAME, index=False)
    
if __name__ == "__main__":
    main()
    print("done")