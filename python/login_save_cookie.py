import asyncio
from twikit import Client

async def main():
    client = Client('ja')

    # ログイン（asyncなので await が必要）
    await client.login(
        auth_info_1='bemvh543oi@sute.jp',
        auth_info_2='nairo_sub',
        password='hiro0716'
    )

    # cookies.json を保存
    client.save_cookies('cookies.json')
    print("cookies.json を保存しました")

# asyncio で実行
asyncio.run(main())
