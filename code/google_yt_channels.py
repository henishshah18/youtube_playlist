from bs4 import BeautifulSoup
import requests
import re
import json
from read_browser_history import yt_video_content
import pandas as pd
import random
import lxml
from custom_logger import create_logger

logger = create_logger('../data/test.log',__name__)

def clean_lst(lst):
    final_lst=[]
    for i in lst:
        temp_lst = []
        for j in i:
            if isinstance(j,str) and j!=i[-1]:
                for k in j.split('.')[1:]:
                    if 'zx' not in k:
                        temp_lst.append(k)
                    else:
                        temp_lst.append(k.split('zx')[0])
            else:
                temp_lst.append(j)  

        final_lst.append(temp_lst)
    return final_lst

def find_yt_channels(inp):
    buffer_channels_df = pd.read_csv('../data/buffer_topic_channels.csv')
    buffer_channel_topics = buffer_channels_df['topic'].unique()
    if inp in buffer_channel_topics:
        yt_channel_links = buffer_channels_df[buffer_channels_df['topic']==inp]['channel_link'].tolist()

    else:
        a = 'https://www.google.com/search?q=top+youtube+channels+for+learning'
        for word in inp.split():
            a+= f'+{word}'
        # print(a)
        html_page = requests.get(a)
        # print(html_page)
        soup = BeautifulSoup(html_page.text, "lxml")
        # print(soup)
        links = []
        for link in soup.findAll('a'):
            try:
                if link.get('href').startswith('/url?q='):
                    clean_url = link.get('href').split('&sa')[0]
                    links.append(clean_url[7:])
            except:
                continue


        yt_channel_links = []
        combinations = ['youtube.com/c/','youtube.com/channel/','youtube.com/user/']
        for link in links:
            try:
                html_page = requests.get(link)
                soup = BeautifulSoup(html_page.text, "lxml")
                
                for link in soup.findAll('a'):
                    try:
                        if any(x in str(link.get('href')) for x in combinations):
                            channel_link = link.get('href')
                            if 'playlists' in channel_link:
                                channel_link = channel_link.replace('/playlists','')
                            elif 'featured' in channel_link:
                                channel_link = channel_link.replace('/featured','')
                            yt_channel_links.append(channel_link)

                        elif 'youtube.com/watch?v=' in link.get('href'):
                            yt_video_link = [link.get('href').split('/watch?v=')[1]]
                            video_details = yt_video_content(yt_video_link)
                            channel_id = video_details['channel_id'].values[0]
                            channel_link = f'https://www.youtube.com/channel/{channel_id}'
                            yt_channel_links.append(channel_link)
                    except:
                        continue
            except:
                continue
    return list(set(yt_channel_links))

def get_channel_ids(yt_channel_links):
    channel_ids = []
    pattern = ['playlists','videos','featured']
    for i in yt_channel_links:
        if i.split('/')[-1] in pattern:
            channel_ids.append(i.split('/')[-2])
        else:
            channel_ids.append(i.split('/')[-1])
    return channel_ids

def get_final_buffer_channels(topic,watched_channels,yt_channel_links,channel_ids):
    buffer_channels_dict = {'topic':[],'channel_link':[],'channel_status':[]}
    for id in range(len(channel_ids)):
        if id in watched_channels:
            buffer_channels_dict['topic'].append(topic)
            buffer_channels_dict['channel_link'].append(yt_channel_links[id])
            buffer_channels_dict['channel_status'].append(1)
        else:
            buffer_channels_dict['topic'].append(topic)
            buffer_channels_dict['channel_link'].append(yt_channel_links[id])
            buffer_channels_dict['channel_status'].append(0)

    buffer_channels_df = pd.DataFrame(buffer_channels_dict)
    return buffer_channels_df
    


def channel_top_videos(topic,buffer_channels_df,watched_videos):

    
    # this recursive function creates a list of key:key:...:value pairs for nested json files. this function used with clean_lst defined before
    # gives use a clean list of lists. 
    g = []
    def json_to_list(v, prefix=''):
        
        if isinstance(v, dict):
            for k, v2 in v.items():
                p2 = "{}.{}".format(prefix, k)
                json_to_list(v2, p2)           # recursive call
        elif isinstance(v, list):
            for i, v2 in enumerate(v):
                p2 = "{}zx{}zx".format(prefix, i)
                json_to_list(v2, p2)           # recursive call
        else:
            g.append(['{}'.format(prefix),v])
        return g  

    # for channel in yt_channels:
    def get_channel_top_videos(channel):
        yt_channel=[]
        yt_vid=[]
        try:
            if not '/videos' in channel:
                a = channel+'/videos?view=0&sort=p'
            else:
                a = channel+'?view=0&sort=p'
            html_page = requests.get(a)
            soup = BeautifulSoup(html_page.text, "lxml")
            rawJ = soup.find_all('script')
            J = str(rawJ[-7]) # The required json dict was found at this position for this problem statement
            J1 = J.split('var ytInitialData = ')
            J2 = J1[1].split(';',1)[0]
            s = json.loads(J2)
            b = [s]
            # print(s)
            key_val_pairs = clean_lst(json_to_list(b))
            n_max = 30
            for lst in key_val_pairs:
                if n_max<0:
                    break
                if isinstance(lst[-1],str) and 'watch?v' in lst[-1]:
                    yt_channel.append(a.split('/videos')[0])
                    yt_vid.append(f'https://www.youtube.com{lst[-1]}')
                    n_max-=1
        except Exception as e:
            print('This is an exception:',e)
        
        return yt_vid
        
    topic_watched_channels = buffer_channels_df[buffer_channels_df['channel_status']==1].loc[:,'channel_link'].tolist()
    topic_unwatched_channels = buffer_channels_df[buffer_channels_df['channel_status']==0].loc[:,'channel_link'].tolist()

    # print('Watched_channels:',topic_watched_channels)
    # print('Unwatched channels:',topic_unwatched_channels)
    
    final_channel_dict={1:{},0:{}}
    if len(topic_watched_channels)<2:
        if len(topic_watched_channels)==0:
            total_channels=5
            for channel in topic_unwatched_channels:
                g=[] #For each new channel, we get a different dictionary
                # print('Channel:',channel)
                if total_channels==0:
                    break
                unseen_vids = [x for x in get_channel_top_videos(channel) if x not in watched_videos]
                # print('Channel videos:',unseen_vids)
                if not len(unseen_vids)<5:
                    final_channel_dict[0][channel]=unseen_vids
                    total_channels-=1
                else:
                    continue
        elif len(topic_watched_channels)==1:
            g=[]
            channel=topic_watched_channels[0]
            unseen_vids = [x for x in get_channel_top_videos(channel) if x not in watched_videos]
            total_channels=5
            if not len(unseen_vids)<5:
                final_channel_dict[1][channel]=unseen_vids
                total_channels-=1
                for channel in topic_unwatched_channels:
                    g=[]
                    if total_channels==0:
                        break
                    unseen_vids = [x for x in get_channel_top_videos(channel) if x not in watched_videos]
                    if not len(unseen_vids)<5:
                        final_channel_dict[0][channel]=unseen_vids
                        total_channels-=1
                    else:
                        continue
            else:
                total_channels=5
                for channel in topic_unwatched_channels:
                    g=[]
                    if total_channels==0:
                        break
                    unseen_vids = [x for x in get_channel_top_videos(channel) if x not in watched_videos]
                    if not len(unseen_vids)<5:
                        final_channel_dict[0][channel]=unseen_vids
                        total_channels-=1
                    else:
                        continue
    elif len(topic_unwatched_channels)<3:
        if len(topic_unwatched_channels)==0:
            watched_channel_count=5
            for channel in topic_watched_channels:
                g=[]
                if watched_channel_count==0:
                    break
                unseen_vids = [x for x in get_channel_top_videos(channel) if x not in watched_videos]
                if not len(unseen_vids)<5:
                    final_channel_dict[1][channel]=unseen_vids
                    watched_channel_count-=1
                else:
                    continue
        
        elif len(topic_unwatched_channels)==1:
            watched_channel_count=4
            unwatched_channel_count=1
            for channel in topic_watched_channels:
                g=[]
                if watched_channel_count==0:
                    break
                unseen_vids = [x for x in get_channel_top_videos(channel) if x not in watched_videos]
                if not len(unseen_vids)<5:
                    final_channel_dict[1][channel]=unseen_vids
                    watched_channel_count-=1
                else:
                    continue
            
            for channel in topic_unwatched_channels:
                g=[]
                if unwatched_channel_count==0:
                    break
                unseen_vids = [x for x in get_channel_top_videos(channel) if x not in watched_videos]
                if not len(unseen_vids)<5:
                    final_channel_dict[0][channel]=unseen_vids
                    unwatched_channel_count-=1
                else:
                    continue
        elif len(topic_unwatched_channels)==2:
            watched_channel_count=3
            unwatched_channel_count=2
            for channel in topic_watched_channels:
                g=[]
                if watched_channel_count==0:
                    break
                unseen_vids = [x for x in get_channel_top_videos(channel) if x not in watched_videos]
                if not len(unseen_vids)<5:
                    final_channel_dict[1][channel]=unseen_vids
                    watched_channel_count-=1
                else:
                    continue
            
            for channel in topic_unwatched_channels:
                g=[]
                if unwatched_channel_count==0:
                    break
                unseen_vids = [x for x in get_channel_top_videos(channel) if x not in watched_videos]
                if not len(unseen_vids)<5:
                    final_channel_dict[0][channel]=unseen_vids
                    unwatched_channel_count-=1
                else:
                    continue
    else:
        watched_channel_count=2
        unwatched_channel_count=3
        for channel in topic_watched_channels:
            g=[]
            if watched_channel_count==0:
                break
            unseen_vids = [x for x in get_channel_top_videos(channel) if x not in watched_videos]
            if not len(unseen_vids)<5:
                final_channel_dict[1][channel]=unseen_vids
                watched_channel_count-=1
            else:
                continue
        
        for channel in topic_unwatched_channels:
            g=[]
            if unwatched_channel_count==0:
                break
            unseen_vids = [x for x in get_channel_top_videos(channel) if x not in watched_videos]
            if not len(unseen_vids)<5:
                final_channel_dict[0][channel]=unseen_vids
                unwatched_channel_count-=1
            else:
                continue
    return final_channel_dict


def buffer_videos_to_list(inp,watched_videos):
    buffer_videos = pd.read_csv('../data/buffer_topic_videos.csv')
    final_channel_dict={1:{},0:{}}
    watched_channel_videos = buffer_videos.loc[(buffer_videos['topic']==inp)&(buffer_videos['channel_status']==1)&(~buffer_videos['vid_link'].isin(watched_videos)),:]
    unwatched_channel_videos = buffer_videos.loc[(buffer_videos['topic']==inp)&(buffer_videos['channel_status']==0)&(~buffer_videos['vid_link'].isin(watched_videos)),:]

    if len(watched_channel_videos)+len(unwatched_channel_videos)>10:
        if watched_channel_videos.channel_link.nunique()!=0:
            if watched_channel_videos.channel_link.nunique()==1 and len(watched_channel_videos)>=3: # if there is only one watched channel then the number of unwatched videos in it should be atleast 3
                for channel_link,temp_df in watched_channel_videos.groupby('channel_link'):
                    final_channel_dict[1][channel_link] = temp_df.vid_link.tolist()
                
                n_unwatched_channels=4
                for channel_link,temp_df in unwatched_channel_videos.groupby('channel_link'):
                    if n_unwatched_channels==0:
                        break
                    final_channel_dict[0][channel_link] = temp_df.vid_link.tolist()
                    n_unwatched_channels-=1

            elif watched_channel_videos.channel_link.nunique()==1 and len(watched_channel_videos)<3:    
                n_unwatched_channels=5
                for channel_link,temp_df in unwatched_channel_videos.groupby('channel_link'):
                    if n_unwatched_channels==0:
                        break
                    final_channel_dict[0][channel_link] = temp_df.vid_link.tolist()
                    n_unwatched_channels-=1
            
            else:
                n_watched_channels = 2
                n_unwatched_channels = 3
                for channel_link,temp_df in watched_channel_videos.groupby('channel_link'):
                    if n_watched_channels==0:
                        break
                    final_channel_dict[1][channel_link] = temp_df.vid_link.tolist()
                    n_watched_channels-=1
                for channel_link,temp_df in unwatched_channel_videos.groupby('channel_link'):
                    if n_unwatched_channels==0:
                        break
                    final_channel_dict[0][channel_link] = temp_df.vid_link.tolist()
                    n_unwatched_channels-=1
            return final_channel_dict
        else:
            n_unwatched_channels=5
            for channel_link,temp_df in unwatched_channel_videos.groupby('channel_link'):
                if n_unwatched_channels==0:
                    break
                final_channel_dict[0][channel_link] = temp_df.vid_link.tolist()
                n_unwatched_channels-=1
            return final_channel_dict
           
    else:
        return 0   
        

                

    

if __name__=='__main__':

    inp = input('What would you like to learn about today?:')
    yt_channels = find_yt_channels(inp)
    top_channels = yt_channels[:1]
    buffer_channels = yt_channels[1:]
    yt_channel,yt_vid = channel_top_videos(top_channels)
    yt_vid = list(set(yt_vid))
    yt_vid_id=[x.split('watch?v=')[1] for x in yt_vid]
    
    print(top_channels)
    print('*'*150)
    print(yt_vid)
    print(len(yt_channel))
    print(len(yt_vid))
    print(len(buffer_channels))
    print('*'*150)

    df_vid_details = yt_video_content(yt_vid_id)
    print(df_vid_details)
    # def search_by_country():
    #     return




