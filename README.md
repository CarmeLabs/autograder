# Autograding with Colab and Gopher Grader

I've seen that quite a few other people teaching analytics have been discussing different autograding solutions.  This is my effort to create something that is relatively easy to use.

Generally, the workflow is as follows:

  (1) Use [GitHub Classroom](https://classroom.github.com) to collect assignments.  I can hear you already, I don't want to use git, it is too complicated.  It really is extremely easy, and it is a good learning experience for the students.  If you aren't a git users, you can easily [drag and drop a file to GitHub using the Web interface.](https://help.github.com/en/github/managing-files-in-a-repository/adding-a-file-to-a-repository)

  (2) Maintain all of the aspects of an assignment via a configuration file and roster.  This details aspects of the tests and the students.  If you collect notebooks via GitHub, this will allow a translation between GitHub and other notebooks.

  (3) Run the grading notebook.  The grading notebook will (a.) load the configuration files with information on the setup, (b.) copy the notebook file from the github repository to a /tmp folder for grading, (c.) append grading code to the bottom of the notebook.  (d.) execute the notebook. (d.) Output a JSON file with the results.

Give it a try with the attached notebook and grade the sample exercises.  The sample exercises are setup to address a number of different test cases, including 0/3 -3/3 grades, no submission, duplicate submission, etc.


### Install Dependencies to Use Locally
This can be done on colab for simple assignments.  For large classes or better performance it is faster to do on your laptop on server.

Note that though it works on colab, when running locally there is a issue with Gopher Grader.  

1. Make sure your conda environment is up to date.
`conda update conda`

2. Create autograding environment.
`conda create -n autograding python=3.6.8 anaconda`
