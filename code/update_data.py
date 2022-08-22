import pandas as pd
import pickle
import browserhistory as bh
import os
from datetime import datetime
from read_browser_history import yt_video_content 
from doc_freq_vectorizer import doc_freq
from custom_logger import create_logger

logger = create_logger('../data/test.log',__name__)

def initiate_data():
    if not os.path.exists('../data/yt_watched_final_details.csv'):
        df = pd.DataFrame(columns=['vid_link','vid_title','description','tags','duration','channel_id','channel_name','meta_data','tokens'])
        df.to_csv('../data/yt_watched_final_details.csv',index=False)
    
    if not os.path.exists('../data/yt_shorts.csv'):
        df = pd.DataFrame(columns=['yt_shorts_link'])
        df.to_csv('../data/yt_shorts.csv',index=False)
    
    if not os.path.exists('../data/suggested_yt_videos.pickle'):
        suggested_vids=[]
        pickle.dump(suggested_vids, open("../data/suggested_yt_videos.pickle", "wb" ))

    if not os.path.exists('../data/invalid_videos.csv'):
        df = pd.DataFrame(columns=['invalid_vid_link'])
        df.to_csv('../data/invalid_videos.csv',index=False)
    
    if not os.path.exists('../data/buffer_topic_channels.csv'):
        df = pd.DataFrame(columns=['topic','channel_link','channel_status'])
        df.to_csv('../data/buffer_topic_channels.csv',index=False)
    
    if not os.path.exists('../buffer_topic_videos.csv'):
        df = pd.DataFrame(columns=['topic', 'vid_link', 'title', 'description', 'tags', 'duration', 
        'channel_id', 'channel_name', 'meta_data', 'tokens', 'channel_status', 'channel_link','token_score'])
        df.to_csv('../data/buffer_topic_videos.csv',index=False)
    
    if not os.path.exists('../data/watched_yt_videos.pickle'):
        watched_vids=[]
        pickle.dump(watched_vids,open('../data/watched_yt_videos.pickle','wb'))


def update_yt_watched_videos(watched_videos):
    bh.write_browserhistory_csv()
    df = pd.read_csv('chrome_history.csv',names=['links','title','timestamp'])
    test = df['links'].apply(lambda x:x if ('www.youtube.com' in x and 'watch?v=' in x and 'channel' not in x) else '')
    test = [x for x in test if len(x)>1]
    yt_vids = [x for x in test if x not in watched_videos]
    yt_vid_ids=[x.split('watch?v=')[1] if '&' not in x else x.split('watch?v=')[1].split('&')[0] for x in yt_vids]
    df_watched_vid_details = yt_video_content(yt_vid_ids)
    df_watched_vid_details.to_csv('../data/yt_watched_final_details.csv',mode='a',index=False,header=False)
    logger.info('--> Watched youtube videos updated.')

def update_pickle_files():
    df_watched_vid_details = pd.read_csv('../data/yt_watched_final_details.csv',usecols=['vid_link','channel_name','channel_id','tokens'])
    vid_list = df_watched_vid_details['vid_link'].tolist()
    pickle.dump(vid_list, open("../data/watched_yt_videos.pickle", "wb" ))
    channel_list = df_watched_vid_details['channel_name'].tolist()+df_watched_vid_details['channel_id'].tolist()
    pickle.dump(channel_list, open("../data/watched_channel_names_ids.pickle", "wb" ))
    vocab_dict = doc_freq(df_watched_vid_details['tokens'])
    pickle.dump(vocab_dict, open('../data/train_vocab_dict.pickle', 'wb'))
    logger.info('--> Pickle files updated.')

def update_csv_files():
    buffer_channels = pd.read_csv('../data/buffer_topic_channels.csv')
    buffer_videos = pd.read_csv('../data/buffer_topic_videos.csv')
    watched_channels = pickle.load(open('../data/watched_channel_names_ids.pickle','rb'))

    buffer_channel_ids = buffer_channels.loc[:,'channel_link'].apply(lambda x:x.split('/')[-1]) 
    updated_channel_status=[1 if id in watched_channels else 0 for id in buffer_channel_ids]
    buffer_channels['channel_status']=updated_channel_status
    buffer_channels.drop_duplicates(subset='channel_link',keep='last',inplace=True)
    buffer_channels.to_csv('../data/buffer_topic_channels.csv',index=False)

    buffer_video_channel_ids = buffer_videos.loc[:,'channel_link'].apply(lambda x:x.split('/')[-1])
    updated_channel_status=[1 if id in watched_channels else 0 for id in buffer_video_channel_ids]
    buffer_videos['channel_status']=updated_channel_status
    buffer_videos.drop_duplicates(subset='vid_link',keep='last',inplace=True)
    buffer_videos.to_csv('../data/buffer_topic_videos.csv',index=False)

    logger.info('--> Buffer csv files updated.')


if __name__=='__main__':
    watched_videos = pickle.load(open('../data/watched_yt_videos.pickle','rb'))
    yt_new = update_yt_watched_videos(watched_videos)
    print(yt_new)
