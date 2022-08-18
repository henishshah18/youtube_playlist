import pandas as pd
import pickle
# import configparser

# config_writer = configparser.ConfigParser()

# config_writer['credentials'] = {'developerKey':'AIzaSyBb1xI4gzTMZjxvVGQqxBst3fzrv7Ikqi8'}

# with open('config.ini','w') as config_details:
#     config_writer.write(config_details)
# df_og = pd.read_csv('yt_watched_final_details.csv',usecols=['vid_link'])
# vid_list = df_og['vid_link'].tolist()
# pickle.dump(vid_list, open("watched_yt_videos.pickle", "wb" ))

# suggested_vids=[]
# pickle.dump(suggested_vids, open("suggested_yt_videos.pickle", "wb" ))

# df = pd.DataFrame(columns=['topic', 'vid_link', 'title', 'description', 'tags', 'duration',
#        'channel_id', 'channel_name', 'meta_data', 'tokens', 'channel_status', 'channel_link','token_score'])
# df.to_csv('buffer_topic_videos.csv',index=False)

# df = pd.read_csv('buffer_topic_videos.csv')
# df.drop_duplicates(subset=['vid_link'],keep='last',inplace=True)
# # print(len(df))
# df.to_csv('buffer_topic_videos.csv',index=False)

# df = pd.DataFrame(columns=['topic','channel_link','channel_status'])
# df.to_csv('buffer_topic_channels.csv',index=False)

# df = pd.DataFrame(columns=['yt_shorts_link'])
# df.to_csv('../data/yt_shorts.csv',index=False)

# df = pd.DataFrame(columns=['invalid_vid_link'])
# df.to_csv('../data/invalid_videos.csv',index=False)

df = pd.DataFrame(columns=['topic', 'vid_link', 'title', 'description', 'tags', 'duration',
       'channel_id', 'channel_name', 'meta_data', 'tokens', 'channel_status', 'channel_link','token_score'])
df.to_csv('../data/buffer_topic_videos.csv',index=False)

df = pd.DataFrame(columns=['topic','channel_link','channel_status'])
df.to_csv('../data/buffer_topic_channels.csv',index=False)
