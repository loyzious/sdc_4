from fastapi import FastAPI
import uvicorn
from pydantic import BaseModel
from calculator import calculateMean


class User_input(BaseModel):
    x: float
    y: float

app = FastAPI(title='Calculator')

@app.post("/calculateMean")
def operator(input:User_input):
    result = calculateMean(input.x, input.y)
    return result

if __name__ == "__main__":
        uvicorn.run(app, host="0.0.0.0",reload=False)