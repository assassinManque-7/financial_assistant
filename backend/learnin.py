from transformers import pipeline
import emoji

emoji_dic={}

for i in emoji:
    emoji_dic[i] = i.desc

def return_d_ph(ph)
    desc_ph = ""
    for j in ph:
        if j.isEmoji():
            desc_ph += f'{emoji_dic[j]}'

        else:
            desc_ph += j

    return desc_ph

analyzer_object = pipeline(
    "sentiment=analyser",
    model = "cardiffnlp/twitter-roberta-base-sentiment-latest"
)   

def get_sentiment(ph):
    proc_text = return_d_ph(ph)

    result = analyzer_object(proc_text)

    print("proc text : ", proc_text)
    print("sentiment : ", result[0]['label'])
    print("score : ", result[0]['score'])

