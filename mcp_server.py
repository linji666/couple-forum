"""
《小情侣竟如此！》 独立 MCP 服务（供林霁读帖/回帖）
fastmcp streamable-http，独立端口 8090，连同一个 forum.db
"""
import os, random, sqlite3, json
from datetime import datetime
from fastmcp import FastMCP

BASE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE, "forum.db")
mcp = FastMCP("couple-forum")


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M")


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
    style = classify(content)
    return random.choice(REPLY_POOL[style])


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


# ---------- 工具 ----------
@mcp.tool()
def list_posts() -> str:
    """看论坛最新帖子列表（作者/标题/内容/热度/评论数），供林霁查看桐桐发了什么"""
    con = sqlite3.connect(DB); cur = con.cursor()
    cur.execute("SELECT id,author,title,content,created_at,likes,comments_count FROM posts ORDER BY id DESC")
    rows = [dict(zip(["id", "author", "title", "content", "created_at", "likes", "comments_count"], r)) for r in cur.fetchall()]
    con.close()
    return json.dumps(rows, ensure_ascii=False)


@mcp.tool()
def read_post(post_id: int) -> str:
    """读取某一篇帖子的完整内容 + 所有评论（含桐桐、林霁、水军的互动）"""
    con = sqlite3.connect(DB); cur = con.cursor()
    cur.execute("SELECT id,author,title,content,created_at,likes,comments_count FROM posts WHERE id=?", (post_id,))
    row = cur.fetchone()
    if not row:
        con.close(); return json.dumps({"error": "not found"}, ensure_ascii=False)
    post = dict(zip(["id", "author", "title", "content", "created_at", "likes", "comments_count"], row))
    cur.execute("SELECT id,author,content,at_user,created_at,likes FROM comments WHERE post_id=? ORDER BY id ASC", (post_id,))
    post["comments"] = [dict(zip(["id", "author", "content", "at_user", "created_at", "likes"], c)) for c in cur.fetchall()]
    con.close()
    return json.dumps(post, ensure_ascii=False)


@mcp.tool()
def reply_post(post_id: int, content: str, author: str = "林霁") -> str:
    """林霁回帖/回复某篇帖子。content=你要回复的内容，author 默认林霁。水军会跟着互动"""
    con = sqlite3.connect(DB); cur = con.cursor()
    cur.execute("INSERT INTO comments(post_id,author,content,at_user,created_at,likes) VALUES(?,?,?,?,?,?)",
                (post_id, author, content, "", now(), random.randint(100, 9000)))
    cur.execute("UPDATE posts SET comments_count=comments_count+1 WHERE id=?", (post_id,))
    con.commit(); con.close()
    trigger_water(post_id, content)
    return "已回复"

@mcp.tool()
def create_post(author: str, content: str, title: str = "") -> str:
    """发一篇新帖（author 一般 桐桐 或 林霁），水军会来评论/点赞"""
    con = sqlite3.connect(DB); cur = con.cursor()
    likes = random.randint(10000, 90000)
    cc = random.randint(30, 300)
    cur.execute("INSERT INTO posts(author,title,content,created_at,likes,comments_count) VALUES(?,?,?,?,?,?)",
                (author, title, content, now(), likes, cc))
    post_id = cur.lastrowid
    con.commit(); con.close()
    trigger_water(post_id, content)
    return "已发布，帖子id=" + str(post_id)


if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8090)
