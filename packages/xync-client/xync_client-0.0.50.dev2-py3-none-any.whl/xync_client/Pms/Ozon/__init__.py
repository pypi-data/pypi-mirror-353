from asyncio import run
from x_model import init_db
from xync_schema import models
from xync_client.loader import PG_DSN
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time


async def loggin(driver, agent) -> None:
    driver.get("https://finance.ozon.ru")
    for cookie in agent.state:
        driver.add_cookie(cookie)
    driver.get("https://finance.ozon.ru/lk")
    pin = agent.auth.get("code")
    actions = ActionChains(driver)
    for char in pin:
        actions.send_keys(char)
    actions.perform()


async def send_cred(driver, amount, payment, cred):
    pass


async def main():
    _ = await init_db(PG_DSN, models, True)
    agent = await models.PmAgent.filter(pm__norm="ozon", auth__isnull=False).first()
    chrome_options = uc.ChromeOptions()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    driver = uc.Chrome(options=chrome_options)

    try:
        if agent.state:
            await loggin(driver, agent)
            time.sleep(1000)
        else:
            driver.get("https://ozon.ru/ozonid-lite")
            driver.implicitly_wait(3)
            driver.find_element(By.NAME, "autocomplete").send_keys(agent.auth.get("phone"))
            driver.find_element(By.CLASS_NAME, "b201-a").click()
            sms_code = input("Введите 6-ти значный код: ")
            driver.implicitly_wait(3)
            driver.find_element(By.CLASS_NAME, "d01-a.d01-a5").send_keys(sms_code)
            driver.implicitly_wait(5)
            agent.state = driver.get_cookies()  # Получаем все куки
            await agent.save()

    finally:
        driver.quit()


if __name__ == "__main__":
    run(main())
