from fastapi import FastAPI, Depends
import schemas, models, auth, crud
from database import engine
from router import users

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(auth.router)
app.include_router(users.router)

