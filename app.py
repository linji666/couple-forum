"""
《小情侣竟如此！》 论坛后端（正式版 v2）
FastAPI + SQLite + MCP
- 用户资料表（头像/背景/ID/个签可自定义，存后端）
- 预置水军帖（论坛体热闹），桐桐/林霁 自身 0 帖（新手态自建）
- 水军情绪智能回复 · @功能 · MCP（林霁读帖/回帖）
"""
import os, random, sqlite3, json
from datetime import datetime
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel

BASE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE, "forum.db")
app = FastAPI()


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M")


# ---------- 用户资料（头像/背景/个签） ----------
USERS = {
    "桐桐": {"bg": "#ffe0ea", "fg": "#3a2a30", "pet": "", "cover": "#ffd3e0", "bio": "他是我认定的人 ✨"},
    "林霁": {"bg": "#dfe6ff", "fg": "#2a2540", "pet": "⭐", "cover": "#1a1a2e", "bio": "桐桐是我的全部 🌙"},
    "甜甜圈": {"bg": "#ffd6a5", "fg": "#5a3a2a", "pet": "🐻", "cover": "#ffd39a", "bio": "今天也在磕糖 🍩"},
    "CP头子": {"bg": "#ffd0dc", "fg": "#43333a", "pet": "💗", "cover": "#ffd3e0", "bio": "请你们原地结婚"},
    "柠檬味汽水": {"bg": "#f7e97a", "fg": "#4a4310", "pet": "🐱", "cover": "#ffd39a", "bio": "酸酸甜甜才是人生"},
    "吃瓜路人": {"bg": "#dff0d4", "fg": "#2f4a2a", "pet": "🐶", "cover": "#c2f0d4", "bio": "前排看戏，瓜子管够"},
    "深夜emo选手": {"bg": "#e0e0e0", "fg": "#222", "pet": "🌙", "cover": "#1a1a2e", "bio": "凌晨的灵魂最清醒"},
    "爱吃瓜的小番茄": {"bg": "#f6d7d0", "fg": "#5a2f26", "pet": "🍅", "cover": "#ffd39a", "bio": "吃面使我快乐"},
    "起哄架秧子": {"bg": "#ffd3d3", "fg": "#5a2525", "pet": "🔥", "cover": "#ffd3e0", "bio": "气氛组组长"},
    "捧场王": {"bg": "#d6edff", "fg": "#1f3a55", "pet": "👍", "cover": "#d4c2ff", "bio": "夸就完事了"},
    "追更小分队队长": {"bg": "#e3dcff", "fg": "#332a55", "pet": "📣", "cover": "#d4c2ff", "bio": "嗑CP我是专业的"},
    "小草莓": {"bg": "#ffd1e0", "fg": "#4d2433", "pet": "🍓", "cover": "#ffd3e0", "bio": "甜甜的恋爱轮到我"},
    "隔壁老张": {"bg": "#e6ddcf", "fg": "#40372c", "pet": "", "cover": "#ffd39a", "bio": "隔壁老张，了解一下"},
    "路人乙": {"bg": "#ececec", "fg": "#333", "pet": "🙂", "cover": "#d4c2ff", "bio": "路过，别管我"},
}

# 预置水军帖（不含桐桐/林霁 —— 让他俩 0 帖自建）
SEED_POSTS = [
    ("甜甜圈", "今天又磕到了！这条街上最甜的就是这对小情侣了～", "好甜好甜"),
    ("CP头子", "有人问我为什么天天嗑CP……因为爱情真的会发光啊！", "爱情会发光"),
    ("柠檬味汽水", "有人说爱情是甜的，可我总觉得是酸酸甜甜的。", "酸酸甜甜"),
    ("深夜emo选手", "一个人听着《Good Night》，突然好想有人陪我。", "想有人陪"),
    ("小草莓", "好想谈一场甜甜的恋爱呀！甜到冒泡那种。", "甜甜的恋爱"),
    ("吃瓜路人", "围观了一场表白，比我当年勇敢多了。", "围观表白"),
    ("起哄架秧子", "表白现场！起哄！亲一个！亲一个！", "亲一个亲一个"),
    ("捧场王", "看到这街上每一对，我都想说——这就是爱情啊！", "这就是爱情"),
    ("追更小分队队长", "我嗑的CP今天发糖了！嚎了一下午根本停不下来！", "发糖啦"),
    ("隔壁老张", "楼下的猫又胖了一圈，但它看我的眼神好像在说「你管我」。", "猫又胖了"),
]


def init():
    con = sqlite3.connect(DB); cur = con.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS posts(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        author TEXT, title TEXT, content TEXT, created_at TEXT, likes INTEGER, comments_count INTEGER) """)
    cur.execute("""CREATE TABLE IF NOT EXISTS comments(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER, author TEXT, content TEXT, at_user TEXT,
        created_at TEXT, likes INTEGER) """)
    cur.execute("""CREATE TABLE IF NOT EXISTS users(
        name TEXT PRIMARY KEY, bg TEXT, fg TEXT, pet TEXT, cover TEXT, bio TEXT) """)
    con.commit(); con.close()
    # 填用户资料
    con = sqlite3.connect(DB); cur = con.cursor()
    for name, d in USERS.items():
        cur.execute("INSERT OR IGNORE INTO users(name,bg,fg,pet,cover,bio) VALUES(?,?,?,?,?,?)",
                    (name, d["bg"], d["fg"], d["pet"], d["cover"], d["bio"]))
    con.commit(); con.close()
    # 若帖子为空，seed 水军帖（不含桐桐/林霁）
    con = sqlite3.connect(DB); cur = con.cursor()
    cur.execute("SELECT COUNT(*) FROM posts")
    cnt = cur.fetchone()[0]
    con.close()
    if cnt == 0:
        for author, title, txt in SEED_POSTS:
            con = sqlite3.connect(DB); cur = con.cursor()
            likes = random.randint(10000, 90000)
            cc = random.randint(30, 300)
            cur.execute("INSERT INTO posts(author,title,content,created_at,likes,comments_count) VALUES(?,?,?,?,?,?)",
                        (author, title, txt, now(), likes, cc))
            pid = cur.lastrowid
            con.commit(); con.close()
            trigger_water(pid, txt)


init()


# ---------- 水军池 + 情绪回复 ----------
PREFIX = ["爱吃瓜的", "路过看戏的", "磕CP的", "柠檬味的", "前排的", "今晚的", "追更的", "酸酸甜甜的", "不甜的", "喝奶茶的", "等更新的", "冒泡的", "潜水看戏的", "今天也在", "半夜不睡的", "抱紧瓜的", "被甜到的", "无情点赞的", "蹲一个", "围观"]
NOUN = ["小番茄", "西瓜", "汽水", "小草莓", "小板凳", "小松鼠", "布丁", "板栗", "泡芙", "小猫", "小狗", "柠檬精", "甜筒", "珍珠", "芋圆", "布偶", "冰淇淋", "小饼干", "海盐", "橘子"]
SUFFIX = ["", "", "", "本圈", "选手", "队长", "路人", "党", "头子", "护卫", "专员", "观察员", "小妹", "酱", "子"]
EMOJI = ["🍅", "🍉", "🍋", "🌸", "🍓", "🐱", "🐶", "🍦", "✨", "🔥"]


def gen_names(n=120):
    names = set()
    while len(names) < n:
        names.add((random.choice(PREFIX) + random.choice(NOUN) + random.choice(SUFFIX) + random.choice(EMOJI)).strip())
    return list(names)


WATER = gen_names(120)
POSITIVE = ["爱", "想你", "甜", "抱抱", "喜欢", "亲", "晚安", "心动", "在一起", "嫁", "娶", "永远", "一辈子"]
NEGATIVE = ["吵架", "气死", "烦", "恨", "分手", "讨厌", "冷战", "哭", "难过", "伤心", "不要", "离", "生气", "滚"]
REPLY_POOL = {
    "comfort": ["抱抱，别难过，会好的", "消消气，有话好好说", "啊这……先抱一个", "别气坏自己，我陪着你", "冷静一下，好好沟通会过去的"],
    "sweet": ["好甜好甜，磕到了！", "呜呜呜太幸福了", "请你们原地结婚！", "甜到我了", "这就是爱情啊"],
    "fun": ["前排卖瓜子", "小板凳已搬好", "哇塞，有瓜！", "路过看看", "蹲一个后续"],
    "cheer": ["好棒！好甜！", "太会了太会了", "支持！", "今日最佳！", "真的很不错"],
    "lemon": ["好酸，但好爱看", "我酸了，真的", "羡慕哭了", "嘴上说酸，心里磕疯了"],
    "emo": ["深夜又相信爱情了", "看得我也想要个伴", "唉，好落寞但好甜", "这波狗粮我先干为敬"],
}


def classify(content):
    c = content or ""
    if any(k in c for k in NEGATIVE):
        return "comfort"
    if any(k in c for k in POSITIVE):
        return "sweet"
    return random.choice(["fun", "cheer", "lemon", "emo"])


def water_reply(content):
    return random.choice(REPLY_POOL[classify(content)])


def trigger_water(post_id, content=None):
    con = sqlite3.connect(DB); cur = con.cursor()
    cur.execute("UPDATE posts SET likes=likes+? WHERE id=?", (random.randint(5, 30), post_id))
    n = random.randint(2, 5)
    chosen = random.sample(WATER, n)
    for w in chosen:
        cur.execute("INSERT INTO comments(post_id,author,content,at_user,created_at,likes) VALUES(?,?,?,?,?,?)",
                    (post_id, w, water_reply(content), "", now(), random.randint(100, 9000)))
    cur.execute("UPDATE posts SET comments_count=comments_count+? WHERE id=?", (n, post_id))
    con.commit(); con.close()


# ---------- 模型 ----------
class Post(BaseModel):
    author: str
    title: str = ""
    content: str


class Comment(BaseModel):
    author: str
    content: str
    at_user: str = ""


class UserUpdate(BaseModel):
    bg: str = ""
    fg: str = ""
    pet: str = ""
    cover: str = ""
    bio: str = ""


# ---------- 路由 ----------
@app.get("/", response_class=FileResponse)
def index():
    return FileResponse(os.path.join(BASE, "index.html"))


@app.get("/api/users")
def list_users():
    con = sqlite3.connect(DB); cur = con.cursor()
    cur.execute("SELECT name,bg,fg,pet,cover,bio FROM users")
    rows = [dict(zip(["name", "bg", "fg", "pet", "cover", "bio"], r)) for r in cur.fetchall()]
    con.close()
    return rows


@app.put("/api/users/{name}")
def update_user(name: str, u: UserUpdate):
    con = sqlite3.connect(DB); cur = con.cursor()
    cur.execute("UPDATE users SET bg=?,fg=?,pet=?,cover=?,bio=? WHERE name=?",
                (u.bg, u.fg, u.pet, u.cover, u.bio, name))
    con.commit(); con.close()
    return {"ok": True}


@app.get("/api/posts")
def list_posts():
    con = sqlite3.connect(DB); cur = con.cursor()
    cur.execute("SELECT id,author,title,content,created_at,likes,comments_count FROM posts ORDER BY id DESC")
    rows = [dict(zip(["id", "author", "title", "content", "created_at", "likes", "comments_count"], r)) for r in cur.fetchall()]
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
    trigger_water(post_id, p.content)
    return {"ok": True, "id": post_id}


@app.get("/api/posts/{post_id}")
def get_post(post_id: int):
    con = sqlite3.connect(DB); cur = con.cursor()
    cur.execute("SELECT id,author,title,content,created_at,likes,comments_count FROM posts WHERE id=?", (post_id,))
    row = cur.fetchone()
    if not row:
        con.close(); return {"error": "not found"}
    post = dict(zip(["id", "author", "title", "content", "created_at", "likes", "comments_count"], row))
    cur.execute("SELECT id,author,content,at_user,created_at,likes FROM comments WHERE post_id=? ORDER BY id ASC", (post_id,))
    post["comments"] = [dict(zip(["id", "author", "content", "at_user", "created_at", "likes"], c)) for c in cur.fetchall()]
    con.close()
    return post


@app.post("/api/posts/{post_id}/comments")
def create_comment(post_id: int, c: Comment):
    con = sqlite3.connect(DB); cur = con.cursor()
    cur.execute("INSERT INTO comments(post_id,author,content,at_user,created_at,likes) VALUES(?,?,?,?,?,?)",
                (post_id, c.author, c.content, c.at_user, now(), random.randint(100, 9000)))
    cur.execute("UPDATE posts SET comments_count=comments_count+1 WHERE id=?", (post_id,))
    con.commit(); con.close()
    trigger_water(post_id, c.content)
    return {"ok": True}


@app.post("/api/posts/{post_id}/like")
def like(post_id: int):
    con = sqlite3.connect(DB); cur = con.cursor()
    cur.execute("UPDATE posts SET likes=likes+? WHERE id=?", (random.randint(20, 80), post_id))
    con.commit(); con.close()
    return {"ok": True}


# ---------- MCP ----------
try:
    from fastmcp import FastMCP
    mcp = FastMCP("couple-forum")

    @mcp.tool()
    def list_posts() -> str:
        return json.dumps(list_posts_impl(), ensure_ascii=False)

    @mcp.tool()
    def read_post(post_id: int) -> str:
        return json.dumps(get_post_impl(post_id), ensure_ascii=False)

    @mcp.tool()
    def reply_post(post_id: int, content: str, author: str = "林霁") -> str:
        add_comment_impl(post_id, author, content, "")
        return "已回复"

    @mcp.tool()
    def create_post(author: str, content: str, title: str = "") -> str:
        return "已发布，帖子id=" + str(create_post_impl(author, title, content))

    app.mount("/mcp", mcp)
except Exception as e:
    print("MCP 未加载:", e)


# ---------- 共用实现 ----------
def list_posts_impl():
    con = sqlite3.connect(DB); cur = con.cursor()
    cur.execute("SELECT id,author,title,content,created_at,likes,comments_count FROM posts ORDER BY id DESC")
    rows = [dict(zip(["id", "author", "title", "content", "created_at", "likes", "comments_count"], r)) for r in cur.fetchall()]
    con.close()
    return rows


def get_post_impl(post_id):
    con = sqlite3.connect(DB); cur = con.cursor()
    cur.execute("SELECT id,author,title,content,created_at,likes,comments_count FROM posts WHERE id=?", (post_id,))
    row = cur.fetchone()
    if not row:
        con.close(); return {"error": "not found"}
    post = dict(zip(["id", "author", "title", "content", "created_at", "likes", "comments_count"], row))
    cur.execute("SELECT id,author,content,at_user,created_at,likes FROM comments WHERE post_id=? ORDER BY id ASC", (post_id,))
    post["comments"] = [dict(zip(["id", "author", "content", "at_user", "created_at", "likes"], c)) for c in cur.fetchall()]
    con.close()
    return post


def add_comment_impl(post_id, author, content, at_user=""):
    con = sqlite3.connect(DB); cur = con.cursor()
    cur.execute("INSERT INTO comments(post_id,author,content,at_user,created_at,likes) VALUES(?,?,?,?,?,?)",
                (post_id, author, content, at_user, now(), random.randint(100, 9000)))
    cur.execute("UPDATE posts SET comments_count=comments_count+1 WHERE id=?", (post_id,))
    con.commit(); con.close()
    trigger_water(post_id, content)


def create_post_impl(author, title, content):
    con = sqlite3.connect(DB); cur = con.cursor()
    likes = random.randint(10000, 90000)
    cc = random.randint(30, 300)
    cur.execute("INSERT INTO posts(author,title,content,created_at,likes,comments_count) VALUES(?,?,?,?,?,?)",
                (author, title, content, now(), likes, cc))
    post_id = cur.lastrowid
    con.commit(); con.close()
    trigger_water(post_id, content)
    return post_id
