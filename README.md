
# HSL Function Finder

## Overview
HSL Function Finder is a Python web application that facilitates the extraction and exploration of functions from `.hsl`, `.hs_`, and `.hsi` files in a specified directory. Built using Flask, it provides a user-friendly interface to list, search, and highlight function details from the selected files.

## Features
- **Function Extraction**: Scans `.hsl`, `.hs_`, and `.hsi` files in a directory to extract functions, arguments, return types, and file paths.
- **Web Interface**: Displays extracted functions in a searchable table format.
- **File Viewing**: Highlights the function's location in the source file, with an option to view the file and jump to the relevant line.
- **Directory Selection**: Allows users to specify the directory containing the files to process.

## Requirements
- Python 3.8 or higher
- Flask

## Installation
1. Clone or download the repository:
   ```bash
   git clone https://github.com/dcurrier/HSL-Search/Search%20HSL.git
   cd hsl-search
   ```
2. Install required Python packages:
   ```bash
   pip install flask
   ```

## Usage
1. Start the application:
   ```bash
   python Search_HSL.py
   ```
2. Open your browser and navigate to:
   ```
   http://127.0.0.1:5000/
   ```
3. Enter the directory path containing `.hsl`, `.hs_`, or `.hsi` files and click "Submit".
4. View the list of extracted functions, search for specific functions, or click a function name to view its location in the source file.

## File Descriptions
- **`Search_HSL.py`**: Main application file containing the Flask app and function extraction logic.

## Application Logic
### Key Functions
1. **`extract_functions_from_file(file_path, root_directory)`**:
   - Extracts function names, arguments, return types, and line numbers from a given file using regex.

2. **`extract_all_functions(directory)`**:
   - Iterates over files in the directory, extracting functions while resolving conflicts between `.hsl`, `.hs_`, and `.hsi` files.

3. **`create_html(all_functions)`**:
   - Generates an HTML table of the extracted functions for rendering in the web interface.

4. **Routes**:
   - `/`: Main route to input the directory and display results.
   - `/view_file`: Displays the selected file, highlighting the line containing the function.

### HTML Features
- Search box for filtering functions.
- Table displaying function name, arguments, return type, and file path.
- File viewer with auto-scrolling to highlight specific lines.

## Customization
- Modify `default_directory` in the `index` route to change the pre-filled directory path.
- Update `function_pattern` in `extract_functions_from_file` to accommodate additional syntax.

## License
This project is licensed under the MIT License.

## Contributing
Feel free to fork the repository and submit pull requests for improvements or feature additions. For major changes, please open an issue first to discuss your ideas.

---

Enjoy exploring your HSL functions!
