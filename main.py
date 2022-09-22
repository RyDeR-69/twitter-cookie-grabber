import asyncio

from loguru import logger
from os.path import exists
from itertools import cycle
from playwright.async_api import async_playwright, TimeoutError


def format_proxy(proxy: str) -> dict | None:
    return None if not proxy else {
        "server": f"http://{':'.join(proxy.split(':')[-2:])}",
        "username": proxy.split("@")[0].split(":")[1].strip("//"),
        "password": proxy.split("@")[0].split(":")[2]
    }


async def grabber(
        login: str,
        pwd: str,
        extra_data: str = None,
        proxy: str = None,
        ua: str = None
) -> None:
    try:
        async with async_playwright() as p:
            # timeout, slow_mo may be changed in ydependent of threads amount
            browser = await p.firefox.launch(
                headless=False,
                proxy=format_proxy(proxy),
                slow_mo=750,
                timeout=120 * 60
            )
            context = await browser.new_context(user_agent=ua)
            page = await context.new_page()

            await page.goto("https://twitter.com/i/flow/login", timeout=120 * 60)
            await page.locator("input[name=\"text\"]").fill(login)
            await page.locator("div[role=\"button\"]:has-text(\"Next\")").click()
            await page.locator("input[name=\"password\"]").fill(pwd)
            await page.locator("[data-testid=\"LoginForm_Login_Button\"]").click()
            if extra_data:
                try:
                    # timeout may be changed in dependent of threads amount
                    await page.wait_for_selector("[data-testid=\"ocfEnterTextTextInput\"]", timeout=30 * 60)
                    await page.locator("[data-testid=\"ocfEnterTextTextInput\"]").click()
                    await page.locator("[data-testid=\"ocfEnterTextTextInput\"]").fill(extra_data)
                    async with page.expect_navigation():
                        await page.locator("[data-testid=\"ocfEnterTextNextButton\"]").click()
                except TimeoutError:
                    pass
            # random sleep
            await asyncio.sleep(2.5)

            # save cookies
            await context.storage_state(path=f"cookies/{login}.json")
            print(f"{login}: grabbed")

            # -----------------------end----------------------- #

            await context.close()
            await browser.close()
    except Exception as e:
        logger.exception(f"{login} ERROR | {e}")


async def wrapper(queue: asyncio.Queue) -> bool | None:
    while True:
        [login, pwd, extra_data], proxy, ua = await queue.get()
        await grabber(
            login=login,
            pwd=pwd,
            extra_data=extra_data,
            proxy=proxy,
            ua=ua
        )

        if queue.empty():
            return True


async def create_task() -> None:
    queue = asyncio.Queue()

    for items in zip(data, cycle(proxies), cycle(user_agents)):
        queue.put_nowait(items)

    tasks = [asyncio.create_task(wrapper(queue)) for _ in range(threads)]

    await asyncio.gather(*tasks)


def format_data(user_data: list[str]) -> list[list[str | None]]:
    if optional_data:
        return [[items.split(":")[0], items.split(":")[1], items.split(":")[2]] for items in user_data]
    return [[items.split(":")[0], items.split(":")[1], None] for items in user_data]


if __name__ == '__main__':
    user_agents, proxies, optional_data = [None], [None], False
    data = list(filter(bool, open("data/twitter_pass.txt").read().strip().split("\n")))

    if exists("data/proxy.txt"):
        proxies = list(filter(bool, open("data/proxy.txt").read().strip().split("\n")))
    if exists("data/ua_list.txt"):
        user_agents = list(filter(bool, open("data/ua_list.txt").read().strip().split("\n")))

    if input("have optional data (y/skip) >>> "):
        optional_data = True

    data = format_data(data)

    threads = int(input("threads >>> "))

    asyncio.run(create_task())
