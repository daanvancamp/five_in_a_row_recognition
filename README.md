# five_in_a_row_recognition

Is part of this project: https://github.com/daanvancamp/gomoku-thesis-proj
This is the image recognition part.

**If you would want to test the program with my images, use recognition**
**If you want to build this into another program, use recognition_version to built-in**

**Use calibrate_color if you want to calibrate the color that is detected. This can improve the accuracy. This is very important when there is a lot of background.**

Note that a windows specific API is used, so if you would want to use this on another system, then you will need to change that API to another one. Then you need to change this line     cap = cv2.VideoCapture(1, cv2.CAP_DSHOW) and just delete that API/keyword argument.
 

developped by: @daanvancamp
