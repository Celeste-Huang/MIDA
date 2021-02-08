## README before download
If you use 'Download ZIP' to download the repository, you may not get Git LFS files (i.e., Exe/main.exe, Example/*.exe, Videos/*.mp4). There are three ways to solve this problem.

Solution 1. Use 'git clone' command rather than 'Download ZIP'.

Solution 2. Navigate with web browser to any Git LFS file and click 'Download' button on top right, then you got the real file not the pointer.
For example, navigate to Videos/, click 1. How to .. mp4 file, click 'Download' button, then you will get 50.2MB mp4 file rather than 1KB pointer file. You may need to repeat this action for all mp4 files in Videos/ folder, .exe file in Exe/ folder and all .exe file in Example/ folder.  

Solution 3. Download ZIP archiver from Google Driver https://drive.google.com/drive/folders/1S8vbJ62XTm0TRb4gPbHlzZBxn8in28hX?usp=sharing

## Brief instructions for using MIDA module

1. Prepare all necessary data, such as observation files, output configuration files, model executable, parameter range, etc. 
2. Enter into exe/ folder, copy the main.exe file to your preferred working path (e.g., F:\Lab\Work\MIDA\Code\MIDA) 
3. Enter into your working path, double click the main.exe, two windows will pop up. 
4. Input all necessary information in the first panel (i.e., preparation of DA), and generate the namelist.txt file
5. Indicate the namelist.txt file and click 'run DA' button, the process of DA will be print out in the other window
6. After you successfully run DA, click the 'generate plots' button, figures will generate automatically
7. Any error occurred, detailed information will be print out in the other window.

For detailed information, please refer to the MIDA_tutorial.pdf in Documents/ folder and watch video tutorials in Videos/ folder. If you have more questions, please feel free to contact me (xh59@nau.edu). 
