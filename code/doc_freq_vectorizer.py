import pandas as pd
import numpy as np
import ast
import pickle


def create_df_for_vect(df):
    
    def clean_duration(x):
        mins=0
        secs=0
        hrs=0
        try:
            x = x.replace('PT','')
            a = x.split('M')
            if 'H' not in a[0]:
                if 'S' in a[1]:
                    secs = int(a[1].replace('S',''))
                mins = int(a[0])
                ans = mins+(secs/60)
            else:
                b = a[0].split('H')
                hrs = int(b[0])
                mins = int(b[1])
                if 'S' in a[1]:
                    secs = int(a[1].replace('S',''))
                ans = (hrs*60)+mins+(secs/60)
        except Exception as e:
            # print(e)
            ans = np.nan
        return ans

    def clean_tokens(x):
        if isinstance(x,str):
            x = list(set(ast.literal_eval(x)))
        else:
            x = list(set(x))
        x = [word for word in x if len(word)>1]
        return x

    df.loc[:,'duration'] = df.loc[:,'duration'].apply(clean_duration)
    df.loc[:,'duration'] = df['duration'].fillna(int(df['duration'].mean()))
    df.loc[:,'duration'] = (df['duration']-df['duration'].mean())/df['duration'].std()

    df.loc[:,'tokens'] = df.loc[:,'tokens'].apply(clean_tokens)
    return df


def doc_freq(df_column):
    doc_dict={}
    token_list = df_column.tolist()
    for tokens in token_list:
        for word in tokens:
            if word not in doc_dict:
                doc_dict[word]=1
            else:
                doc_dict[word]+=1

    doc_dict = {k:v/len(token_list) for k,v in doc_dict.items()}
    return doc_dict

def corpus_doc_freq(df_column,doc_dict):   
    if isinstance(df_column,list):
        token_list = []
        token_list.append(df_column)
    else:
        token_list = df_column.tolist()
    final_doc_dict={}
    for i in range(len(token_list)):
        final_doc_dict[i]={word:doc_dict[word] for word in token_list[i] if word in doc_dict}
    return final_doc_dict

def df_vectorizer(df_column,vocab_dict,corpus_doc_dict):
    if isinstance(df_column,list):
        token_list = []
        token_list.append(df_column)
    else:
        token_list = df_column.tolist()
    vocab = list(vocab_dict.keys())
    vec = np.zeros((len(token_list),len(vocab_dict.keys())))
    for i in range(len(token_list)):
        for word in token_list[i]:
            if word in vocab:
                vec[i][vocab.index(word)]=corpus_doc_dict[i][word]
    return vec


if __name__ == "__main__":

    df_og = pd.read_csv('../data/yt_watched_final_details.csv',usecols=['duration','tokens'])
    df = create_df_for_vect(df_og)


    vocab_dict = doc_freq(df['tokens'])

    # with open('train_vocab_dict.pickle', 'wb') as handle:
    #     pickle.dump(vocab_dict,handle)

    corpus_doc_dict = corpus_doc_freq(df['tokens'],vocab_dict)
    vec = df_vectorizer(df['tokens'],vocab_dict,corpus_doc_dict)
    print(vec)

    trial_str = ['data science','ai', 'pipeline', 'top', 'mistakes', 'avoid', 'resume', 'data science interview', 'interview', '2022']
    trial_corpus_dict = corpus_doc_freq(trial_str,vocab_dict)
    # print(trial_corpus_dict)
    trial_vec = df_vectorizer(trial_str,vocab_dict,trial_corpus_dict)
    print(sum(trial_vec[0]))





