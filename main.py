from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from json import dumps
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

        f.write('['+dumps(data.dict()) + ']' + '\n')  #dict convert to словарь
        f.close()
    else:
        print("The file is not empty.")
        f = open(LOG_FILE, 'r+')
        f.seek(0, 2)  # Переход к концу файла
        f.seek(f.tell() - 2)  # Назад на 2 символа
        # Обрезаем файл до текущей позиции
        f.truncate()
        f.write('\n, ' + dumps(data.dict()) + ']' + '\n')  #dict convert to словарь
        f.close()

    






if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)