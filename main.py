from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from json import dumps
from json import load
from fastapi.responses import HTMLResponse
import os


app = FastAPI(title="JSON Logger Server", version="1.0.0")


LOG_FILE = "data_log.json"

class JSONData(BaseModel):
    accuracy: float
    latitude: float
    longitude: float
    provider: str
    recordedTime: int
    source: str
    timestamp: int



if not os.path.exists(LOG_FILE):
    open(LOG_FILE, 'w').close()



@app.post("/push")
async def pushData(data: JSONData):

    if os.path.getsize(LOG_FILE) == 0:
        f = open(LOG_FILE, 'w')
        print("The file is empty.")

        f.write('['+dumps(data.model_dump()) + ']' + '\n')  #dict convert to словарь
        f.close()
    else:
        print("The file is not empty.")
        f = open(LOG_FILE, 'r+')
        f.seek(0, 2)  # Переход к концу файла
        f.seek(f.tell() - 2)  # Назад на 2 символа
        # Обрезаем файл до текущей позиции
        f.truncate()
        f.write('\n, ' + dumps(data.model_dump()) + ']' + '\n')  #dict convert to словарь
        f.close()



def read_all_data():
    """Читает все данные из файла"""
  
    try:
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            return load(f)
    except :
        return []





    
@app.get("/log")
async def show_all_data():

    try:
        data = read_all_data()
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Location Data Logger</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    background-color: #f5f5f5;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background: white;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                h1 {{
                    color: #333;
                    text-align: center;
                }}
                .stats {{
                    background: #e8f4fd;
                    padding: 15px;
                    border-radius: 5px;
                    margin-bottom: 20px;
                }}
                .data-table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 20px;
                }}
                .data-table th, .data-table td {{
                    border: 1px solid #ddd;
                    padding: 12px;
                    text-align: left;
                }}
                .data-table th {{
                    background-color: #4CAF50;
                    color: white;
                    position: sticky;
                    top: 0;
                }}
                .data-table tr:nth-child(even) {{
                    background-color: #f2f2f2;
                }}
                .data-table tr:hover {{
                    background-color: #e9e9e9;
                }}
                .timestamp {{
                    font-size: 0.9em;
                    color: #666;
                }}
                .coordinates {{
                    font-family: monospace;
                }}
                .map-link {{
                    color: #2196F3;
                    text-decoration: none;
                }}
                .map-link:hover {{
                    text-decoration: underline;
                }}
                .no-data {{
                    text-align: center;
                    color: #666;
                    font-style: italic;
                    padding: 40px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📍 Location Data Logger</h1>
                
                <div class="stats">
                    <strong>Всего записей:</strong> {len(data)}<br>
                 
                </div>
        """
        
        if not data:
            html_content += """
                <div class="no-data">
                    <h2>📭 Данных пока нет</h2>
                    <p>Отправьте данные через POST запрос на /push</p>
                </div>
            """
        else:
            html_content += """
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Время получения</th>
                            <th>Координаты</th>
                            <th>Точность</th>
                            <th>Провайдер</th>
                            <th>Источник</th>
                            <th>Карта</th>
                        </tr>
                    </thead>
                    <tbody>
            """
            
            for i, entry in enumerate(reversed(data), 1):  
               
                server_time = entry.get('server_received_time', 'N/A')
                if server_time != 'N/A':
                    try:
               
                        server_time = dt.strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        pass
                
     
                lat = entry.get('latitude', 0)
                lon = entry.get('longitude', 0)
                map_url = f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}&zoom=15"
                
                html_content += f"""
                        <tr>
                            <td>{i}</td>
                            <td class="timestamp">{server_time}</td>
                            <td class="coordinates">
                                📍 {lat:.6f}, {lon:.6f}
                            </td>
                            <td>{entry.get('accuracy', 'N/A')}м</td>
                            <td>{entry.get('provider', 'N/A')}</td>
                            <td>{entry.get('source', 'N/A')}</td>
                            <td>
                                <a href="{map_url}" target="_blank" class="map-link">
                                    🗺️ Посмотреть на карте
                                </a>
                            </td>
                        </tr>
                """
            
            html_content += """
                    </tbody>
                </table>
            """
        
        html_content += """
            </div>
        </body>
        </html>
        """
        
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head><title>Error</title></head>
        <body>
            <h1>Ошибка</h1>
            <p>Не удалось загрузить данные: {str(e)}</p>
        </body>
        </html>
        """
        return HTMLResponse(content=error_html, status_code=500)

@app.get("/data")
async def get_raw_data():
    try:
        data = read_all_data()
        return {
            "status": "success",
            "count": len(data),
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading data: {str(e)}")




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)