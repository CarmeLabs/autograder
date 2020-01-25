import configparser, sys, os, importlib, json
from bs4 import BeautifulSoup
from client.api.notebook import Notebook
#Load the configuration
with open('config.json', 'r') as fp:
    cf = json.load(fp)
#load the autograding library
sys.path.append(cf['autograde_lib'])
import grading_object_detection as god

#NEWCELL
#!pip install git+https://github.com/carme/Gofer-Grader

#NEWCELL
#Checks function.
#def check_get_hashtags(file,hashtag,answer):
#    with open(file) as json_file:
#        statuses = json.load(json_file)
#    other_hashtags = get_hashtags(statuses, hashtag)
#    #print(other_hashtags)
#    other_hashtags = [s.replace('#', '') for s in other_hashtags]
#    if other_hashtags==answer:
#        return True
#    else:
#        return False

#NEWCELL
ok = Notebook(cf['ok_file'])
_ = ok.auth(inline=False)
results= {q[:-3]:ok.grade(q[:-3]) for q in os.listdir("tests") if q.startswith('q')}


#NEWCELL
import autograde as ag
importlib.reload(ag)

def output_tests(cf, results):
    autograde={}
    autograde['github_id']=cf['github_id']
    #This is a selection of variables from config file.
    for s in cf['variables']:
        if s in globals():
            autograde[s]=eval(s)
        else:
            autograde[s]=None

    #get text based answers for manual grading.
    for a in cf['answers']:
        if a in globals():
            autograde[a]=eval(a).strip()
        else:
            autograde[a]='No answer.'
        autograde[a+"_score"]=''

    total_autograde=0

    #This loops through the results
    for key, val in results.items():
        autograde[key]=val.grade
        results_key=str(key)+"-failed"
        autograde[key]=val.grade*cf['points_per_test']
        total_autograde+=autograde[key]
        #We use beautiful soup to parse the tests.
        soup = BeautifulSoup(str(val.failed_tests), "html.parser")
        #There are multiple components, but the expected data seems most valuable.
        got = soup.get_text().split('\\n')[16:20]
        autograde[results_key]=str(got)
        #total grade
    autograde['autograde_total']=total_autograde

    with open(cf['github_id']+'.json', 'w') as fp:
                json.dump(autograde, fp, sort_keys=True, indent=4)

    return autograde

grade=output_tests(cf, results)
grade
