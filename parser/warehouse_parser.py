"""
Парсер email-адресов складов Москвы.
Ищет сайты через Яндекс/Google, затем извлекает email с каждого сайта.
Результат сохраняется в results.csv
"""

import re
import csv
import time
import random
import logging
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ru-RU,ru;q=0.9",
}

EMAIL_RE = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")

# Стартовые сайты-каталоги складов Москвы
SEED_URLS = [
    "https://skladovoy.ru/katalog-skladov/moskva/",
    "https://www.skladman.ru/warehouses/moskva/",
    "https://www.cian.ru/snyat-sklad-moskva/",
    "https://www.avito.ru/moskva/kommercheskaya_nedvizhimost/sklady-ASgBAgICAkSUA~KABg?s=104",
    "https://warehouses.ru/catalog/moskva/",
    "https://ru.kompass.com/searchCompany?r=RU&activity=sklady-hranenie&city=moskva",
    "https://yandex.ru/maps/?text=склад+аренда+Москва&type=biz",
]

# Дополнительные прямые сайты складских компаний
DIRECT_SITES = [
    "https://www.logistic-center.ru/contact",
    "https://www.skladlogistic.ru/contacts",
    "https://www.fml.ru/contact",
    "https://www.pk-logistika.ru/contacts/",
    "https://www.omni-logistic.ru/contacts",
    "https://technopark.ru/contact",
    "https://www.skladpro.ru/contact",
    "https://www.msk-sklad.ru/kontakty",
    "https://www.roslogistics.ru/contacts",
    "https://northway.ru/contacts/",
    "https://www.megalogix.ru/kontakty/",
    "https://www.skladovoy.ru/kontakty",
    "https://www.rentasklad.ru/contacts",
    "https://www.sklady-online.ru/contacts",
    "https://www.sklad-msk.ru/kontakty/",
]

CONTACT_KEYWORDS = ["contact", "kontakt", "about", "о нас", "контакт", "связь", "почта"]

SESSION = requests.Session()
SESSION.headers.update(HEADERS)


def get_page(url: str, timeout: int = 10) -> str | None:
    try:
        r = SESSION.get(url, timeout=timeout, allow_redirects=True)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except Exception as e:
        log.warning(f"Ошибка загрузки {url}: {e}")
        return None


def extract_emails(html: str) -> set[str]:
    emails = set(EMAIL_RE.findall(html))
    # Фильтруем мусор (картинки, шрифты, примеры)
    return {
        e.lower() for e in emails
        if not any(e.endswith(ext) for ext in [".png", ".jpg", ".gif", ".svg", ".woff"])
        and "example" not in e
        and "domain" not in e
    }


def find_contact_links(html: str, base_url: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"].lower()
        text = a.get_text(strip=True).lower()
        if any(kw in href or kw in text for kw in CONTACT_KEYWORDS):
            full = urljoin(base_url, a["href"])
            if urlparse(full).netloc == urlparse(base_url).netloc:
                links.append(full)
    return list(set(links))


def scrape_site(url: str) -> dict:
    domain = urlparse(url).netloc
    log.info(f"Парсим: {url}")

    html = get_page(url)
    if not html:
        return {}

    emails = extract_emails(html)

    # Ищем страницу контактов если email не нашли
    if not emails:
        contact_links = find_contact_links(html, url)
        for link in contact_links[:3]:
            time.sleep(random.uniform(1, 2))
            contact_html = get_page(link)
            if contact_html:
                emails |= extract_emails(contact_html)
            if emails:
                break

    if emails:
        log.info(f"  ✓ {domain} → {emails}")
        return {"domain": domain, "url": url, "emails": ", ".join(sorted(emails))}

    log.info(f"  — {domain}: email не найден")
    return {}


def save_csv(results: list[dict], filename: str = "results.csv"):
    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["domain", "url", "emails"])
        writer.writeheader()
        writer.writerows(results)
    log.info(f"\nСохранено: {filename} ({len(results)} записей)")


def main():
    results = []
    seen_domains = set()

    all_urls = DIRECT_SITES[:]

    for url in all_urls:
        domain = urlparse(url).netloc
        if domain in seen_domains:
            continue
        seen_domains.add(domain)

        data = scrape_site(url)
        if data:
            results.append(data)

        time.sleep(random.uniform(1.5, 3.0))

    save_csv(results)
    print(f"\n✅ Готово! Найдено email-адресов: {len(results)}")
    print("📁 Результат в файле: results.csv")


if __name__ == "__main__":
    main()
