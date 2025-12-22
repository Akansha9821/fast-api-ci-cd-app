import os
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

ENV = os.getenv("APP_ENV", "dev")

app = FastAPI(title=f"MyApp ({ENV})")

# Static folders
app.mount("/css", StaticFiles(directory="css"), name="css")
app.mount("/js", StaticFiles(directory="js"), name="js")
app.mount("/img", StaticFiles(directory="img"), name="img")

@app.get("/", include_in_schema=False)
def root():
    return FileResponse("html/main.html")
