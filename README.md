# Katastar Data Fetcher

This Python script retrieves and processes cadastral parcel data from the Croatian Land Registry's public API. It is designed to perform searches and extract detailed information about parcels, including their ownership details.

## Features

- Searches cadastral parcels based on input criteria.
- Fetches details of cadastral parcels, such as:
    - Parcel number.
    - Address.
    - Area.
    - Ownership details (name, address, tax number, etc.).
- Logs the data into a CSV file (`cestice.csv`) for further analysis.

## How It Works

The script interacts with the Croatian Land Registry's public API (`https://oss.uredjenazemlja.hr`) to fetch cadastral data. Here are its key components:

1. **Data Fetching:**
    - The `do_get_data` function sends GET requests to the API with appropriate headers to retrieve JSON data.
    - If the API request fails, it retries up to 10 times before raising an error.

2. **Search Functions:**
    - The script provides functions (`search_puk`, `search_odjel`, `search_ko`, `search_cestica`) to query specific data, such as cadastral offices, departments, municipalities, and parcel numbers.

3. **Data Processing:**
    - Parcel details are fetched and processed, including ownership information like owner name, address, and tax number.
    - The `dump_katastar` function iterates through parcels and writes the data to a CSV file.

4. **Logging:**
    - Data is logged to a file named `cestice.csv`. If the file already exists, the script appends new data.
    - The `log` function ensures that each entry is written in a structured format.

## Prerequisites

The script requires the following Python packages:
- `requests`
- `urllib3`
- `argparse`

Ensure they are installed before running the script.

## Usage

Run the script from the command line with the required arguments:

```bash
python main.py --puk <PUK_NAME> --odjel <DEPARTMENT_NAME> --ko <MUNICIPALITY_NAME> [--max <MAX_PARCEL>] [--min <MIN_PARCEL>]
```

### Arguments:
- `--puk`: **Required**. Name of the cadastral office (e.g., `--puk=ZADAR`).
- `--odjel`: **Required**. Name of the department within the cadastral office (e.g., `--odjel=ZADAR`).
- `--ko`: **Required**. Name of the cadastral municipality (e.g., `--ko="VELI RAT"`).
- `--max`: Optional. Maximum number of parcels to fetch. Default is `10000`.
- `--min`: Optional. Minimum parcel number to start from. Default is `1`.

## Output

The script creates or updates a CSV file named `cestice.csv` with the following columns:
- Parcel number.
- Parcel address.
- Parcel area.
- Ownership share.
- Owner name.
- Owner address.
- Owner tax number.

## Example

To fetch data for parcels in the municipality `VELI RAT` within the `ZADAR` cadastral office, starting from parcel number 1 up to 50:

```bash
python main.py --puk ZADAR --odjel ZADAR --ko "VELI RAT" --max 50
```

## Key Functions

- **do_get_data:** Fetches data from the API with optional CORS headers and retries upon failure.
- **get_data:** Filters and validates data fetched from the API.
- **search_puk, search_odjel, search_ko, search_cestica:** Perform searches for cadastral offices, departments, municipalities, and parcels respectively.
- **dump_katastar:** Iterates through parcels, fetches details, and writes them to the CSV file.
- **log:** Handles logging of data to the CSV file.
- **last_non_empty_line:** Retrieves the last non-empty line from the CSV file to resume logging.
- **fix:** Cleans and formats string values for CSV writing.

## Notes

- The script retries API requests in case of failures and includes headers to mimic a browser request.
- Some API calls depend on specific parameters (e.g., `puk`, `odjel`, `ko`) being valid; incorrect values will result in errors.
- Make sure the API endpoint (`https://oss.uredjenazemlja.hr`) is accessible from your network.

## Disclaimer

This script is provided as-is and is not affiliated with or endorsed by the Croatian Land Registry. Use it responsibly and in compliance with the terms of use for the API.

## License
This project is licensed under the MIT License - see the [LICENSE](https://raw.githubusercontent.com/mstipanov/katastar-parser/refs/heads/main/LICENSE) file for details.