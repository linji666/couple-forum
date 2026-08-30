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
    "comfort": ["抱抱，别难过，会过去的", "先别气，喝口热水缓缓", "啊这，我先抱一个再说", "慢慢来，不着急的", "有情绪说出来就好，我听着", "别憋着，我陪你聊", "气坏了自己不划算", "深呼吸，明天会更好", "这种时候最需要人陪了，抱抱", "你的感受我懂，会好的"],
    "sweet": ["好甜好甜，磕到了！", "呜呜呜这也太幸福了吧", "你们俩这糖我磕定了", "看完嘴角就没下来过", "原地结婚！快！", "这就是我理想中的爱情啊", "甜得我牙都倒了但还想吃", "救命，这种日常谁顶得住", "细节好戳我，是真的在爱", "请务必一直这样下去"],
    "fun": ["哈哈哈哈笑死我了", "这楼我蹲住了，等后续", "路过带了个瓜，顺手吃一口", "笑不活了，这是真的吗", "快展开说说，别吊胃口", "我搬好小板凳了", "前排围观，瓜子管够", "太真实了，是我本人", "这不就是生活吗，哈哈", "蹲一个后续，别停"],
    "cheer": ["这波真的可以，赞！", "太优秀了，向你学习", "我看行，支持！", "给你点个大大的赞", "好棒，继续保持！", "真有你的，厉害", "这状态绝了，佩服", "不错的，为你能做成一件事高兴", "羡慕了，你也太会了吧", "慢慢来，你已经在变好了"],
    "lemon": ["酸得我默默喝了一口柠檬水", "这谁顶得住啊，酸", "我默默收起了我的狗碗", "嘴上说羡慕，心里其实为你开心", "酸归酸，还是祝你们好", "今天也是被甜到酸的一天", "好家伙，这波柠檬我吃了", "看着你们，我又相信感情了", "酸是酸了点，但祝福是真的", "我酸我快乐，继续看"],
    "emo": ["突然也想要这样安定的日子", "看完有点想找人说说话", "羡慕得我有点睡不着", "这样的陪伴真好啊", "我也想有个能一起吃饭的人", "深夜看到这个，心里软软的", "平平淡淡才是真，真好", "有点想家了，也有点想ta", "这样的时刻最戳人心", "我也相信，会轮到我的"],
}


def classify(content):
    c = content or ""
    if any(k in c for k in NEGATIVE):
        return "comfort"
    if any(k in c for k in POSITIVE):
        return "sweet"
    return random.choice(["fun", "fun", "cheer", "cheer", "lemon", "emo", "emo"])


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
