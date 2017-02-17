import pandas as pd
headers = ['url','title','year','director','scenarist','actor','tp','state','language','time','runtime','name','link','related_info']

def drop_duplicates(file,encoding):
	df = pd.read_csv(file,encoding=encoding,names=headers)
	df = df.drop_duplicates(['url'])
	df.to_csv(file,index=False,encoding=encoding,header=False)

if __name__ == '__main__':
	drop_duplicates('moviedata.csv','utf-8')