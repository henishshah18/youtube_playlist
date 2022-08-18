from email import parser
from urllib.error import HTTPError
import browserhistory as bh
import os
import pandas as pd
from requests import head
from googleapiclient.discovery import build
import nltk
# nltk.download('stopwords')
from nltk.corpus import stopwords
from datetime import datetime
import re
from ast import literal_eval
import configparser
from custom_logger import create_logger

logger = create_logger('../data/test.log',__name__)

def clean_text(x):
    # print('x:',x)
    try:
        clean_sent = [word.lower() for word in x.split() if word.lower() not in stopwords.words('english')]
        clean_sent = ' '.join(clean_sent)
        clean_sent = clean_sent.replace('\n',' ')
        clean_sent = re.sub('[^a-zA-Z0-9]', '', clean_sent)
        clean_sent = " ".join(clean_sent.split())
    except:
        clean_sent=''
    return clean_sent

def tokenizer(inp):
    if isinstance(inp,list): # for tags
        a=[clean_text(word) for x in inp for word in x.split() if word not in stopwords.words('english')]
        b=[word for word in a if word!=' ']
    elif isinstance(inp,str): # for titles
        a=[clean_text(word) for word in inp.split()]
        b=[word for word in a if not len(word)<=2]
    return b


def yt_video_content(yt_videos):

    config = configparser.ConfigParser()
    config.read('../data/config.ini')
    youtube = build('youtube','v3',developerKey=config['credentials']['developerKey'])

    skip_videos = pd.read_csv('../data/invalid_videos.csv')
    invalid_videos = skip_videos['invalid_vid_link'].tolist()

    video_details = pd.DataFrame(columns=['vid_link','title','description','tags','duration','channel_id','channel_name','meta_data'])
    yt_shorts = pd.DataFrame(columns=['yt_shorts_link'])
    links=[]
    titles=[]
    desc=[]
    tags=[]
    duration=[]
    meta_data=[]
    channel_id=[]
    channel_name=[]
    shorts=[]
    
    # df = pd.read_csv('yt_watched_final_details.csv')
    df_shorts = pd.read_csv('../data/yt_shorts.csv')
    for vid_id in yt_videos:
        shorts=[]
        if f'https://www.youtube.com/watch?v={vid_id}' not in invalid_videos and f'https://www.youtube.com/watch?v={vid_id}' not in df_shorts.yt_shorts_link:
        # if f'https://www.youtube.com/watch?v={yt_video}' not in invalid_videos and f'https://www.youtube.com/watch?v={yt_video}' not in df_shorts.yt_shorts_link:
            try:
                # yt_dict = youtube.videos().list(part='contentDetails,snippet,statistics',id=yt_video).execute()
                yt_dict = youtube.videos().list(part='contentDetails,snippet',id=vid_id).execute()
                duration_vid = yt_dict['items'][0]['contentDetails']['duration']
                if 'M' not in duration_vid or ('1M' in duration_vid and 'S' not in duration_vid) or duration_vid=='PT1M1S':
                    shorts.append(f'https://www.youtube.com/watch?v={vid_id}')
                    yt_shorts['yt_shorts_link']=shorts
                    yt_shorts.to_csv('../data/yt_shorts.csv',mode='a',header=False,index=False)
                    continue

                # print(f'For yt video https://www.youtube.com/watch?v={yt_video}')
                titles.append(yt_dict['items'][0]['snippet']['title'])
                links.append(f'https://www.youtube.com/watch?v={vid_id}')
                desc.append(yt_dict['items'][0]['snippet']['description'])
                duration.append(duration_vid)
                meta_data.append(str(yt_dict))
                channel_id.append(yt_dict['items'][0]['snippet']['channelId'])
                channel_name.append(yt_dict['items'][0]['snippet']['channelTitle'])
                tag = yt_dict['items'][0]['snippet']['tags']
                if isinstance(tag,str):
                    tag = literal_eval(tag)
                tags.append(tag)
                
                # break
            except KeyError as e:
                tags.append([])
            except Exception as e:
                new_invalid_video = pd.DataFrame([f'https://www.youtube.com/watch?v={vid_id}'],columns=['invalid_vid_link'])
                new_invalid_video.to_csv('../data/invalid_videos.csv',mode='a',index=False,header=False)
                logger.exception(e)
                continue
            
            
    # print(titles)
    video_details['vid_link']=links
    video_details['title']=titles
    video_details['description']=desc
    video_details['tags']=tags
    video_details['duration']=duration
    video_details['meta_data']=meta_data
    video_details['channel_id']=channel_id
    video_details['channel_name']=channel_name

    title_tokens = video_details.loc[:,'title'].apply(tokenizer)
    tag_tokens = video_details.loc[:,'tags'].apply(tokenizer)
    video_details['tokens']=title_tokens+tag_tokens

    # print(video_details)
    return video_details





if __name__=='__main__':

    if not os.path.exists('../data/chrome_history.csv') :
        bh.write_browserhistory_csv()
        df = pd.read_csv('chrome_history.csv',names=['links','title','timestamp'])
        test = df['links'].apply(lambda x:x.split('=')[1] if ('www.youtube.com' in x and 'watch?v=' in x) else '')
        test = [x for x in test if len(x)>1]
    # print(test)
    else:
        if (datetime.now()-datetime.fromtimestamp(os.path.getmtime('../data/chrome_history.csv'))).days>=1:
            bh.write_browserhistory_csv()
        df = pd.read_csv('../data/chrome_history.csv',names=['links','title','timestamp'])
        test = df['links'].apply(lambda x:x.split('=')[1] if ('www.youtube.com' in x and 'watch?v=' in x and 'channel' not in x) else '')
        test = [x for x in test if len(x)>1]
        # print(test)

    df = yt_video_content(test)

