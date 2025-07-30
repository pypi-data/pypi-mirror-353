import aiohttp
import asyncpg

async def pg_get_guids_by_site_url(site_url, db_config):
    conn = await asyncpg.connect(
        host=db_config['host'],
        user=db_config['user'],
        password=db_config['password'],
        database=db_config['base']
    )
    try:
        rows = await conn.fetch("""
            SELECT e.guid
            FROM {prefix}entry e
            JOIN {prefix}feed f ON e.id_feed = f.id
            WHERE f.website = $1
        """.format(prefix=db_config['prefix']), site_url)
        return {row['guid'] for row in rows}
    finally:
        await conn.close()

async def api_get_links_by_site_url(freshrss_url, username, api_password, site_url, n):
    token = await api_get_freshrss_token(freshrss_url,username,api_password)
    headers = {
        'Authorization': f'GoogleLogin auth={token}'
    }
    async with aiohttp.ClientSession(headers=headers) as session:
        # Step 1: 获取订阅列表
        sub_url = f"{freshrss_url}/reader/api/0/subscription/list?output=json"
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
        content_url = f"{freshrss_url}/reader/api/0/stream/contents/{stream_id}?output=json&n={n}"
        async with session.get(content_url) as resp:
            resp.raise_for_status()
            data = await resp.json()
            items = data.get('items', [])
        # Step 4: 提取 guid
        links = {item.get("canonical", [{}])[0].get("href") for item in items}
        return links

async def api_get_freshrss_token(freshrss_url, username, password):
    login_url = f"{freshrss_url}/accounts/ClientLogin"
    data = {
        'Email': username,
        'Passwd': password
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(login_url, data=data) as resp:
            text = await resp.text()
            for line in text.splitlines():
                if line.startswith('Auth='):
                    return line[5:].strip()
    raise ValueError("无法获取 Auth token")

if __name__ == "__main__":
    import asyncio

    async def main():
        try:
            links = await api_get_links_by_site_url(
                freshrss_url='http://rss.example.com/api/greader.php',
                username='username',
                api_password='api_password',
                site_url="https://jandan.net/top#tab=3days",
                n = 100
            )
            print(links)
        except Exception as e:
            print(e)

        db_config = {
            'host': 'host',
            'user': 'user',
            'password': 'password',
            'base': 'base',
            'prefix': 'freshrss_userxxx_',
        }

        try:
            guids = await pg_get_guids_by_site_url(
                site_url="https://jandan.net/top#tab=3days",
                db_config = db_config
            )
            print(guids)
        except Exception as e:
            print(e)
            pass

    asyncio.run(main())
