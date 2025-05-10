from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
import instaloader

# ---------- بخش تنظیمات ----------
SEARCH_KEYWORD = "iran"   # کلیدواژه جستجو
NUM_RESULTS = 20          # چند تا یوزرنیم اول رو بررسی کنه؟
WAIT_TIME = 2             # بین کلیک‌ها چند ثانیه صبر کنه؟

FILTERS = {
    "min_followers": 1000,
    "max_followers": 10000,
    "bio_keywords": ["iran", "digital"],
}

# ---------- راه‌اندازی مرورگر ----------
chrome_options = Options()
chrome_options.add_argument("--headless")  # برای اجرا بدون باز شدن پنجره مرورگر
driver = webdriver.Chrome(options=chrome_options)

print("🔍 در حال جستجوی یوزرنیم‌ها در اینستاگرام...")

driver.get(f"https://www.instagram.com/explore/search/keyword/?q={SEARCH_KEYWORD}")
time.sleep(3)

# اینستاگرام نیاز به لاگین دارد، پس از جستجو مستقیم استفاده نمی‌کنیم.
# به جای آن از موتور جستجوی Google استفاده می‌کنیم تا یوزرنیم پیدا کنیم:
driver.get(f"https://www.google.com/search?q=site:instagram.com+{SEARCH_KEYWORD}")
time.sleep(2)

links = driver.find_elements(By.CSS_SELECTOR, 'a')
usernames = []

for link in links:
    href = link.get_attribute('href')
    if href and "instagram.com" in href and "/p/" not in href:
        try:
            parts = href.split("/")
            uname = parts[3]
            if uname not in usernames and uname.isalnum():
                usernames.append(uname)
        except:
            continue
    if len(usernames) >= NUM_RESULTS:
        break

driver.quit()
print(f"✅ {len(usernames)} یوزرنیم پیدا شد: {usernames}")

# ---------- گرفتن اطلاعات با instaloader ----------
L = instaloader.Instaloader()
results = []

for username in usernames:
    try:
        profile = instaloader.Profile.from_username(L.context, username)
        bio = profile.biography.lower()

        # فیلتر
        if not (FILTERS["min_followers"] <= profile.followers <= FILTERS["max_followers"]):
            continue
        if not any(keyword in bio for keyword in FILTERS["bio_keywords"]):
            continue

        results.append({
            "Username": profile.username,
            "Full Name": profile.full_name,
            "Followers": profile.followers,
            "Following": profile.followees,
            "Bio": profile.biography,
            "External URL": profile.external_url,
        })
        print(f"[✔] Added: {username}")
        time.sleep(1)

    except Exception as e:
        print(f"[✘] Skipped {username}: {str(e)}")

# ---------- ذخیره خروجی ----------
df = pd.DataFrame(results)
df.to_excel("instagram_search_filtered.xlsx", index=False)
print("\n📦 ذخیره شد در فایل 'instagram_search_filtered.xlsx'")
