# Importing Packages
import cv2
import numpy as np
import pytesseract 
import os

# Setting the threshold for getting the information of checkboxes/Radiobuttons
pixelThreshold = 100

# C:\Program Files\Tesseract-OCR
# For windows uncomment this line
# Linking the tesseract executable file
pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

# Bounding box information of necessary fields.
# roi contains type of the field and name of the fields.
roi = [[(34, 190), (870, 236), 'text', 'company_name'],
       [(36, 272), (872, 318), 'text', 'Alternate_name'],
       [(36, 436), (1202, 484), 'text', 'Vendor_Address'],
       [(34, 790), (86, 830), 'box', 'Corporation'],
       [(34, 832), (84, 874), 'box', 'LLC'],
       [(396, 792), (442, 830), 'box', 'Individual'],
       [(396, 830), (442, 874), 'box', 'Partnership'],
       [(36, 932), (84, 972), 'box', 'Checks_yes'],
       [(36, 974), (84, 1016), 'box', 'Checks_No'],
       [(256, 932), (306, 974), 'box', 'Card_yes'],
       [(256, 972), (306, 1014), 'box', 'Card_No'],
       [(804, 932), (1198, 972), 'text', 'Account_No']]

# Feature Detection
# Importing the template image
imgQ = cv2.imread('Template\\template.jpg')
h,w,c = imgQ.shape
#imgQ = cv2.resize(imgQ,(w//2,h//2))
#cv2.imshow("Template",imgQ)

# ORB(oriented FAST and rotated BRIEF) detector
# By default it will retain 500 features.
# Idea is to find the features and descriptors using ORB detector
orb = cv2.ORB_create(5000)
kp1, des1 = orb.detectAndCompute(imgQ,None)
imgkp1 = cv2.drawKeypoints(imgQ,kp1,None)
#imgkp1 = cv2.resize(imgkp1,(w//2,h//2))
#cv2.imshow("Keypoints",imgkp1)


# Importing the testing images
#path = '/home/venkatesh/Downloads/python/images/Testing'
#path = '/home/venkatesh/Downloads/python/images/sample/8'
#path = '/home/venkatesh/Downloads/python/images/Training'
path = 'Testing'
myPicList = os.listdir(path)
print(myPicList)

# Looping through all the testing images
for j,y in enumerate(myPicList):
    img = cv2.imread(path + "/" +y)
    #img = cv2.resize(img,(w//2,h//2))
    #cv2.imshow(y,img)
    
    # Finding the features and descriptors of testing images
    kp2, des2 = orb.detectAndCompute(img,None)
    bf = cv2.BFMatcher(cv2.NORM_HAMMING)
    
    # Using brute force matcher
    # Matching the descriptors of template and testing images
    matches = list(bf.match(des2,des1)) 
    matches.sort(key=lambda x:x.distance)
    good = matches[:int(len(matches)*(25/100))]
    imgMatch = cv2.drawMatches(img,kp2,imgQ,kp1,good[:20],None,flags=2)
    #imgMatch = cv2.resize(imgMatch,(w//2,h//2))
    #cv2.imshow(y,imgMatch)
    
    # Aligning  the images
    srcPoints = np.float32([kp2[m.queryIdx].pt for m in good]).reshape(-1,1,2)
    dstPoints = np.float32([kp1[m.trainIdx].pt for m in good]).reshape(-1,1,2)
    
    # Find the relationship matrix of the images and passing this to warpPerspective
    M, _ = cv2.findHomography(srcPoints,dstPoints,cv2.RANSAC,5.0)
    
    # Fitting the size of the aligned image to the size of the template image
    imgScan = cv2.warpPerspective(img,M,(w,h))
    #imgScan = cv2.resize(imgScan,(w//2,h//2))
    #cv2.imshow(y,imgScan)
    
    # Generating the mask using numpy
    imgShow = imgScan.copy()
    imgMask = np.zeros_like(imgShow)
    

    myData = []

    print(f"{10*'#'} Extracting Data From {y} {10*'#'}")
    
    for x,r in enumerate(roi):
        
        # Applying the mask on region of interests(roi) where the bounding box information is provided
        cv2.rectangle(imgMask, (r[0][0],r[0][1]),(r[1][0],r[1][1]),(0,255,0),cv2.FILLED)
        imgShow = cv2.addWeighted(imgShow,0.99,imgMask,0.1,0)
        
        # Cropping the masked areas using bounding box information
        imgCrop = imgScan[ r[0][1]:r[1][1] , r[0][0]:r[1][0] ]
        #cv2.imshow(str(x),imgCrop)
            
        # If the image type is TEXT
        if r[2] == 'text':
            
            # Image is passed as input to pytesseract function
            # image_to_string retrieves the text inside the image
            temp = pytesseract.image_to_string(imgCrop)
            print(f'{r[3]} : {temp[:-1]}') 
            
            # Storing the information
            myData.append(temp[:-1])
            
        # If the image type is BOX 
        if r[2] == 'box':
            
            # Converts the image to grayscale image
            imgGray = cv2.cvtColor(imgCrop,cv2.COLOR_BGR2GRAY)
            
            # Converts the image into binary image where foreground and background gets seperated
            imgThresh = cv2.threshold(imgGray,170,255,cv2.THRESH_BINARY_INV)[1]
            
            # Counts the non-zero pixels
            totalPixels = cv2.countNonZero(imgThresh)
            #cv2.imshow('threshold',imgThresh)
            #print(totalPixels)
        
            # Compare the pixel value with the threshold
            # Checks whether the checkboxs are checked or unchecked
            if totalPixels>pixelThreshold: 
                totalPixels = 1
            else: 
                totalPixels = 0
            
            print(f'{r[3]} : {totalPixels}')
            
            # Storing the information
            myData.append(totalPixels)
            
            
        cv2.putText(imgShow,str(myData[x]),(r[0][0],r[0][1]), cv2.FONT_HERSHEY_PLAIN,2.5,(0,0,255),4)
        
    # Converting the information into .csv file        
    
    with open('Data.csv','a+') as f:
        for data in myData:
            f.write(str(data)+',')
        f.write('\n')
    
    # prints the information 
    print(myData)
    #imgShow = cv2.resize(imgShow,(w//2,h//2))
    #cv2.imshow(y,imgShow)
        
cv2.waitKey(0)