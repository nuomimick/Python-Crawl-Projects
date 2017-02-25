import pandas as pd
headers = ['url','title','year','director','scenarist','actor','tp','state','language','time','runtime','name','link','related_info']

def drop_duplicates(file,encoding):
	df = pd.read_csv(file,encoding=encoding,names=['url','user_name','user_url','saw','rating','time','content'])
	print(len(df.drop_duplicates(['content'])))
	# df.to_csv(file,index=False,encoding=encoding,header=False)
	
	

if __name__ == '__main__':
	drop_duplicates('comments.csv','utf-8')
	