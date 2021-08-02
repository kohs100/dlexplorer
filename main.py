import dlsite
import json
import atexit
import webbrowser
from glob import glob
from flask import Flask, send_file, jsonify, send_from_directory

app = Flask(__name__)

DB = {}

def DBWriteBack():
    with open('db.json', 'w', encoding='utf-8') as fp:
        json.dump(DB, fp, ensure_ascii=False)

def DBLoad():
    global DB
    try:
        with open('db.json', 'r', encoding='utf-8') as fp:
            DB = json.load(fp)
    except FileNotFoundError:
        print("db.json not found. Creating one...")
    except json.decoder.JSONDecodeError:
        arg = input("Corrupted db.json detected. Create new one?(Y/n)")
        if arg.lower() == 'y':
            print('Creating one...')
        else:
            print('Exiting...')
            exit()
    
    atexit.register(DBWriteBack)

def load_work(richcode):
    if richcode in DB:
        return True
    else:
        try:
            res = dlsite.Work(richcode)
        except dlsite.WorkNotFoundError:
            DB[richcode] = None
            return True
        except Exception as e:
            print(e)
            return False
        else:
            DB[richcode] = res.dict
            return True
        
@app.route('/dlsite/db/<code>', methods=['GET'])
def get_dlsite(code):
    if not dlsite.Utils.validate_code(code):
        return app.response_class(
            response = "InvalidCode",
            status = 404
        )
    
    if load_work(code):
        if DB[code]:
            return jsonify(DB[code])
        else:
            return app.response_class(
                response = "WorkNotFound",
                status = 404
            )

def get_image(richcode):
    path = f'images/{richcode}.jpg'
    if not glob(path):
        dlsite.Utils.get_image(f'images/{richcode}.jpg', richcode, DB[richcode]["img_url"])
    return path

@app.route('/dlsite/db/<code>/img', methods=['GET'])
def img_dlsite(code):
    if not dlsite.Utils.validate_code(code):
        return app.response_class(
            response = "InvalidCode",
            status = 404
        )

    if load_work(code):
        if DB[code]:
            return send_file(get_image(code), mimetype="image/jpeg")
        else:
            return app.response_class(
                response = "WorkNotFound",
                status = 404
            )

@app.route('/dlsite/<path:path>', methods=['GET'])
def index_dlsite(path):
    return send_from_directory('ui', path)
            
if __name__ == '__main__':
    DBLoad()
    chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'
    webbrowser.get(chrome_path).open('http://localhost:5000/dlsite/index.html')
    app.run()