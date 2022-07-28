# OCR-openCV-pytesseract
Simple OCR which performs the NLP task to extract the text and other informations from any kind of forms.

## Working
Initially any kind of forms needs to be converted into image. Then we have the specify the region of interests means locating the interested regions on the image from where we tend to get the information. For this we will make use of below python script.

### bbox.py
This python script is used to get the bounding box information from the template image. Here template image is used as referencing image. We have to the mark the regions using the mouse. After marking the region it will ask for type and name of the region. To make sure the same region is not marked again the points will be coloured after marking.
   

