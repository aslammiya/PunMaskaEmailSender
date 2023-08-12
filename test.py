import gspread

recipients = []
try:
    # Fetch recipients from the Google Sheet (public sheet)
    client = gspread.authorize(None)  # No credentials needed for public sheets
    # Replace the following URL with the URL of your Google Sheets document
    test_sheet_url = 'https://docs.google.com/spreadsheets/d/1ZEt8gCD3cYuMeJJGKky1itiXBTpBBp-oi-W6QDaJpFg/edit?usp=sharing'
    print(f'Opening Google Sheet: {test_sheet_url}')
    sheet = client.open_by_url(test_sheet_url)
    if sheet is None:
        print('Failed to open the sheet.')
    else:
        worksheet = sheet.get_worksheet(0)
        values = worksheet.get_all_records()
        print(f'Number of rows in the sheet: {len(values)}')
        for row in values:
            name = f" {row['Name'].strip()}"
            print(name)
            email = row['Email'].strip()
            print(email)
            recipients.append((name, email))
except gspread.exceptions.APIError as api_error:
    print(f'An API error occurred while reading the Google Sheet: {api_error}')
except Exception as e:
    print(f'An error occurred while reading the Google Sheet: {e}')
print('Recipients:', recipients)
