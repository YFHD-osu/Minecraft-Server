from datetime import datetime
from nbt import nbt
import requests
import msvcrt
import time
import os
import re

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from bs4 import BeautifulSoup

def formatUUID(uuid: str) -> str:
  return f"{uuid[0:8]}-{uuid[8:12]}-{uuid[12:16]}-{uuid[16:20]}-{uuid[20:]}"

def historyName(username: str, NBTfile: nbt.NBTFile, uuid: str) -> tuple:
  browser.get(f'https://namemc.com/search?q={username}')
  WebDriverWait(browser, 600).until(EC.presence_of_element_located((By.LINK_TEXT, "Log In")))
  if len(re.findall(r"Profiles: \d{0,} result", browser.page_source)) == 0: return (None, None)
  if "[Hidden Result]" in browser.page_source: return (None, None)
  # 查尋最後上線時間
  lastseen = datetime.fromtimestamp(int(str(NBTfile['Paper']['LastLogin'])) / 1000) if NBTfile.get('Paper') != None else uuid
  if rawInput(f"將 {username} 改為正版UUID? 最後上線時間 -> {lastseen} (Y/N) ", "YN") == "n": return (None, None)
  if "1 result" not in re.findall(r"Profiles: \d{0,} result", browser.page_source)[0]:
    WebDriverWait(browser, 600).until(EC.presence_of_element_located((By.ID, "play-pause-btn")))
  else:
    browser.get(f'https://namemc.com/profile/{username}.1')
    WebDriverWait(browser, 600).until(EC.presence_of_element_located((By.LINK_TEXT, "Log In")))
  soup = BeautifulSoup(browser.page_source, "html.parser")
  infoCard = soup.find("div", class_="row no-gutters align-items-center").text
  uuid = re.findall(r".{8}-.{4}-.{4}-.{4}-.{12}", infoCard)
  name = soup.find("h1", class_="text-nowrap").text
  return name, uuid[0]
  print(f"Name: {name}, UUID: {uuid[0]}")
  time.sleep(2000)

def main():
  for filename in os.listdir(PLAYERDATA_PATH):
    PLAYERDATA_FILE = os.path.join(PLAYERDATA_PATH, filename)
    if not os.path.isfile(PLAYERDATA_FILE): continue
    if '.dat_old' in PLAYERDATA_FILE: continue
    UUID = PLAYERDATA_FILE.split('\\')[-1].replace('.dat', '')
    ADVANCEMENTS_FILE = os.path.join(ADVANCEMENTS_PATH, f"{UUID}.json")

    nbtfile = nbt.NBTFile(f"{PLAYERDATA_FILE.split('/')[-1]}", 'rb')

    if nbtfile.get('bukkit') == None: # DAT文件中沒有記錄玩家名稱
      response = requests.get(f"https://sessionserver.mojang.com/session/minecraft/profile/{UUID}")
      if response.status_code != 200: continue # 這人非正版玩家
      if response.json()['id'] == UUID: continue # 文件的UUID已經正確
      os.rename(PLAYERDATA_FILE, f"{PLAYERDATA_PATH}/{formatUUID(response.json()['id'])}.dat")
      os.rename(ADVANCEMENTS_FILE, f"{ADVANCEMENTS_PATH}/{formatUUID(response.json()['id'])}.json")
      # print(f"[未知的名字] {UUID} -> {response.json()['id']} (玩家: {response.json()['name']})")
      continue

    response = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{nbtfile['bukkit']['lastKnownName']}")

    if response.json().get('id') == None: # 這人非正版(官方角度)玩家或是已經改名
      name, uuid = historyName(nbtfile['bukkit']['lastKnownName'], nbtfile, UUID)
      if name is None: continue # 這是盜版帳號(伺服器)，別動
      if UUID == uuid: continue # UUID已經正確，不改
      if os.path.exists(f"{PLAYERDATA_PATH}/{uuid}.dat"): 
        if rawInput(f"覆蓋 {nbtfile['bukkit']['lastKnownName']} 正版帳號? (Y/N) ", "YN") == "n": continue
        renameFile(UUID, uuid, True)
        continue
      renameFile(UUID, uuid, False)
      continue 

    if formatUUID(response.json()['id']) == UUID: continue # 文件的UUID已經正確
    if os.path.exists(f"{PLAYERDATA_PATH}/{formatUUID(response.json()['id'])}.dat"): 
      if rawInput(f"覆蓋 {UUID} -> {formatUUID(response.json()['id'])} ({nbtfile['bukkit']['lastKnownName']}) 正版帳號? (Y/N) ", "YN") == "n": continue
      renameFile(UUID, formatUUID(response.json()['id']), True)
      continue
    renameFile(UUID, formatUUID(response.json()['id']), False)
    continue

def renameFile(OLD_UUID:str, NEW_UUID: str, overwrite=None):
  overwrite = True
  newFiles = [
    f"{PLAYERDATA_PATH}/{NEW_UUID}.dat",    # 背包
    f"{ADVANCEMENTS_PATH}/{NEW_UUID}.json", # 成就
    f"{SLIMEFUN_PATH}/{NEW_UUID}.yml",      # 黏液科技
    f"{ESSENTIALS_PATH}/{NEW_UUID}.yml"     # 基礎插件
  ]
  oldFiles = [
    f"{PLAYERDATA_PATH}/{OLD_UUID}.dat",
    f"{ADVANCEMENTS_PATH}/{OLD_UUID}.json",
    f"{SLIMEFUN_PATH}/{OLD_UUID}.yml",
    f"{ESSENTIALS_PATH}/{OLD_UUID}.yml"
  ]

  if overwrite == None:
    return

  if overwrite: 
    for newFile in newFiles: 
      if os.path.exists(newFile): os.remove(newFile) # 刪除衝突檔案
  
  for i in range(0, len(newFiles)):
    if os.path.exists(oldFiles[i]): 
      try: os.rename(oldFiles[i], newFiles[i])
      except Exception as e: print(e)
    
  return

def rawInput(lore: str, acceptAnswer: str):
  print(lore+" ", end="")
  while True:
    reply = str(msvcrt.getch()).replace("b'", "").replace("'","").lower()
    if reply in acceptAnswer.lower(): break
  print(reply.upper())
  return reply

PLAYERDATA_PATH = '.\\playerdata'
ADVANCEMENTS_PATH = ".\\advancements"
SLIMEFUN_PATH = ".\\Players"
ESSENTIALS_PATH = ".\\userdata"
options = uc.ChromeOptions()
options.add_experimental_option("prefs", {"download.prompt_for_download":False, "download_restrictions": 3} )
options.headless = False

if __name__ == "__main__": 
  browser = uc.Chrome(options=options)
  main()