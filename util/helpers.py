from aiohttp import ClientSession

async def fetch(url):
    async with ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                content = response.headers.get("Content-Type", "")
                if "application/json" in content:
                    return await response.json()
                else:
                    return await response.text()
            else:
                print(response.status)
                response.raise_for_status()


def bar(current, total):
    ratio = current / total
    position = int(ratio * 10)

    bar = ""
    for i in range(10):
        bar += "❍" if i == position else "-"

    mins, secs = divmod(int(current), 60)
    totalm, totals = divmod(int(total), 60)

    return f"{mins}:{secs:02} {bar} {totalm}:{totals:02}"
