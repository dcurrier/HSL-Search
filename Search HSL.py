from flask import Flask, render_template_string, request
import os
from pathlib import Path
import re
import subprocess
import platform

# Function to extract function names and return types from .hsl/.hs_/.hsi files
def extract_functions_from_file(file_path, root_directory, help_file):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        content = file.read()

    # Updated Regex pattern for functions with named capture groups (name, args, returns)
    function_pattern = r"^\s*function\s+(?P<name>\w+)\s*\((?P<args>.*)\)\s*(?P<returns>\w*)\s*[\n\r]{"
    matches = re.finditer(function_pattern, content, re.MULTILINE)

    # Collecting function details
    functions = []
    relative_file_path = os.path.relpath(file_path, root_directory)  # Get relative file path
    for match in matches:
        # Find the line number of the match in the original file content
        start_pos = match.start()
        line_number = content[:start_pos].count('\n') + 1

        function_name = match.group('name')
        return_type = match.group('returns')
        function_args = match.group('args')
        functions.append({
            "function_name": function_name,
            "arguments": function_args,
            "return_type": return_type,
            "file_path": relative_file_path,
            "full_file_path": file_path,
            "help_file_path": help_file,
            "line_number": line_number
        })
    
    return functions

def extract_all_functions(directory):
    all_functions = {}

    for root, _, files in os.walk(directory):
        for file in files:
            file_path = Path(root) / file
            dir_path = Path(file_path).parent

            # Exclude files that start with "~"
            if file.startswith("~"):
                continue

            file_ext = file_path.suffix
            stem = file_path.stem

            # Collect functions from .hsl, .hs_, .hsi files
            if file_ext in ['.hsl', '.hsi']:
                if file_ext == ".hsl":
                    hs_path = file_path.with_suffix(".hs_")
                    extraction_file_path = hs_path if hs_path.exists() else file_path
                else:
                    extraction_file_path = file_path

                # Look for a help file with the same stem
                help_file_path = None
                for chm in dir_path.glob(f"{stem}*.chm"):
                    help_file_path = chm
                    break  # just use the first matching one

                functions = extract_functions_from_file(extraction_file_path, directory, help_file_path)

                # Add the functions if the stem doesn't exist yet or the list is empty
                all_functions[stem] = functions
                
    
    # Flatten the dictionary to a list of functions
    flat_function_list = [func for func_list in all_functions.values() for func in func_list]
   
    return flat_function_list

def create_html(all_functions):
    html_template = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Function Search</title>
        <style>
            body {
                font-family: Arial, sans-serif;
            }
            table {
                width: 100%;
                border-collapse: collapse;
            }
            th, td {
                text-align: left;
                padding: 8px;
            }
            th {
                background-color: #f2f2f2;
            }
            tr {
                border-bottom: 1px solid #ddd;
            }
            tr:nth-child(even) {
                background-color: #f9f9f9;
            }
            tr:nth-child(odd) {
                background-color: #ffffff;
            }
            input {
                margin-bottom: 12px;
                padding: 8px;
                width: 100%;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
        </style>
    </head>
    <body>
        <h1>Function Search</h1>
        <input type="text" id="searchInput" onkeyup="searchFunction()" placeholder="Search for functions..">
        <table>
            <thead>
                <tr>
                    <th>Function Name</th>
                    <th>Arguments</th>
                    <th>Return Type</th>
                    <th>File Path</th>
                    <th>Help File</th>
                </tr>
            </thead>
            <tbody id="functionList">
            {% for func in functions %}
                <tr>
                    <td><a href="/view_file?file_path={{ func.full_file_path }}&line_number={{ func.line_number }}" target="_blank">
                        <strong>{{ func.function_name }}</strong>
                    </a></td>
                    <td>{{ func.arguments }}</td>
                    <td>{{ func.return_type }}</td>
                    <td>{{ func.file_path }}</td>
                    <td>{% if func.help_file_path %} <a href="/open_help?file={{ func.help_file_path }}" target="_blank">Open Help</a>
                        {% else %}
                            N/A
                        {% endif %}
                    </td>
                </tr>
            {% endfor %}
            </tbody>
        </table>

        <script>
        function searchFunction() {
            var input, filter, table, tr, td, i, txtValue;
            input = document.getElementById("searchInput");
            filter = input.value.toUpperCase();
            table = document.getElementById("functionList");
            tr = table.getElementsByTagName("tr");
            for (i = 0; i < tr.length; i++) {
                td = tr[i].getElementsByTagName("td")[0];
                if (td) {
                    txtValue = td.textContent || td.innerText;
                    if (txtValue.toUpperCase().indexOf(filter) > -1) {
                        tr[i].style.display = "";
                    } else {
                        tr[i].style.display = "none";
                    }
                }       
            }
        }
        </script>
    </body>
    </html>
    '''
    
    # Generate and return the HTML content
    return render_template_string(html_template, functions=all_functions)


# Flask web app to serve the HTML file
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    default_directory = r"C:\\Program Files (x86)\\Hamilton\\Library"
    directory = default_directory
    all_functions = None
    
    if request.method == 'POST':
        directory = request.form['directory']
        
        # Validate if the directory exists
        if not os.path.isdir(directory):
            return '''
            <html>
                <body>
                    <h1>Error</h1>
                    <p>Invalid directory! Please enter a valid directory path.</p>
                    <a href="/">Go Back</a>
                </body>
            </html>
            '''
        
        # Extract all functions using the user-provided directory
        all_functions = extract_all_functions(directory)

    # Display the HTML with the results (if any) and the form to re-enter a new path
    return render_template_string('''
    <html>
        <body>
            <h1>HSL Function Finder</h1>

            <!-- Form to enter or browse for a directory -->
            <form method="POST" enctype="multipart/form-data">
                <label for="directory">Enter or Browse for directory:</label>
                <input type="text" id="directory" name="directory" value="{{ directory if directory else '' }}" required>
                <input type="submit" value="Submit">
            </form>

            <!-- Show results if functions are found -->
            {% if all_functions %}
                <h2>Functions Found in Directory: {{ directory }}</h2>
                {{ create_html(all_functions)|safe }}
                <br>
            {% endif %}

            
        </body>
    </html>
    ''', directory=directory, all_functions=all_functions, create_html=create_html)



@app.route('/view_file')
def view_file():
    file_path = request.args.get('file_path')
    line_number = int(request.args.get('line_number'))

    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        # Escape HTML special characters
        escaped_lines = [line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;') for line in lines]

        # Highlight the target line
        for i in range(len(escaped_lines)):
            if i == line_number - 1:
                escaped_lines[i] = f'<span id="line-{line_number}" style="background-color:yellow;">{escaped_lines[i]}</span>'

        # Join without <br> so <pre> preserves formatting
        content = ''.join(escaped_lines)

        return f'''
        <html>
        <head>
            <title>Viewing {file_path}</title>
            <script>
                window.onload = function() {{
                    var element = document.getElementById("line-{line_number}");
                    if (element) {{
                        element.scrollIntoView({{ behavior: "smooth", block: "center" }});
                    }}
                }};
            </script>
        </head>
        <body>
            <h1>File: {file_path}</h1>
            <pre>{content}</pre>
        </body>
        </html>
        '''
    except FileNotFoundError:
        return f"File {file_path} not found."

@app.route('/open_help')
def open_help():
    file = request.args.get('file')
    full_path = os.path.abspath(file)

    # Windows-only: Use explorer to open .chm file
    if platform.system() == "Windows" and os.path.exists(full_path):
        subprocess.Popen(['explorer', full_path], shell=True)
        return f"<html><body><p>Opening help file: {file}</p><a href='/'>Back</a></body></html>"
    else:
        return f"<html><body><p>Help file not found or unsupported platform.</p><a href='/'>Back</a></body></html>"



if __name__ == '__main__':
    # Run the web server to display functions
    app.run(debug=True)
