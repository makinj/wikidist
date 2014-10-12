import requests
import unidecode
import urllib
from flask import render_template
from flask import Flask
app = Flask(__name__)

def find_path(start_page, end_page):
  end_page = end_page.lower()
  queue = []
  benched_queue = [start_page]

  family_trie={start_page.lower():''}
  found=0
  while not found and (len(queue)>0 or len(benched_queue)>0):
    if len(queue)==0:
      queue = benched_queue
      benched_queue=[]
    to_search=queue
    if len(queue) > 50:
      to_search = queue[:50]
      queue = queue[50:]
    else:
      queue = []
    url = 'http://en.wikipedia.org/w/api.php?format=json&action=query&titles=%s&prop=revisions&rvprop=content' %(urllib.quote_plus('|'.join(to_search)))
    r = requests.get(url)
    pages = r.json()['query']['pages']
    for page in pages.keys():
      page_title = unidecode.unidecode(pages[page]['title']).lower()
      if int(page)<0:
        continue
      page_data = unidecode.unidecode(pages[page]['revisions'][0]['*'])
      link_start = page_data.find('[[')
      while link_start!=-1:
        link_end = page_data.find(']]', link_start)
        current_link = page_data[link_start+2:link_end].split('|')[0]
        current_link_low = current_link.lower()
        if current_link_low and current_link.find('File:')==-1 and current_link.find('Image:')==-1 and current_link_low not in family_trie:
          benched_queue.append(current_link)
          family_trie[current_link_low]=page_title
          if current_link_low==end_page:
            found=1
            break

        link_start = page_data.find('[[', link_end)
      if found:
        break
  if found:
    current = end_page
    results = []
    while current != '':
      results.append(current)
      current=family_trie[current]
    results.reverse()
    return results
  else:
    return "no link found"

@app.route("/path/<start>/<end>")
def path(start, end):
  start =unidecode.unidecode(start)
  end = unidecode.unidecode(end)
  print start
  print end
  path = find_path(start, end)
  results = ''
  if type(path) is str:
    results = path
  else:
    for node in path:
      results+= node
      if(node!=path[-1]):
        results += " -> "
  return results

@app.route("/")
def index():
  return render_template('index.html')

if __name__ == "__main__":
  app.run(host='0.0.0.0', port=8080)
