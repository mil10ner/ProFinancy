import uvicorn
from fastapi import FastAPI
import redis
from random import randint


app = FastAPI(
    title='ReportWB',
    description='API Для работы с рекламой WB',
    version='0.0.1')


# Коннектор к Redis
# Вставляем свои данные к своей бзе Redis
client = redis.Redis(host="localhost",
                port=49153,
                username="default",
                password="redispw",
                db=0,
                charset='utf-8',
                decode_responses=True)



# РАБОТА С БАЗОЙ
# Запись нового голосования id - идентификатор голосования name - название голосования list_option - ответы
def set_vote(id, name, list_option):
    client.lpush(id, name)
    for option in list_option:
        client.rpush(id, f"{option}:0")
    client.rpush(id, f"counter:0")

# Запрос нужного голосования по id
def get_vote(id):
    vote = client.lrange(id, 0, -1)
    return vote

# Процес голосования. Добавляет 1 к необходимому ответу из списка
def set_vote_option(id, option):
    options = client.lrange(id, 0, -1)
    n = False
    count = 1
    for o in options[1:-1]:
        x = o.split(":")[0]
        y = int(o.split(":")[1])
        if x == option:
            y += 1
            client.lset(id, count, f"{x}:{y}")
            n = True
        count += 1

    count = int(options[-1].split(':')[1])
    client.lset(id, -1, f"counter:{count+1}")

    return n


# Метод создания нового голосования
@app.post("/vote/new_vote/")
async def new_vote_p(name_vote: str, list_option: list[str]):
    id = f"{randint(0,1000)}{randint(0,1000)}{randint(0,1000)}"
    set_vote(id, name_vote, list_option)
    return id

# Метод непосредственного голосования
@app.post("/vote/vote_option/")
async def get_vote_p(id_vote: str, option: str):
    vote = set_vote_option(id_vote, option)
    if vote == True:
        return "Спасибо за голос. Мы ценим ваш выбор"
    else:
        return "Среди вопросов нет вашего. Попробуйте проголосовать еще раз!"

# Метод получения результатов голосования
@app.post("/vote/get_vote/")
async def get_vote_p(id_vote: str):
    list_vo = get_vote(id_vote)
    response = list_vo[0]
    count = int(list_vo[-1].split(":")[1])
    for vo in list_vo[1:-1]:
        x = vo.split(":")[0]
        y = int(vo.split(":")[1])
        response += f"-- {x} : {round((y / count) * 100, 2)}% --"
    response += f"Всего проголосовало : {count}"
    return response


if __name__ == '__main__':
    uvicorn.run(
        "main:app",
        host='0.0.0.0',
        port=7000,
        #workers=5,
        reload=True,
    )







