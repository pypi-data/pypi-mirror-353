import sys
import webbrowser
import random
import asyncio
from playwright.async_api import async_playwright

async def quick_mode(genre):
    url = f"https://bandcamp.com/tag/{genre}?sort_field=pop"
    print(f"fetching albums tagged '{genre}' (quick mode)...")

    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=True)
        page = await browser.new_page()

        # block images, fonts, css for speed
        await page.route(
            "**/*",
            lambda route: route.abort() if route.request.resource_type in ["image", "stylesheet", "font"] else route.continue_()
        )

        await page.goto(url)
        try:
            await page.wait_for_selector("a[href*='/album/']", timeout=10000)
        except Exception:
            print("timeout waiting for albums to load.")
            await browser.close()
            sys.exit(1)

        album_links = await page.eval_on_selector_all(
            "a[href*='/album/']", "elements => elements.map(e => e.href)"
        )

        await browser.close()

    if not album_links:
        print("no albums found for this genre.")
        sys.exit(1)

    chosen = random.choice(album_links)
    print(f"selected album: {chosen}")
    webbrowser.open(chosen)


async def full_mode(genre):
    url = f"https://bandcamp.com/tag/{genre}?sort_field=pop"
    print(f"fetching albums tagged '{genre}' (full mode)...")

    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=True)
        page = await browser.new_page()

        # block images, fonts, css for speed
        await page.route(
            "**/*",
            lambda route: route.abort() if route.request.resource_type in ["image", "stylesheet", "font"] else route.continue_()
        )

        await page.goto(url)

        try:
            await page.wait_for_selector("a[href*='/album/']", timeout=10000)
        except Exception:
            print("timeout waiting for albums to load.")
            await browser.close()
            sys.exit(1)

        album_links = await page.eval_on_selector_all(
            "a[href*='/album/']", "elements => elements.map(e => e.href)"
        )

        if not album_links:
            print("no albums found for this genre.")
            await browser.close()
            sys.exit(1)

        chosen = random.choice(album_links)
        print(f"selected album: {chosen}")

        # go to album page for details
        await page.goto(chosen)
        await page.wait_for_load_state("networkidle")

        tralbum_data = await page.evaluate("window.TralbumData")
        album_title = tralbum_data.get("current", {}).get("title", "unknown")
        artist_name = tralbum_data.get("artist", "unknown")
        release_date = tralbum_data.get("album_release_date", "")

        if not release_date:
            release_date = await page.get_attribute("meta[itemprop='datePublished']", "content")

        if not release_date:
            release_date = "unknown"

        # trim time part if present
        if release_date != "unknown" and ":" in release_date:
            release_date = " ".join(release_date.split(" ")[:3])

        # fetch genres from page if possible
        genres = await page.eval_on_selector_all(
            "a.tag",
            "elements => elements.map(e => e.textContent.trim())"
        )
        genre_list = ", ".join(genres) if genres else "unknown"

        print(f"album: {album_title}")
        print(f"artist: {artist_name}")
        print(f"release date: {release_date}")
        print(f"genres: {genre_list}")

        await browser.close()

    open_choice = input("open this album in your browser? (y/n): ").strip().lower()
    if open_choice == "y":
        webbrowser.open(chosen)


async def main():
    if len(sys.argv) < 2:
        print("usage: pycamp <genre> [--quick|-q|--full|-f]")
        sys.exit(1)

    args = sys.argv[1:]
    mode = "quick"  # default is quick now

    if args[-1] in ("--quick", "-q", "--full", "-f"):
        flag = args[-1]
        args = args[:-1]
        if flag in ("--quick", "-q"):
            mode = "quick"
        else:
            mode = "full"

    if not args:
        print("error: no genre provided.")
        print("usage: pycamp <genre> [--quick|-q|--full|-f]")
        sys.exit(1)

    genre = "-".join(args).lower()

    if mode == "quick":
        await quick_mode(genre)
    else:
        await full_mode(genre)


def run():
    asyncio.run(main())