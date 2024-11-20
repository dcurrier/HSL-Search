from flask import Flask, render_template_string, request
import os
from pathlib import Path
import re

# Function to extract function names and return types from .hsl/.hs_/.hsi files
def extract_functions_from_file(file_path, root_directory):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        content = file.read()

    # Updated Regex pattern for functions with named capture groups (name, args, returns)
    function_pattern = r"^\s*function\s+(?P<name>\w+)\s*\((?P<args>.*)\)\s*(?P<returns>\w*)\s*{"
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
            "line_number": line_number
        })
    
    return functions

def extract_all_functions(directory):
    all_functions = {}

    for root, _, files in os.walk(directory):
        for file in files:
            file_path = Path(root) / file

            # Exclude files that start with "~"
            if file.startswith("~"):
                continue

            file_ext = file_path.suffix
            stem = file_path.stem

            # Collect functions from .hsl, .hs_, .hsi files
            if file_ext in ['.hsl', '.hs_', '.hsi']:
                functions = extract_functions_from_file(file_path, directory)

                # Check if the stem already exists in all_functions and if the function list is non-empty
                if stem in all_functions and len(all_functions[stem]) > 0:
                    # If the existing file is an .hsl, skip adding functions from .hs_ or .hsi
                    if Path(all_functions[stem][0]['file_path']).suffix == '.hsl' and file_ext in ['.hs_', '.hsi']:
                        continue
                else:
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
        
        # Generate HTML for the file content
        highlighted_lines = ""
        for i, line in enumerate(lines):
            if i == line_number - 1:
                highlighted_lines += f'<span id="line-{line_number}" style="background-color:yellow;">{line}</span><br>'
            else:
                highlighted_lines += f'{line}<br>'
        
        # Add JavaScript to scroll to the highlighted line
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
            <pre>{highlighted_lines}</pre>
        </body>
        </html>
        '''
    except FileNotFoundError:
        return f"File {file_path} not found."



if __name__ == '__main__':
    # Run the web server to display functions
    app.run(debug=True)
