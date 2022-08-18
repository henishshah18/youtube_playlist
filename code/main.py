from bs4 import BeautifulSoup
from read_browser_history import yt_video_content
from google_yt_channels import find_yt_channels,get_channel_ids,get_final_buffer_channels,channel_top_videos,buffer_videos_to_list
import pandas as pd
from doc_freq_vectorizer import create_df_for_vect,doc_freq,corpus_doc_freq,df_vectorizer
import pickle
import numpy as np
from create_playlist import load_credentials,initiate_playlist,add_videos_to_playlist
from update_data import update_yt_watched_videos,update_pickle_files,update_csv_files
pd.options.mode.chained_assignment = None
from custom_logger import create_logger

logger = create_logger('../data/test.log',__name__)

watched_videos = pickle.load(open('../data/watched_yt_videos.pickle','rb'))
update_yt_watched_videos(watched_videos)
update_pickle_files()
update_csv_files()

watched_channels = pickle.load(open('../data/watched_channel_names_ids.pickle','rb'))
watched_videos = pickle.load(open('../data/watched_yt_videos.pickle','rb'))
suggested_videos = pickle.load(open('../data/suggested_yt_videos.pickle','rb'))

watched_and_suggested_videos = watched_videos+suggested_videos

buffer_videos = pd.read_csv('../data/buffer_topic_videos.csv')

inp = input('What would you like to learn about today?:  ')
inp=inp.lower()

channel_vid_dict = buffer_videos_to_list(inp,watched_and_suggested_videos)
final_video_list = []
# print(channel_vid_dict)

if channel_vid_dict!=0:
    for status,channel_dict in channel_vid_dict.items():
        for channel,videos in channel_dict.items():
            # yt_vid_id=[x.split('watch?v=')[1] for x in videos]
            df_vid_details = buffer_videos.loc[buffer_videos['vid_link'].isin(videos),:]
            # print(df_vid_details)

            df_vect = df_vid_details[['duration','tokens']]
            df = create_df_for_vect(df_vect)

            vocab_dict = pd.read_pickle('../data/train_vocab_dict.pickle')
            corpus_doc_dict = corpus_doc_freq(df['tokens'],vocab_dict)
            vec = df_vectorizer(df['tokens'],vocab_dict,corpus_doc_dict)
            df_vid_details.loc[:,'token_score']=vec.sum(axis=1)
            df_vid_details.sort_values(by='token_score',inplace=True,ascending=False)

            top_videos = df_vid_details.vid_link.tolist()[:2]
            final_video_list+=top_videos
 
else:
    yt_channels = find_yt_channels(inp)
    channel_ids = get_channel_ids(yt_channels)
    buffer_channel_df = get_final_buffer_channels(inp.lower(),watched_channels,yt_channels,channel_ids)
    buffer_channel_df.to_csv('../data/buffer_topic_channels.csv',mode='a',header=False,index=False)
    channel_vid_dict = channel_top_videos(inp.lower(),buffer_channel_df,watched_and_suggested_videos)

    # print('Channels collected:',list(channel_vid_dict[0].keys())+list(channel_vid_dict[1].keys()))
    yt_vids = [yt_vid for x in list(channel_vid_dict[0].values())+list(channel_vid_dict[1].values()) for yt_vid in x]
    # print(len(set(yt_vids)))
    # print('Total videos collected:',len(yt_vids))

    for status,channel_dict in channel_vid_dict.items():
        for channel,videos in channel_dict.items():
            yt_vid_id=[x.split('watch?v=')[1] if '&' not in x else x.split('watch?v=')[1].split('&')[0] for x in videos]
            df_vid_details = yt_video_content(yt_vid_id)
            if status==1:
                channel_status = np.ones((len(df_vid_details,)))
                df_vid_details['channel_status']=channel_status
            elif status==0:
                channel_status = np.zeros((len(df_vid_details,)))
                df_vid_details['channel_status']=channel_status
            
            df_vid_details.insert(0, 'topic', [inp.lower()]*len(df_vid_details))
            df_vid_details['channel_link'] = [channel]*len(df_vid_details)

            df_vect = df_vid_details[['duration','tokens']]
            df = create_df_for_vect(df_vect)

            vocab_dict = pd.read_pickle('../data/train_vocab_dict.pickle')
            corpus_doc_dict = corpus_doc_freq(df['tokens'],vocab_dict)
            vec = df_vectorizer(df['tokens'],vocab_dict,corpus_doc_dict)
            df_vid_details.loc[:,'token_score']=vec.sum(axis=1)
            df_vid_details.sort_values(by='token_score',inplace=True,ascending=False)
            df_vid_details.to_csv('../data/buffer_topic_videos.csv',mode='a',header=False,index=False)

            top_videos = df_vid_details.vid_link.tolist()[:2]
            final_video_list+=top_videos


# print(final_video_list)
suggested_videos+=final_video_list
# print('Suggested videos:',suggested_videos)
pickle.dump(suggested_videos,open('../data/suggested_yt_videos.pickle','wb'))
yt_vid_ids=[x.split('watch?v=')[1] if '&' not in x else x.split('watch?v=')[1].split('&')[0] for x in final_video_list]
credentials = load_credentials()
try:
    playlist_dict = initiate_playlist(inp,credentials)
    add_videos_to_playlist(yt_vid_ids,playlist_dict,credentials)
except Exception as e:
    logger.exception(e)
    print('Sorry, our resources have exhausted for the day!')

        
            

        

