---
type: "post"
id: 1
title: "我的第一篇 Django 博客文章"
slug: "my-first-django-post"
status: "published"
excerpt: "这是 Yuki Blog 的第一篇测试文章。"
cover: "posts/2026/07/96cd1b8143ae00e027ebf3a7dafaf170--867638143.jpg"
category: "technology"
tags: ["django", "python"]
author: "yuki"
is_featured: true
is_pinned: true
published_at: "2026-07-14T10:14:00+00:00"
created_at: "2026-07-14T10:15:47.149387+00:00"
updated_at: "2026-07-17T07:29:53.313841+00:00"
url: "/blog/my-first-django-post/"
---

把一个生产域名从旧应用逐步切到重写版，首先需要明确缓存与路由的边界。

## 分流必须发生在缓存之前

每一层缓存都需要回答一个问题：

> 当前缓存键是否包含了真正决定内容版本的信息？

下面是一段示例代码：

```python
def select_origin(bucket: int) -> str:
    if bucket < 10:
        return "new-origin"

    return "legacy-origin"
```

## 每一层缓存都要回答

需要重点检查：

- CDN 缓存键
- Cookie 分流信息
- Worker 路由
- 构建产物位置

### 缓存命中状态

可以检查响应头：

```text
cf-cache-status: HIT
age: 1278
```

## 探针要与用户同构

测试请求必须尽可能接近真实浏览器请求。

1. 使用相同的 User-Agent
2. 携带必要 Cookie
3. 使用正确 Host
4. 排除本地缓存

[^1]: 这里是一条脚注示例。
