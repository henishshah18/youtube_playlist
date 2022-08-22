# Personalised Youtube Playlist
## I. Motivation

- Ever went down that rabbit hole where you are watching something on Youtube, and cut to an hour later you find yourself binge watching funny clips from the TV show 'Friends' or something entirely different from what you started with? 

***(If that little voice inside of you screamed YES!, don't worry we've all been there...)***

- There are two major issues with the Youtube Algorithm that recommends videos in the app- 

  **1. It maximizes our screen time on the platform by recommending videos that we have a higher chance of clicking on.**
  >How is that bad? Now, this is not a bad business model, but it certainly is disadvantageous for us as it only gives a little entertainment in exchange for keeping us in a potentially harmful dopamine loop.       


  **2. It does not give users a control over what they watch.**
  >This is a big one for me. As users of Youtube, we are limited to what the algorithm shows us unless we explicitly search for something.

<br>

- I created this project to tackle these exact issues. After you are done setting up the environment for the code, all you have to do is enter a topic that you want to 
watch videos about and it will create a playlist of personalised videos for you.

>***Note***- For best results, search for broad topics like Data Science, Economics, Videography, UI/UX, Geo-politics, etc.
</br>

### Demo:

<p align="center">
  <img src="https://user-images.githubusercontent.com/74452754/185832515-4ce35287-f781-48c5-b48c-218aedfc2503.png" />
</p>


## II. Overview

The project consists of three main sections:

**1. Data Acquisition:**
 - Collecting browser history from local machine.
 - Scraping top Youtube channels for input topic.
 - Collecting the data of videos from those channels through Youtube Data API.

**2. Data Modelling:**
- Unsupervised Content Based Recommendation Algorithm is used in this project. 
- The two main features used for modelling are 'video_title' and 'video_tags'. As both these features contain only keywords, the use of traditional method of Tf-idf vectorisation is futile.
- Thus, the method of 'Document Frequency Vectorization' was implemented from scratch in order to find top videos that are most similar to previously watched videos by the user.

**3. Playlist Creation:**
- Finally, a selected set of 10 videos (two videos per channel) are used to create a playlist.
- Using the Google OAuth 2.0, a playlist is created in your Youtube account.


**The overall flow of the algorithm is given below:**

<p align="center">
  <img src="https://user-images.githubusercontent.com/74452754/185822742-fd263722-33cb-42da-9373-5f5dd9810717.PNG" />
</p>

## III. Environment Variables

To run this project, you will firstly need to install the dependant libraries in your environment. To do this, use the following code:

```bash
pip install -r requirements.txt
```

## IV. API Keys and OAuth

- In order to use the Youtube Data API, you have to get a '**developerKey**'. 
  1. Follow the steps given [here](https://blog.hubspot.com/website/how-to-get-youtube-api-key) to get an access.
  2. Paste the developerKey inside `/data/config.ini` file.

- In order to create a playlist in your account, you will require an OAuth '**client_id**' and '**client_secret code**'.
  1. Follow the steps given [here](https://support.google.com/workspacemigrate/answer/9222992?hl=en)

  >***Note*** - When you are in OAuth Consent screen inside your created project, under 'Test User' section add the google account in which you want your playlists to be created.

  >***Note*** - When you are adding the URI under 'Authorized Redirect URIs', add `http://localhost:8080/` in the field.

  2. Finally, download the OAuth client details. Rename the file to `client_secrets.json` and replace it with the current empty file in `../data/client_secrets.json`.

![Oauth_download_button](https://user-images.githubusercontent.com/74452754/185827673-e1ba3eba-418b-4935-98f6-971905b6b2d9.PNG)


## V. Deployment

To deploy this project, run the following command:

```bash
  python3 main.py
```

## VI. Limitations
- The model performs very well for relatively broad topics for which there are established Youtube channels available but performs inconsistently with specific topics for eg. World War II. This can be overcome by introducing the alternative approach of scraping Youtube directly for those niche topics.
- As we obtain the list of relevant Youtube channels using Google search, the results maybe biased in some cases as there are instances of paid promotions over various blogs/webpages.
- As there is a rate limit attached with using the Youtube Data API, scaling this project might prove difficult. 

## VII. Support

For support or any queries, email henishshah18@gmail.com

