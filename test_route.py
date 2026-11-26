from fastapi import FastAPI
from fastapi.responses import FileResponse

app = FastAPI()

@app.get('/interface', include_in_schema=False)
def interface():
    return FileResponse('interface.html')

# Check the routes
for route in app.routes:
    print(f'Route: {route.path} methods={getattr(route, "methods", None)}')