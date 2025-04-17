import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from werkzeug.utils import secure_filename
import csv
import io
from zipfile import ZipFile
import tempfile

app = Flask(__name__)
app.secret_key = 'secret_key'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def upload_db():
    if request.method == 'POST':
        file = request.files.get('dbfile')
        if not file or file.filename == '':
            flash('Please upload a .db or .sqlite3 file')
            return redirect(request.url)
        if not (file.filename.endswith('.db') or file.filename.endswith('.sqlite3')):
            flash('Invalid file type. Please upload a .db or .sqlite3 file')
            return redirect(request.url)

        filename = secure_filename(file.filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(path)
        return redirect(url_for('show_database', filename=filename))

    return render_template('upload.html')

@app.route('/view/<filename>')
def show_database(filename):
    db_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()

    all_tables = []
    for (table_name,) in tables:
        cursor.execute(f"PRAGMA table_info('{table_name}')")
        schema = cursor.fetchall()

        cursor.execute(f"SELECT * FROM '{table_name}'")
        rows = cursor.fetchall()

        cursor.execute(f"PRAGMA foreign_key_list('{table_name}')")
        fks = cursor.fetchall()

        all_tables.append({
            'name': table_name,
            'schema': schema,
            'rows': rows,
            'columns': [col[1] for col in schema],
            'foreign_keys': fks
        })


    cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='view'")
    views = cursor.fetchall()
    cursor.execute("SELECT name, tbl_name, sql FROM sqlite_master WHERE type='index'")
    indexes = cursor.fetchall()
    cursor.execute("SELECT name, tbl_name, sql FROM sqlite_master WHERE type='trigger'")
    triggers = cursor.fetchall()  
    er_diagram = generate_er_diagram(all_tables)
    conn.close()

    return render_template('database.html',
                           tables=all_tables,
                           views=views,
                           indexes=indexes,
                           triggers=triggers, er_diagram=er_diagram,
                           filename=filename)

@app.route('/export/<filename>/<table_name>')
def export_csv(filename, table_name):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    conn = sqlite3.connect(filepath)
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM '{table_name}'")
    rows = cursor.fetchall()
    headers = [description[0] for description in cursor.description]
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    writer.writerows(rows)
    output.seek(0)

    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f"{table_name}.csv"
    )

@app.route('/export/json/<filename>/<table_name>')
def export_json(filename, table_name):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    conn = sqlite3.connect(filepath)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM '{table_name}'")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return {
        "table": table_name,
        "data": rows
    }

import json 

@app.route('/export/all/<filename>')
def export_all_zip(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    conn = sqlite3.connect(filepath)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]

    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, f"{filename}_export.zip")

    with ZipFile(zip_path, 'w') as zipf:
        for table in tables:

            cursor.execute(f"SELECT * FROM '{table}'")
            rows = cursor.fetchall()
            headers = [desc[0] for desc in cursor.description]

            csv_content = io.StringIO()
            writer = csv.writer(csv_content)
            writer.writerow(headers)
            writer.writerows(rows)
            zipf.writestr(f"{table}.csv", csv_content.getvalue())


            cursor.execute(f"SELECT * FROM '{table}'")
            conn.row_factory = sqlite3.Row
            rows_dict = []
            

            for row in cursor.fetchall():
                row_dict = {desc[0]: row[idx] for idx, desc in enumerate(cursor.description)}
                rows_dict.append(row_dict)
                
            json_data = json.dumps(rows_dict, ensure_ascii=False)  
            zipf.writestr(f"{table}.json", json_data)

    conn.close()
    return send_file(zip_path, as_attachment=True, download_name="full_export.zip")

def generate_er_diagram(tables):
    diagram = "erDiagram\n"
    for table in tables:
        table_name = table['name']
        diagram += f"    {table_name} {{\n"
        for col in table['schema']:
            col_name = col[1]
            col_type = col[2]
            diagram += f"        {col_name} {col_type}\n"
        diagram += "    }\n"
        for fk in table['foreign_keys']:
            from_col = fk[3]
            to_table = fk[2]
            to_col = fk[4]
            diagram += f"    {table_name} ||--o| {to_table}: \"{from_col} -> {to_col}\"\n"
    return diagram

if __name__ == '__main__':
    app.run(debug=True)
