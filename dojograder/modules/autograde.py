import os, sys, configparser, datetime, shutil, json
import pandas as pd
from nbconvert import PythonExporter
from nbconvert import PDFExporter
from sys import exit
from bs4 import BeautifulSoup
import glob
import nbformat as nbf
from nbconvert.preprocessors import ExecutePreprocessor
from nbconvert.preprocessors import CellExecutionError
import argparse
import os

CWD = os.getcwd()
TESTS_DIR = 'tests'
ASSIGNMENTS_DIR = 'assignments'
OUTPUT_DIR = 'output'
GRADE_DIR = ''
JSON_DIR = 'json'
NOTEBOOKS_DIR = 'notebooks'
ROSTER_DIR = 'roster'
TMP='tmp'
MISSING='MISSING'

def set_config(base_dir, config, grade):
    #Grading will be done of this path.
    cf={}
    cf['kernal']=config['default']['kernal_name']
    cf['assignment_name']=grade
    cf['mangrade_match_col']=config['default']['mangrade_match_col']
    cf['blackboard_match_col']=config['default']['blackboard_match_col']
    cf['blackboard_rename_col']=config['default']['blackboard_rename_col']
    cf['assignments_path']=os.path.join(base_dir,ASSIGNMENTS_DIR,config[grade]['assignments_dir'])
    cf['append_path']=os.path.join(base_dir,config[grade]['append_script'])
    cf['tests_path']=os.path.join(base_dir,TESTS_DIR,config[grade]['tests_dir'])
    cf['blackboard_total_col']=config[grade]['blackboard_total_col'].replace('"', '')
    cf['ignore']=config['default']['ignore'].replace('"', '').replace(' ', '').split(',')
    cf['roster_path']=os.path.join(base_dir,ROSTER_DIR, config[grade]['roster'])
    cf['notebook_output_path']=os.path.join(base_dir,OUTPUT_DIR, grade, NOTEBOOKS_DIR)
    cf['grades_output_path']=os.path.join(base_dir, OUTPUT_DIR, grade)
    cf['json_output_path']=os.path.join(base_dir, OUTPUT_DIR, grade,JSON_DIR)
    #cf['autograde_output_path']=os.path.join(base_dir,OUTPUT_DIR, grade,config['default']['autograde'])
    cf['mangrade_output_path']=os.path.join(base_dir, OUTPUT_DIR, grade, config['default']['mangrade'])
    cf['status_output_path']=os.path.join(base_dir,OUTPUT_DIR, grade,config['default']['status_file'])
    if base_dir=='.':
        cf['autograde_lib']=os.path.join(os.pardir,os.pardir)
    else:
        cf['autograde_lib']=os.path.join(base_dir)
    #make required directories
    if not os.path.exists(cf['grades_output_path']):
        os.makedirs(cf['grades_output_path'])
    if not os.path.exists(cf['notebook_output_path']):
        os.makedirs(cf['notebook_output_path'])
    if not os.path.exists(cf['json_output_path']):
        os.makedirs(cf['json_output_path'])
    #TODO CHECK FILES
    cf['points_per_test']=int(config[grade]['points_per_test'])
    cf['variables']=config['default']['variables'].replace('"', '').replace(' ', '').split(',')
    cf['answers']=config[grade]['answers'].replace('"', '').replace(' ', '').split(',')
    cf['blackboard_starter']=os.path.join(base_dir,OUTPUT_DIR,config['default']['blackboard'])
    cf['blackboard_output_path']=os.path.join(cf['grades_output_path'], config['default']['blackboard'])
    cf['ok_file']=config['default']['ok_file']
    cf['delete_cells']=config[grade]['delete_cells']
    return cf


#Ignore Directories
def ignore_dir(dir_list, ignore):
    return (list(set(dir_list) - set(ignore)))

def get_submissions(submission_dir, ignore):
    submissions= [os.path.join(o) for o in os.listdir(submission_dir) if os.path.isdir(os.path.join(submission_dir,o))]
    submissions=ignore_dir(submissions, ignore)

    return submissions

def get_config(file):
    config = configparser.ConfigParser()
    return config.read(file)


def copy_and_overwrite(from_path, to_path):
    if os.path.exists(to_path):
        shutil.rmtree(to_path)
    shutil.copytree(from_path, to_path)

def cleanup_path(path):
    shutil.rmtree(path)

def get_notebook(path):
    #Count the number of submission files
    status={}
    files = glob.glob1(path,"*.ipynb")
    status['submission_count'] = len(files)

    #Different actions depending on number of submissions.
    if status['submission_count']==0:
        status['status_code']=1
        status['status_description']='1. No submission.'
        status['file']=MISSING
    elif status['submission_count']>1:
        status['status_code']=2
        biggest_file=0
        for x in files:
            size = os.path.getsize(os.path.join(path,x))
            if size > biggest_file:
                status['file']=x
                biggest_file=size
        status['status_description']='2. Multiple notebooks. Grading largest file: '+str(status['file'])
    else:
        status['status_code']=2
        status['file']=files[0]
        status['status_description']='2. Grading '+ str(status['file'])
    return status

def grade(cf, grade=100000, cleanup = True, regrade = False,submissions=[]):
    #create a dataframe to keep track of grading.
    df = pd.DataFrame()
    with open(cf['append_path']) as file:
        append_script = file.read()
    append_script = append_script.split('#NEWCELL')

    if len(submissions)==0:
        submissions = get_submissions(cf['assignments_path'], cf['ignore'])

    if regrade==False:
        graded_set=set(f.split('.json')[0] for f in os.listdir(cf['json_output_path']) if os.path.isfile(os.path.join(cf['json_output_path'], f)))
        submissions_set=set(submissions)
        to_grade=list(submissions_set-graded_set)
        print("Total submissions:", len(submissions_set),"To grade:",len(to_grade))
    else:
        to_grade = submissions
        print("Total submissions:", len(submissions),"Grading all.")

    #Loop through all the grading
    for x in to_grade:
        row=df.shape[0]
        print("Grading assignment: ", x, "Number", row+1, "/",len(to_grade) )
        cf['exec_path']=os.path.join(TMP,x)
        #Add tests to temp directory
        copy_and_overwrite(cf['tests_path'], cf['exec_path'])

        #record data about the processing of the file.
        df.loc[row,'datetime']=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        df.loc[row,'github_id'] = x  #the github id.

        #find the notebook
        df.loc[row,'assignment_path']=os.path.join(cf['assignments_path'],x)
        submission=get_notebook(df.loc[row,'assignment_path'])
        df.loc[row,'status_code']=submission['status_code']
        df.loc[row,'status_description']=submission['status_description']
        df.loc[row,'file']=submission['file']

        #copy the notebook
        if df.loc[row,'file']!= MISSING:
            print("copying notebook", df.loc[row,'assignment_path'], df.loc[row,'file'])
            notebook_exe=os.path.join(cf['exec_path'],x+'.ipynb')
            notebook_starter=os.path.join(df.loc[row,'assignment_path'],df.loc[row,'file'])
            print("exe",notebook_exe, "starter", notebook_starter)
            cf['notebook_output_file']=x+'_output.ipynb'
            cf['grade_output_json']=x+'.json'
            grade_tmp_output=os.path.join(cf['exec_path'],cf['grade_output_json'])
            notebook_tmp_output=os.path.join(cf['exec_path'],cf['notebook_output_file'])
            copy=copy_notebook(notebook_starter, notebook_exe, append_script,cf['delete_cells'])
            cf['github_id']=x
            #write the config to an autograding file.
            with open(os.path.join(cf['exec_path'],'config.json'), 'w') as fp:
                json.dump(cf, fp, sort_keys=True, indent=4)
        #execute the notebooks
            status_code, status_description=grade_notebook(cf['exec_path'], notebook_exe, notebook_tmp_output, cf['kernal'])

        #copy the FILES
            if os.path.exists(grade_tmp_output) & os.path.exists(grade_tmp_output):
                df.loc[row,'status_code']=status_code
                df.loc[row,'status_description']=submission['status_description']+" "+status_description
                shutil.copyfile(notebook_tmp_output,os.path.join(cf['notebook_output_path'], cf['notebook_output_file']))
                shutil.copyfile(grade_tmp_output,os.path.join(cf['json_output_path'], cf['grade_output_json']))
            else:
                df.loc[row,'status_code']='3.'
                df.loc[row,'status_description']=submission['status_description']+'3. Error during notebook execution. Output file not generated.'
        #cleanup
        if  cleanup==True:
            cleanup_path(cf['exec_path'])

        #Just for just a few
        if row+1  ==grade:
            break
    df.to_excel(cf['status_output_path'], sheet_name='status', index=False)
    #copy autograde file for manual grading.
    #if not os.path.exists(cf['mangrade_output_path']):
    #    shutil.copyfile(cf['autograde_output_path'],cf['mangrade_output_path'])
    #Copy Blackboard starter
    #if not os.path.exists(cf['blackboard_output_path']):
    #    blackboard_df=pd.read_csv(cf['blackboard_starter'])
    #    blackboard_df.rename(columns={cf['blackboard_rename_col']: cf['blackboard_total_col']}, inplace=True)
    #    blackboard_df.to_csv(cf['blackboard_output_path'], index=False)
    return df

def copy_notebook(path_in, path_out, cells, delete):
    #Copy to a directory so all notebooks will be together.
    try:
        with open(path_in) as f:
            nb = nbf.read(f, as_version=4)
        #Delete cells
        del nb['cells'][0:int(delete)]

        #temportary # HACK:
        delete_cells=[]
        for g in range(len(nb['cells'])):
            if '!rm -rf *' in str(nb['cells'][g]['source']):
                print("deleting cell:", nb['cells'][g]['source'])
                delete_cells.append(g)
        for h in range(len(delete_cells)):
            del nb['cells'][delete_cells[h]]


        #Add Cells
        for x in cells:
            nb['cells'].append(nbf.v4.new_code_cell(source=x))
        #Write Script out to file
        with open(path_out, mode='w', encoding='utf-8') as f:
            nbf.write(nb, f)
    except IOError as e:
        print("Unable to  convert file. %s" % e)

def grade_notebook(path, notebook_path, output_path, kernal='python3'):
        print("Running notebooks: ", notebook_path)
        with open(notebook_path) as f:
            nb = nbf.read(f, as_version=4)
        ep = ExecutePreprocessor(allow_errors=True,timeout=600, kernel_name=kernal)
        try:
            out = ep.preprocess(nb, {'metadata': {'path': path}})
        except CellExecutionError:
            out = None
            msg = 'Error executing the notebook "%s".\n\n' % notebook_filename
            msg += 'See notebook "%s" for the traceback.' % output_path
            print(msg)
            raise
        finally:
            print("Writing to", output_path)
            with open( output_path, mode='w', encoding='utf-8') as f:
                nbf.write(nb, f)
            return 4, "4. Graded."

def username_from_email(email):
    email = str(email).lower()
    username=email.split("@")[0]
    return username

def output_tests(cf, results):
    autograde={}
    autograde['github_id']=cf['github_id']
    #This is a selection of variables from config file.
    for s in cf['variables']:
        if s in globals():
            autograde[s]=eval(s).lower()
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

def generate_mangrade(cf):
    graded=[f for f in os.listdir(cf['json_output_path']) if os.path.isfile(os.path.join(cf['json_output_path'], f))]

    mangrade_df=pd.DataFrame()
    row=0
    for x in graded:
        with open(os.path.join(cf['json_output_path'], x)) as f:
            data = json.load(f)
        for key in data.keys():
            mangrade_df.loc[row,key] = data[key]
        row+=1
        mangrade_df.to_excel(cf['mangrade_output_path'], sheet_name='mangrade', index=False)
    return mangrade_df

def generate_blackboard(cf):
        #if not os.path.exists(cf['blackboard_output_path']):
        #    blackboard_df=pd.read_csv(cf['blackboard_starter'])
        #    blackboard_df.rename(columns={cf['blackboard_rename_col']: cf['blackboard_total_col']}, inplace=True)
        #    blackboard_df.to_csv(cf['blackboard_output_path'], index=False)
        print("test")

def main():
    # count the arguments
    parser = argparse.ArgumentParser(description="Autograder")
    parser.add_argument("-P", "--path", help="path to assignment", default='.')
    args=parser.parse_args()
    print(args)
    cf={}
    if args.path:
        cf['path']=args.path
        print("grading notebooks in path", cf['path'])
    status = get_notebook(cf['path'])
    cf['status_code']=status['status_code']
    cf['status_description']=status['status_description']
    cf['file']=status['file']

    #grade_notebook(path, notebook_path, output_path, kernal='python3'):

if __name__== "__main__":
  main()
