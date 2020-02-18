# Autograding with Colab and Gopher Grader

I've seen that quite a few other people teaching analytics have been discussing different autograding solutions.  This is my effort to create something that is relatively easy to use.

Generally, the workflow is as follows:

  (1) Use [GitHub Classroom](https://classroom.github.com) to collect assignments.  I can hear you already, I don't want to use git, it is too complicated.  It really is extremely easy, and it is a good learning experience for the students.  If you aren't a git users, you can easily [drag and drop a file to GitHub using the Web interface.](https://help.github.com/en/github/managing-files-in-a-repository/adding-a-file-to-a-repository)

  (2) Maintain all of the aspects of an assignment via a configuration file and roster.  This details aspects of the tests and the students.  If you collect notebooks via GitHub, this will allow a translation between GitHub and other notebooks.

  (3) Run the grading notebook (located at 'autograder/notebooks/notebook.ipynb'.  The grading notebook will (a.) load the configuration files with information on the setup, (b.) copy the notebook file from the github repository to a /tmp folder for grading, (c.) append grading code to the bottom of the notebook.  (d.) execute the notebook. (d.) Output a JSON file with the results.

Give it a try with the attached notebook and grade the sample exercises.  The sample exercises are setup to address a number of different test cases, including 0/3 -3/3 grades, no submission, duplicate submission, etc.

### Install Dependencies to Use Locally
These steps more or less cover everything you need to get the autograder working. It is assumed that you've cloned the repository to some local destination.

1. We'll be using Anaconda with Python 3.7, which you can get here:
https://www.anaconda.com/distribution

2. Open Anaconda Prompt and make sure your conda environment is up to date.
`conda update conda`

3. Create autograding environment.
`conda create -n autograding python=3.6.8 anaconda`

4. Install the autograder library from Carme
`conda create --name autograder --yes`
`conda activate autograder`
`#change to the autograder directory`
`conda install -c anaconda git --yes`
`conda install -c anaconda pip --yes`
`pip install -r requirements.txt`

If you have problems with installation, make sure you activate the autograder in Anaconda Prompt using `conda activate autograder` and navigate to your local repository before installing the required tools.

Once the dependencies are installed, run Jupyter Notebook and open the grading notebook at 'autograder/notebooks/grade.ipynb' and follow the instructions there.

### Using Google Colab and Google Drive
Colab can be used to grade simple assignments due to its slower speed. For large classes, or simply just better performance, it is faster to grade on your laptop or on server.

1. Copy the autograder repository to your base Google Drive in a folder called 'autograder'.

2. Upload and open the grading notebook at 'autograder/notebooks/grade.ipynb'

3. Uncomment the following lines of code and run them to use Colab:
`from google.colab import drive`
`drive.mount('/content/drive')`
`!ls -al /content/drive/'My Drive'/autograder`
Note: If your directory is different, modify either the physical directory or the code.