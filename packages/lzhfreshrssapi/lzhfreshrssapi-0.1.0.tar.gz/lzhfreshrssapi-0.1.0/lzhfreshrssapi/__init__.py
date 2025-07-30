import aiohttp

async def get_guids_by_site_url(freshrss_url, username, app_password, site_url):
    auth = aiohttp.BasicAuth(username, app_password)

    async with aiohttp.ClientSession(auth=auth) as session:
        # Step 1: 获取订阅列表
        sub_url = f"{freshrss_url}/api/greader/api/0/subscription/list?output=json"
        async with session.get(sub_url) as resp:
            resp.raise_for_status()
            data = await resp.json()
            subscriptions = data.get('subscriptions', [])

        # Step 2: 查找 htmlUrl 匹配
        stream_id = None
        for sub in subscriptions:
            if sub.get('htmlUrl') == site_url:
                stream_id = sub.get('id')
                break

        if not stream_id:
            raise ValueError("找不到匹配的订阅源")

        # Step 3: 获取该 stream 的内容
        content_url = f"{freshrss_url}/api/greader/api/0/stream/contents/{stream_id}?output=json"
        async with session.get(content_url) as resp:
            resp.raise_for_status()
            data = await resp.json()
            items = data.get('items', [])

        # Step 4: 提取 guid
        guids = {item['id'] for item in items if 'id' in item}
        return guids
