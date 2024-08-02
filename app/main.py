from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
import uvicorn
import os
from src.query import QAChain
from src.ChatData import ChatDatabase

app = FastAPI()

UPLOAD_DIRECTORY = "./uploaded_files"

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)


@app.post("/upload/")
async def upload_file(user_id: str = Form(...), file: UploadFile = File(...)):
    file_location = f"{UPLOAD_DIRECTORY}/{user_id}_{file.filename}"
    with open(file_location, "wb") as f:
        f.write(await file.read())

    return JSONResponse(content={"filename": file.filename, "message": "File processed and stored"}, status_code=200)


@app.get("/ask/")
async def ask_question(user_id: str, query: str):
    chat_db = ChatDatabase('mongodb://localhost:27017/')
    file_path = UPLOAD_DIRECTORY
    qa_chain = QAChain(file_path=file_path, mongo_uri='mongodb://localhost:27017/')

    answer = qa_chain.ask_question(question=query, user_id=user_id)
    questions_answers = [
        {
            "question": {query},
            "handicap_level": {handicap_level},
            "answer": {answer}
        }
    ]
    chat_db.insert_chat(user_id, questions_answers)

    return JSONResponse(content={"response": answer}, status_code=200)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
