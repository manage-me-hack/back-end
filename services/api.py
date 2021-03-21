from services import *
import json
import requests

def face_detect(face_image: str, is_local: bool) -> json:
    '''
    Params:
        is_local: Boolean to denote wether image is available locally or hosted
        face_image: path of image
    Desc:
    Returns face parameters and emotions
    Need to use detection model 01 for recognising emotions 
    '''

    try:
        if not is_local:
            detected_faces = face_client.face.detect_with_url(url=face_image, **API_PARAMS) 
        else:
            detected_faces = face_client.face.detect_with_stream(image=face_image, **API_PARAMS)
    except Exception as e:
        print("Services Module:", e)
        if (str(e).find('429') != -1):
            raise Exception('API LIMIT')
        else:
            raise Exception('API FAIL')

    if not detected_faces:
        print("Services module: NO FACE DETECTED")
        raise Exception('API FAIL')

    res = {
        "id": None,
        "rectangle": None,
        "emotion": None
    }

    # Detected faces are in descending order of their face bounding boxes
    for face in detected_faces: 
        res["id"] = face.face_id
        res["rectangle"] = json.loads(str(face.face_rectangle).replace("\'", "\""))
        res["emotion"] = json.loads(str(face.face_attributes.emotion).replace("\'", "\""))        
        break

    return res

'''
Returns 20 most important keywords for given link 
''' 
def getKeywords(link):
   
    total_keywords = {}

    try:
        keywords = json.loads(requests.get(YAKE+link+DETAILS).text)
    except Exception as err:
        print("Non Compatible link. {}".format(err))
        raise Exception("FAIL")

    keywords = keywords['keywords']
    for word in keywords:
        word['ngram'] = stemmer.stem(word['ngram'])
        
        # Testing
        
        word['score'] = 1/word['score']
        
        # Testing

        total_keywords[word['ngram']] = word['score']
    
    total_keywords = {k: v for k, v in sorted(total_keywords.items(), key=lambda item: item[1], reverse=True)}
    
    return total_keywords 


def detect_change(history_all: dict, history_just: dict) -> bool:

    def getFullHistoryKeyword(history, count):

        top_all = {}
        for link in history:
            keywords = history[link]

            for word in keywords:

                if word in top_all:
                    top_all[word] += keywords[word]
                else:
                    top_all[word] = keywords[word]
        
        top_all = {k: v for k, v in sorted(top_all.items(), key=lambda item: item[1], reverse=True)}
       
        top_count = {}
        for key in top_all.keys():
            top_count[key] = top_all[key]
            
            if len(top_count) == count:
                break
        return top_count
    
    keywords_all = getFullHistoryKeyword(history_all, 20)
    keywords_just = getFullHistoryKeyword(history_just, 5)

    count = 0
    total = 0
    for topic in keywords_just:
        if topic in keywords_all:
            print(topic)
            count+=keywords_just[topic]
        total += keywords_just[topic]

    score = count/total
    print(score) 
    return score < THRESHOLD

