from lxml import html
import aiohttp
from asyncio import get_event_loop
import regex as re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://secure.meetcontrol.com/",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
}


class main():
	def __init__(self):
		self.finalData = []
		self.run_extractor()

	def run_extractor(self):
		meetNums = self.getInputs()
		eventLinks = self.get_event_links(meetNums)
		self.getData(eventLinks)
		dataList = self.getDataList(self.finalData)
		self.output_info(dataList)


	def get_event_links(self, meetNums):
		"""Gets the event links from the meet pages"""
		eventLinks = []
		for meetNum in meetNums:
			url = f'https://secure.meetcontrol.com/divemeets/system/meetresultsext.php?meetnum={meetNum}'
			page_source = self.get_page_source(url)
			print(page_source)
			temptree = html.fromstring(page_source)
			table = temptree.xpath('//table[@width = "100%"]')[0]
			for b in table.xpath('tr[@bgcolor = "DDDDDD" or @bgcolor = "FFFFFF"]'):
				print(b)
				if len(b.xpath('td/a')) != 0:
					eventLinks.append(str(b.xpath('td/a')[0].get('href')))
		return eventLinks
	
	@staticmethod
	def get_page_source(url: str):
		service = Service(ChromeDriverManager().install())
		options = webdriver.ChromeOptions()
		options.add_argument("--headless=new")
		options.add_argument("--disable-gpu")
		options.add_argument("--no-sandbox")
		options.add_argument("--disable-dev-shm-usage")
		options.add_argument("--window-size=1920,1080")
		options.add_argument("--disable-blink-features=AutomationControlled")
		options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")
		driver = webdriver.Chrome(service=service, options=options)
		driver.get(url)
		try:
			WebDriverWait(driver, 15).until(
				EC.presence_of_element_located((By.XPATH, '//table[@width = "100%"]'))
			)
		except Exception:
			pass
		source = driver.execute_script("return document.documentElement.outerHTML")
		driver.quit()
		return source



	def getData(self, eventLinks):
		"""Runs the event loop so we can asynchronously get pages and parse them"""
		get_event_loop().run_until_complete(self.getpages(eventLinks))


	async def get_page(self, session, link):
		"""Asynchronously requests pages html content"""
		async with session.get(link, ssl = False) as page:
			return await page.read()


	async def getpages(self, eventLinks):
		"""Parses the information within the html"""
		async with aiohttp.ClientSession(headers=HEADERS) as session:
			for eventLink in eventLinks:
				htmlforpage = await self.get_page(session, f'https://secure.meetcontrol.com/divemeets/system/{eventLink}')
				temptree = html.fromstring(htmlforpage)
				table = temptree.xpath('//table[@width = "100%"]')[0]
				self.finalData += self.parse_html(table)


	def try_linked_html(self, element):
		try:
			return element.xpath('a/text()')[0]
		except:
			pass
		try:
			return element.xpath('text()')[0]
		except:
			return 'unable to parse'

	def parse_html(self, table):
		individualData = []
		meet = table.xpath('tr[1]/td/strong/a/text()')[0]

		if meet.find('Region') >= 0:
			meet = re.search('Region ([0-9]{1,2})', meet).groups()[0]
		if meet.find('Zone') >= 0:
			meet = re.search('Zone ([ABCDEF])', meet).groups()[0]

		event = table.xpath('tr[3]/td/strong/text()')[0]
		for row in table.xpath('tr[position() > 5 and position() < last()]'):
			name = self.try_linked_html(row.xpath('td[1]')[0])
			team = self.try_linked_html(row.xpath('td[2]')[0])
			place = self.try_linked_html(row.xpath('td[3]')[0])
			score = self.try_linked_html(row.xpath('td[4]')[0])

			individualData.append({'meet': meet, 'event': event, 'name': name, 'team': team, 'place': place, 'score': score})
		return individualData


	def getDataList(self, individualData):
		for i in range(0, len(individualData)):
			info = individualData[i]
			individualData[i] = f"{info['name']}|{info['team']}|{info['place']}|{info['score']}|{info['event']}|{info['meet']}\n"
		return individualData
	

	def output_info(self, data):
		file = input('To what file would you like to save?(Defaults to output)')
		if len(file) == 0:
			file = 'output'

		with open(file+'.txt', 'w') as file:
			file.write('name team place score event meet\n')
			file.writelines(data)


	def getInputs(self):
		command = input("Which meets would you like to look at?(input meetnumbers or filename(defaults to Input))")
		if len(command) == 0:
			command = 'input'
		
		if not re.search("^[0-9]{4}", command):
			command = open(f'{command}.txt', 'r').read()
		
		templist = []
		while True:
			match = re.search("([0-9]{4,5})[\\n ,|-]*", command)
			if match:
				templist.append(match.groups()[0])
				command = command[len(match.groups()[0]) + 1:]
			else:
				return templist


object = main()

input('Task completed. Press any button to continue...')