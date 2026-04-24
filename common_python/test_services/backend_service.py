"""
后端测试服务
"""

import uvicorn
from fastapi import FastAPI

app = FastAPI()


@app.get("/aaa")
async def root(code, scope):
    print(f"google code:\n {code} \n")
    return {"message": "Hello World"}


if __name__ == "__main__":
    uvicorn.run("backend_service:app", host="0.0.0.0", port=9080, reload=True)
