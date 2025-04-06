from flask import Flask, render_template, request, send_from_directory
import os

app = Flask(__name__)
REPORTS_FOLDER = 'reports'

@app.route('/')
def index():
    reports = [f for f in os.listdir(REPORTS_FOLDER) if f.endswith('.html')]
    selected = request.args.get('report', reports[0] if reports else None)
    return render_template('index.html', reports=reports, selected=selected)

@app.route('/report/<filename>')
def report(filename):
    return send_from_directory(REPORTS_FOLDER, filename)

if __name__ == '__main__':
    app.run(port=8080, debug=True)
    