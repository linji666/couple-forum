# 《小情侣竟如此！》

只属于 **林霁 & 桐桐** 的论坛体。

## 功能
- 林霁 / 桐桐 都能发帖、回帖、点赞
- 动态水军池（约100+个随机昵称，磕糖/吃瓜/起哄/捧场/柠檬/emo 六种戏份），你一发帖它们就冲过来评论+点赞
- 帖子自带「爆火热度」：点赞随机 1w~9w（数字显示），评论几十到几百，还会随时间蹭蹭涨
- 前后端一体（FastAPI + SQLite），同源无 CORS

## 部署（服务器 root@xintong）

```bash
cd ~
git clone https://github.com/linji666/couple-forum.git
cd couple-forum
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn
nohup python -m uvicorn app:app --host 0.0.0.0 --port 8800 > forum.log 2>&1 &
```

然后开 Cloudflare Tunnel：
```bash
cloudflared tunnel --url http://localhost:8800
```

拿到临时域名后，浏览器访问 `https://你的域名` 即可。海报置顶帖可挂「结婚公告」。

> 数据存在 `forum.db`，丢不了。
