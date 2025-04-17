# SQLite Database Viewer

A web application built using **Flask** that allows users to upload SQLite database files, view tables, schema, and foreign keys, and export data in CSV, JSON, or ZIP formats. It also generates an Entity-Relationship (ER) diagram for the database schema.

## Features

- **Upload SQLite Database**: Upload `.db` or `.sqlite3` files.
- **View Tables**: Displays all tables in the uploaded SQLite database.
- **View Table Schema**: View table structure with columns, data types, and other properties.
- **View Foreign Keys**: Displays foreign key relationships between tables.
- **Export Data**: Export tables as CSV or JSON files.
- **Download All Data**: Download all tables in a ZIP file containing both CSV and JSON files.
- **ER Diagram**: Visualize the database structure with an automatically generated ER diagram.

## Requirements

Make sure to have the following dependencies:

- Python 3.x
- Flask
- SQLite3

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/shahram8708/DataHub.git
   cd DataHub
   ```

2. Install the dependencies using `pip`:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Run the Flask Application**:
   
   To start the web server, run:

   ```bash
   python app.py
   ```

   This will start the server at `http://127.0.0.1:5000/`.

2. **Upload a SQLite Database**:

   - Navigate to the home page (`/`).
   - Upload a `.db` or `.sqlite3` file by selecting the file and clicking on **Submit**.
   - After the database is uploaded, you will be redirected to a page that displays all the tables, their schema, foreign key relationships, and an ER diagram.

3. **Export Data**:

   - To export a table as a CSV or JSON file, click on the respective button next to each table.
   - You can also download all tables in a ZIP file containing both CSV and JSON formats by clicking on the **Download All** button.

4. **View ER Diagram**:

   - After uploading the database, an ER diagram representing the database schema will be displayed on the page.

## File Structure

```
/sqlite-database-viewer
├── app.py                    # Main Flask application
├── requirements.txt          # List of required dependencies
├── templates/                # HTML templates for Flask
│   ├── database.html         # Template to display database info
│   └── upload.html           # Template for uploading SQLite database
└── uploads/                  # Directory for storing uploaded databases
```

## Customization

- **Change Database Directory**: To change where the uploaded files are stored, modify the `UPLOAD_FOLDER` variable in `app.py`.
- **Add New Export Formats**: If you want to add new export formats (other than CSV or JSON), you can extend the export logic in `app.py` with new routes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- **Flask** for providing a simple and lightweight framework for building web applications.
- **SQLite** for being an easy-to-use database engine.
- **Mermaid.js** for generating the ER diagram.