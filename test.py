import cv2 as cv
import numpy as np

MIN_MATCH_COUNT = 30

def AutoHomography(img1, img2):
    sitf = cv.SIFT_create()
    kp1, des1 = sitf.detectAndCompute(img1,None)
    kp2, des2 = sitf.detectAndCompute(img2,None)


    FLANN_INDEX_KDTREE = 1
    index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
    search_params = dict(checks = 50)
    flann = cv.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(des1,des2,k=2)
    # store all the good matches as per Lowe's ratio test.
    good = []
    for m,n in matches:
        if m.distance < 0.7*n.distance:
            good.append(m)


    if len(good)>MIN_MATCH_COUNT:
        src_pts = np.float32([ kp1[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
        dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1,1,2)
        M, mask = cv.findHomography(src_pts, dst_pts, cv.RANSAC,5.0)
    else:
        print("Not enough matches are found")

    return np.float32(M).reshape(9,)


with open("homographies.txt", 'w') as f:
    f.write("1.0000000000 0.0000000000 0.0000000000 0.0000000000 1.0000000000 0.0000000000 0.0000000000 0.0000000000 1.0000000000 \n")
    count = 1
    print("START READING")
    for i in range(1,2000):
        img1 = cv.imread("rgb/{0:04d}.png".format(1), 0)
        img2 = cv.imread("rgb/{0:04d}.png".format(i+1), 0)# cv.IMREAD_GRAYSCALE
        if(img2 is None):
            print("END")
            break
        H = AutoHomography(img1,img2)
        
        #write out
        for arr in H:
            f.write("{:.10f}".format(arr)+' ')
        f.write('\n')

        print(H)
        count += 1
    

'''
if len(good)>MIN_MATCH_COUNT:
    src_pts = np.float32([ kp1[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
    dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1,1,2)
    M, mask = cv.findHomography(src_pts, dst_pts, cv.RANSAC,5.0)
    matchesMask = mask.ravel().tolist()
    h,w = img1.shape
    pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
    dst = cv.perspectiveTransform(pts,M)
    img2 = cv.polylines(img2,[np.int32(dst)],True,255,3, cv.LINE_AA)
else:
    print( "Not enough matches are found - {}/{}".format(len(good), MIN_MATCH_COUNT) )
    matchesMask = None


draw_params = dict(matchColor = (0,255,0), # draw matches in green color
                   singlePointColor = None,
                   matchesMask = matchesMask, # draw only inliers
                   flags = 2)
img3 = cv.drawMatches(img1,kp1,img2,kp2,good,None,**draw_params)

cv.imwrite("matches.png", img3)
'''