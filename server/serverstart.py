# -*- coding:utf-8 -*-
'''
快速创建http服务，监听服务请求

FastAPI是一个现代的、快速（高性能）的web框架
pip3 install fastapi 
pip3 install uvicorn
'''
from pydantic import BaseModel
from fastapi import FastAPI
 
app = FastAPI()
 
@app.get('/test/a={a}/b={b}')
def calculate(a: int=None, b: int=None):
    c = a + b
    res = {"res":c}
    return res




 
@app.post('/test')
def calculate(request_data: Item):
    a = request_data.a
    b = request_data.b
    c = a + b
    res = {"res":c}
    return res

 
 
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app=app,
                host="0.0.0.0",
                port=8080,
                workers=1)
    