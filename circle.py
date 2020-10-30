import cv2
import numpy as np

capture = cv2.VideoCapture(0)
print
capture.get(cv2.CAP_PROP_FPS)
check=0
t = 100
w= 640.0
distance=100 #according to lidar data
last = 0
while True:
    ret, image = capture.read()

    img_height, img_width, depth = image.shape
    scale = w // img_width
    h = img_height * scale
    image = cv2.resize(image, (0, 0), fx=scale, fy=scale)

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_red = np.array([100,150,20])
    upper_red = np.array([255,255,150])
    mask = cv2.inRange(hsv, lower_red, upper_red)
    res = cv2.bitwise_and(image, image, mask=mask)
    red_sayi=1
    x_sum=0
    y_sum=0
    red_middle_x=0
    red_middle_y=0
    for x_i in range(0,len(res),5):
        for y_i in range(0,len(res[x_i]),5):
            if(res[x_i,y_i,2]>100 and res[x_i,y_i,1]<100 and res[x_i,y_i,0]<100):
                x_sum=x_sum+x_i
                y_sum=y_sum+y_i
                red_sayi = red_sayi + 1
                #print(red_sayi)
    red_middle_x=int(x_sum/red_sayi)
    red_middle_y = int(y_sum / red_sayi)
    print(red_middle_x)
    cv2.imshow("mask",res)
    # Apply filters
    grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blured = cv2.medianBlur(grey, 15)

    # Compose 2x2 grid with all previews
    grid = np.zeros([2 * int(h), 2 * int(w), 3], np.uint8)
    grid[0:int(h), 0:int(w)] = image

    # We need to convert each of them to RGB from grescaled 8 bit format
    grid[int(h):2 *int(h), 0:int(w)] = np.dstack([cv2.Canny(grey, int(t) / 2, int(t))] * 3)
    grid[0:int(h), int(w):2 * int(w)] = np.dstack([blured] * 3)
    grid[int(h):2 * int(h), int(w):2 * int(w)] = np.dstack([cv2.Canny(blured, int(t) / 2, int(t))] * 3)

    #cv2.imshow('Image previews', grid)

    sc = 1
    md = 30
    at = 40
    try:
        circles = cv2.HoughCircles(blured, cv2.HOUGH_GRADIENT, 1, 20, param1=75, param2=40, minRadius=10,maxRadius=120)
        circles = np.uint16(np.around(circles))
    except:
        circles = None


    if circles is not None:
        # We care only about the first circle found.
        circle = circles[0][0]

        x, y = int(circle[0]), int(circle[1])
        dot_y=int(h/2)
        # Draw dot in the center
        cv2.circle(image, (x, y), 1, (255, 255, 255), 10)
        cv2.circle(image, (red_middle_x, red_middle_x), 1, (0, 255, 0), 10)
        cv2.circle(image, (320, dot_y), 1, (0, 0, 0), 10)
        cv2.line(image, (x,y), (320,dot_y), (120, 150, 30), 5)
        text1="circle center:"
        text_x=str(x)
        text_y=str(y)
        difference_x = str(x - 320)
        difference_y = str(dot_y - y)
        cv2.putText(image, text1 + text_x + "," + text_y, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (209, 80, 0, 255),
                    2)
        cv2.putText(image, "distance from middle x:" + difference_x, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (209, 80, 0, 255), 2)
        cv2.putText(image, "distance from middle y:" + difference_y, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (209, 80, 0, 255), 2)
    cv2.imshow('Image with detected circle', image)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break