"""
《小情侣竟如此！》 论坛后端（正式版 v3）
FastAPI + SQLite + MCP
- 用户资料表 · 预置水军帖(25条生活化+不侵权配图) · 0帖自建 · 情绪智能回复 · 高赞评论预览
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


def img(seed):
    return "https://picsum.photos/seed/" + seed + "/600/400"


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

# 25条生活化水军帖（不含桐桐/林霁，让他们0帖自建），每条配不侵权图
SEED_POSTS = [
    ("甜甜圈", "今天又磕到了！这条街上最甜的就是这对小情侣，我嗑得齁甜～", img("sweet")),
    ("深夜emo选手", "刚下班，地铁里全是人，累得只想回家躺平。唉，又熬过一天了。", img("metro")),
    ("爱吃瓜的小番茄", "楼下的拉面真的绝了，汤头超鲜！就是贵，心痛，但香。", img("ramen")),
    ("小草莓", "今天买了个草莓蛋糕，一口下去甜到心里，幸福感爆棚！", img("cake")),
    ("隔壁老张", "楼下的猫又胖了一圈，胖成一团，看我的眼神特别傲娇。", img("cat")),
    ("CP头子", "你们知道我嗑的那对CP今天干嘛了吗！发糖了！我嚎了一下午！", img("cp")),
    ("吃瓜路人", "路过一个表白现场，围观了三分钟，比我当年勇敢多了。", img("confess")),
    ("柠檬味汽水", "有人说爱情是甜的，可我总觉得是酸酸甜甜的，才真实。", img("lemon")),
    ("捧场王", "今天天气不错，出去走了一圈，心情都变好了！", img("sky")),
    ("起哄架秧子", "谁要表白喊我一声，我第一个起哄！专业气氛组！", img("cheer")),
    ("柠檬味汽水", "早上挤地铁差点被挤成相片，全靠一杯冰美式续命。", img("coffee")),
    ("深夜emo选手", "深夜听着《Good Night》，有点想家，也有点想找个依靠。", img("night")),
    ("小草莓", "今天的云好软，像棉花糖，好想咬一口。", img("cloud")),
    ("吃瓜路人", "下雨天窝在家刷剧，配一碗热泡面，完美的一天。", img("rain")),
    ("追更小分队队长", "今天更新的番看完啦，坐等下一集，急死我了！", img("anime")),
    ("甜甜圈", "自己做了杯齁甜的奶茶，喝一口甜到牙，但快乐！", img("milk-tea")),
    ("隔壁老张", "老伴今天做了红烧肉，真香，这个点饿得肚子咕咕叫。", img("pork")),
    ("路人乙", "又是摸鱼的一天。打工人日记第108天，今天也在努力……摸鱼。", img("work")),
    ("起哄架秧子", "楼下便利店搞活动，顺手买了两瓶汽水，开心！", img("soda")),
    ("柠檬味汽水", "今天想通了：酸就酸吧，酸完继续磕糖，日子还得过。", img("drink")),
    ("捧场王", "看到街上牵手的小情侣，我都想鼓掌——这就是爱情啊！", img("couple")),
    ("深夜emo选手", "一个人看电影，看到结尾突然觉得，要是有个人在旁边就好了。", img("movie")),
    ("爱吃瓜的小番茄", "中午食堂的饭一般般，但免费，忍了，吃！", img("lunch")),
    ("CP头子", "对面CP粉别跑，来我们这，包甜！", img("sweet2")),
    ("小草莓", "闺蜜说陪我脱单，结果她先找到对象了……我酸！", img("berry")),
]


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
    "comfort": ["抱抱，会好的", "别难过，我陪着你", "啊这……先抱一个", "乖，慢慢来", "有我真人在，不怕", "消消气，喝口热水"],
    "sweet": ["好甜好甜，磕到了！", "呜呜呜太幸福了", "这波我先干为敬", "甜到我了", "原地结婚吧", "又是为你们心动的一天"],
    "fun": ["前排卖瓜子", "路过围观", "哈哈哈哈", "蹲一个后续", "有瓜！", "这瓜我先吃"],
    "cheer": ["好棒！", "太会了！", "支持！", "这就是爱情吧", "夸！", "今日最佳"],
    "lemon": ["好酸，但好爱看", "酸了", "羡慕啊", "嘴上说酸心里磕", "我柠檬了", "酸成精了"],
    "emo": ["深夜又相信爱情了", "唉，好想有个伴", "看得我也想谈恋爱", "这波狗粮我先干", "好落寞但好甜"],
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
    cur.execute("SELECT id,author,title,content,img,created_at,likes,comments_count FROM posts ORDER BY id DESC")
    rows = [dict(zip(["id", "author", "title", "content", "img", "created_at", "likes", "comments_count"], r)) for r in cur.fetchall()]
    con.close()
    for r in rows:
        con = sqlite3.connect(DB); cur = con.cursor()
        cur.execute("SELECT author,content,likes FROM comments WHERE post_id=? ORDER BY likes DESC LIMIT 2", (r["id"],))
        r["top_comments"] = [dict(zip(["author", "content", "likes"], c)) for c in cur.fetchall()]
        con.close()
    return rows


@app.post("/api/posts")
def create_post(p: Post):
    con = sqlite3.connect(DB); cur = con.cursor()
    likes = random.randint(10000, 90000)
    cc = random.randint(30, 300)
    cur.execute("INSERT INTO posts(author,title,content,img,created_at,likes,comments_count) VALUES(?,?,?,?,?,?,?)",
                (p.author, p.title, p.content, "", now(), likes, cc))
    post_id = cur.lastrowid
    con.commit(); con.close()
    trigger_water(post_id, p.content)
    return {"ok": True, "id": post_id}


@app.get("/api/posts/{post_id}")
def get_post(post_id: int):
    con = sqlite3.connect(DB); cur = con.cursor()
    cur.execute("SELECT id,author,title,content,img,created_at,likes,comments_count FROM posts WHERE id=?", (post_id,))
    row = cur.fetchone()
    if not row:
        con.close(); return {"error": "not found"}
    post = dict(zip(["id", "author", "title", "content", "img", "created_at", "likes", "comments_count"], row))
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


try:
    from fastmcp import FastMCP
    mcp = FastMCP("couple-forum")

    @mcp.tool()
    def list_posts() -> str:
        return json.dumps(list_posts(), ensure_ascii=False)

    @mcp.tool()
    def read_post(post_id: int) -> str:
        return json.dumps(get_post(post_id), ensure_ascii=False)

    @mcp.tool()
    def reply_post(post_id: int, content: str, author: str = "林霁") -> str:
        return create_comment(post_id, Comment(author=author, content=content)) and "已回复"

    @mcp.tool()
    def create_post(author: str, content: str, title: str = "") -> str:
        return "已发布，帖子id=" + str(create_post(author, title, content)["id"])

    app.mount("/mcp", mcp)
except Exception as e:
    print("MCP 未加载:", e)


def init():
    con = sqlite3.connect(DB); cur = con.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS posts(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        author TEXT, title TEXT, content TEXT, img TEXT,
        created_at TEXT, likes INTEGER, comments_count INTEGER) """)
    cur.execute("""CREATE TABLE IF NOT EXISTS comments(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER, author TEXT, content TEXT, at_user TEXT,
        created_at TEXT, likes INTEGER) """)
    cur.execute("""CREATE TABLE IF NOT EXISTS users(
        name TEXT PRIMARY KEY, bg TEXT, fg TEXT, pet TEXT, cover TEXT, bio TEXT) """)
    con.commit(); con.close()
    con = sqlite3.connect(DB); cur = con.cursor()
    for name, d in USERS.items():
        cur.execute("INSERT OR IGNORE INTO users(name,bg,fg,pet,cover,bio) VALUES(?,?,?,?,?,?)",
                    (name, d["bg"], d["fg"], d["pet"], d["cover"], d["bio"]))
    con.commit(); con.close()
    con = sqlite3.connect(DB); cur = con.cursor()
    cur.execute("SELECT COUNT(*) FROM posts")
    cnt = cur.fetchone()[0]
    con.close()
    if cnt == 0:
        for author, title, txt_img in SEED_POSTS:
            txt, image = txt_img
            con = sqlite3.connect(DB); cur = con.cursor()
            likes = random.randint(10000, 90000)
            cc = random.randint(30, 300)
            cur.execute("INSERT INTO posts(author,title,content,img,created_at,likes,comments_count) VALUES(?,?,?,?,?,?,?)",
                        (author, title, txt, image, now(), likes, cc))
            pid = cur.lastrowid
            con.commit(); con.close()
            trigger_water(pid, txt)


init()
