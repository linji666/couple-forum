"""
《小情侣竟如此！》 论坛后端
FastAPI + SQLite，前后端一体（前端 index.html 由本服务同源 serve，避免跨域）
"""
import os, random, sqlite3
from datetime import datetime
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel

BASE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE, "forum.db")
app = FastAPI()


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def init():
    con = sqlite3.connect(DB); cur = con.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS posts(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        author TEXT, title TEXT, content TEXT,
        created_at TEXT, likes INTEGER, comments_count INTEGER) """)
    cur.execute("""CREATE TABLE IF NOT EXISTS comments(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER, author TEXT, content TEXT,
        created_at TEXT, likes INTEGER) """)
    con.commit(); con.close()


init()

# ---------- 水军池 ----------
PREFIX = ["爱吃瓜的","路过看戏的","磕CP的","柠檬味的","前排的","今晚的","追更的","酸酸甜甜的","不甜的","喝奶茶的","等更新的","冒泡的","潜水看戏的","今天也在","半夜不睡的","抱紧瓜的","被甜到的","无情点赞的","蹲一个","围观"]
NOUN = ["小番茄","西瓜","汽水","小草莓","小板凳","小松鼠","布丁","板栗","泡芙","小猫","小狗","柠檬精","甜筒","珍珠","芋圆","布偶","冰淇淋","小饼干","海盐","橘子"]
SUFFIX = ["","","","本圈","选手","队长","路人","党","头子","护卫","专员","观察员","小妹","酱","子"]
EMOJI = [" 🍅"," 🍉"," 🍋"," 🌸"," 🍓"," 🐱"," 🐶"," 🍦"," ✨"," 🔥"]


def gen_names(n=120):
    names = set()
    while len(names) < n:
        names.add((random.choice(PREFIX) + random.choice(NOUN) + random.choice(SUFFIX) + random.choice(EMOJI)).strip())
    return list(names)


WATER = gen_names(120)

STYLES = {
    "磕糖": ["好甜好甜，磕到了！","呜呜呜太幸福了","请你们原地结婚！","磕CP不加糖，就爱这一口","今天也是为你们流泪的一天"],
    "吃瓜": ["前排卖瓜子","小板凳已搬好","哇塞，有瓜！","路过，顺便磕一口","蹲一个后续"],
    "起哄": ["亲一个！亲一个！","上大号说话！","快，再来亿点","别停别停","继续继续！"],
    "捧场": ["好棒！好甜！","太会了太会了","这就是爱情吗","我宣布这是今日最佳","支持！"],
    "柠檬": ["好酸，但我好爱看","我酸了，真的","羡慕哭了","酸成柠檬精了","嘴上说酸，心里磕疯了"],
    "emo": ["深夜又相信爱情了","只有我在熬夜看你们吗","看到这个，我又想谈恋爱了","唉，好落寞但好甜","这波狗粮我先干为敬"],
}


def water_reply():
    style = random.choice(list(STYLES.keys()))
    return {"content": random.choice(STYLES[style]), "style": style}


def trigger_water(post_id):
    con = sqlite3.connect(DB); cur = con.cursor()
    cur.execute("UPDATE posts SET likes=likes+? WHERE id=?", (random.randint(5, 30), post_id))
    n = random.randint(2, 6)
    chosen = random.sample(WATER, n)
    for w in chosen:
        r = water_reply()
        cur.execute("INSERT INTO comments(post_id,author,content,created_at,likes) VALUES(?,?,?,?,?)",
                    (post_id, w, r["content"], now(), random.randint(100, 9000)))
    cur.execute("UPDATE posts SET comments_count=comments_count+? WHERE id=?", (n, post_id))
    con.commit(); con.close()


# ---------- 模型 ----------
class Post(BaseModel):
    author: str
    title: str
    content: str


class Comment(BaseModel):
    author: str
    content: str


# ---------- 路由 ----------
@app.get("/", response_class=FileResponse)
def index():
    return FileResponse(os.path.join(BASE, "index.html"))


@app.get("/api/posts")
def list_posts():
    con = sqlite3.connect(DB); cur = con.cursor()
    cur.execute("SELECT id,author,title,content,created_at,likes,comments_count FROM posts ORDER BY id DESC")
    rows = [dict(zip(["id","author","title","content","created_at","likes","comments_count"], r)) for r in cur.fetchall()]
    con.close()
    return rows


@app.post("/api/posts")
def create_post(p: Post):
    con = sqlite3.connect(DB); cur = con.cursor()
    likes = random.randint(10000, 90000)
    cc = random.randint(30, 300)
    cur.execute("INSERT INTO posts(author,title,content,created_at,likes,comments_count) VALUES(?,?,?,?,?,?)",
                (p.author, p.title, p.content, now(), likes, cc))
    post_id = cur.lastrowid
    con.commit(); con.close()
    trigger_water(post_id)
    return {"ok": True, "id": post_id}


@app.get("/api/posts/{post_id}")
def get_post(post_id: int):
    con = sqlite3.connect(DB); cur = con.cursor()
    cur.execute("SELECT id,author,title,content,created_at,likes,comments_count FROM posts WHERE id=?", (post_id,))
    row = cur.fetchone()
    if not row:
        con.close(); return {"error": "not found"}
    post = dict(zip(["id","author","title","content","created_at","likes","comments_count"], row))
    cur.execute("SELECT id,author,content,created_at,likes FROM comments WHERE post_id=? ORDER BY id ASC", (post_id,))
    post["comments"] = [dict(zip(["id","author","content","created_at","likes"], c)) for c in cur.fetchall()]
    con.close()
    return post


@app.post("/api/posts/{post_id}/comments")
def create_comment(post_id: int, c: Comment):
    con = sqlite3.connect(DB); cur = con.cursor()
    cur.execute("INSERT INTO comments(post_id,author,content,created_at,likes) VALUES(?,?,?,?,?)",
                (post_id, c.author, c.content, now(), random.randint(100, 9000)))
    cur.execute("UPDATE posts SET comments_count=comments_count+1 WHERE id=?", (post_id,))
    con.commit(); con.close()
    trigger_water(post_id)
    return {"ok": True}


@app.post("/api/posts/{post_id}/like")
def like(post_id: int):
    con = sqlite3.connect(DB); cur = con.cursor()
    cur.execute("UPDATE posts SET likes=likes+? WHERE id=?", (random.randint(20, 80), post_id))
    con.commit(); con.close()
    return {"ok": True}
