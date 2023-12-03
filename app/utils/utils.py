import hashlib
from string import Template


def generate_hash(input_string):
    sha256_hash = hashlib.sha256()
    sha256_hash.update(input_string.encode('utf-8'))
    return sha256_hash.hexdigest()


def generate_html_table(tasks: list):
    template = Template("""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>PDF Report</title>
        </head>
        <body>
            <h1>Tasks List</h1>
            <table border="1">
                <thead>
                    <tr>
                        $header
                    </tr>
                </thead>
                <tbody>
                    $body
                </tbody>
            </table>
        </body>
        </html>
        """)

    # Prepare header row
    header_row = "".join(f"<th width=\"200px\">{key}</th>" for key in tasks[0].keys())
    # Prepare body rows
    body_rows = "".join(
        "".join(f"<td style=\"text-align:center;\">{value}</td>" for value in row.values())
        for row in tasks
    )

    # Substitute values into the template
    html_content = template.substitute(header=header_row, body=body_rows)

    return html_content

