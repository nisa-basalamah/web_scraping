from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

#insert the scrapping here
url_get = requests.get('https://www.imdb.com/search/title/?release_date=2019-01-01,2019-12-31')
soup = BeautifulSoup(url_get.content,"html.parser")

movie_list = soup.find('div', attrs={'class':'lister list detail sub-list'})
list_content = movie_list.find_all('div', attrs={'class':'lister-item-content'})

#title
header = []
for i in range(0, len(list_content)):
    get_header = list_content[i].find_all('h3', attrs={'class':'lister-item-header'})
    header.append(get_header)
header[:2]

#runtime and genre
runtime_and_genre = []
for i in range(0, len(list_content)):
    get_runtime_and_genre = list_content[i].find_all('p', attrs={'class':'text-muted'})[0]
    runtime_and_genre.append(get_runtime_and_genre)
runtime_and_genre[:2]

#imdb rating
ratings = []
for i in range(0, len(list_content)):
    get_ratings = list_content[i].find_all('div', attrs={'class':'inline-block ratings-imdb-rating'})
    ratings.append(get_ratings)
ratings[:2]

#metascore
ratings_metascore = []
for i in range(0, len(list_content)):
    get_ratings_metascore = list_content[i].find_all('div', attrs={'class':'inline-block ratings-metascore'})
    ratings_metascore.append(get_ratings_metascore)
ratings_metascore[:4]

#votes
num_votes = []
for i in range(0, len(list_content)):
    get_num_votes = list_content[i].find_all('p', attrs={'class':'sort-num_votes-visible'})
    num_votes.append(get_num_votes)
num_votes[:2]

temp = [] #initiating a tuple

for i in range(0, len(list_content)):
#insert the scrapping process here
    #get title
    title = header[i][0].find('a').text
    
    #get runtime
    runtime = runtime_and_genre[i].find('span', attrs={'class':'runtime'})
    
    if (runtime != None):
        runtime = runtime.text
        
    #getruntime
    genre = runtime_and_genre[i].find('span', attrs={'class':'genre'}).text
    genre = genre.strip() #for removing the excess whitespace
    genre = genre.replace(' ', '').split(',')

    #get imdb rating
    imdb_rating = ratings[i][0].find('strong').text
    
    #get metascore
    if (len(ratings_metascore[i])):
        metascore = ratings_metascore[i][0].find('span').text
        metascore = metascore.strip()
    else:
        metascore = None
        
    #get votes
    votes = num_votes[i][0].find('span', attrs={'name':'nv'}).text
    
    for j in range(0, len(genre)):
        temp.append((title, runtime, genre[j], imdb_rating, metascore, votes))

#change into dataframe
df = pd.DataFrame(temp, columns=('Title', 'Runtime (min)', 'Genre', 'IMDb Rating', 'Metascore', 'Votes'))

#insert data wrangling here
df['Runtime (min)'] = df['Runtime (min)'].str.replace('min', '')
df['Votes'] = df['Votes'].str.replace(',', '')

df[['Runtime (min)', 'Metascore']] = df[['Runtime (min)', 'Metascore']].fillna(0)

#convert to category
df['Genre'] = df['Genre'].astype('category')

#convert to integer
df[['Runtime (min)', 'Metascore', 'Votes']] = \
df[['Runtime (min)', 'Metascore', 'Votes']].astype('int64')

#convert to float
df['IMDb Rating'] = df['IMDb Rating'].astype(float)

top7 = df.drop('Genre', axis=1).drop_duplicates()[:7]

top7_genre = df.set_index('Title')['Genre']
top7_genre = top7_genre.loc[:'The Witcher'].reset_index()
#end of data wranggling 

@app.route("/")
def index(): 
	
	card_data = f'{top7["Title"][0]}'

	# generate plot
	ax = top7.sort_values('Votes').plot(kind='barh', x='Title', y='Votes', figsize = (20,9))
	
	
	# Rendering plot
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result = str(figdata_png)[2:-1]
	
	# generate plot2
	ax2 = top7.sort_values('IMDb Rating').plot(kind='barh', x='Title', y='IMDb Rating', figsize = (20,9))
	
	# Rendering plot2
	figfile2 = BytesIO()
	plt.savefig(figfile2, format='png', transparent=True)
	figfile2.seek(0)
	figdata2_png = base64.b64encode(figfile2.getvalue())
	plot_result2 = str(figdata2_png)[2:-1]

	# render to html
	return render_template('index.html',
		card_data = card_data, 
		plot_result=plot_result,
		plot_result2=plot_result2
		)


if __name__ == "__main__": 
    app.run(debug=True)
