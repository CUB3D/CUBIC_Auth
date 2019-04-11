#!venv/bin/python
import cv2
import numpy as np
import pytesseract
import re
from collections import namedtuple

keypointData = namedtuple("keypointData", "kp1 d1 kp2 d2")
processedImage = namedtuple("processedImage", "original greyscale size")
pair = namedtuple("pair", "x y")
perspectiveData = namedtuple("perspectiveData", "matchesMask perspectiveCorrectionMatrix")
results = namedtuple("results", "studentID libraryID success")

FLANN_CONFIG = {
    "algorithm": 1,
    "trees": 5
}


def getKeypoints(img):
    orb = cv2.ORB_create(edgeThreshold=10, patchSize=31, nlevels=8, fastThreshold=20, scaleFactor=1.2, nfeatures=1000000)
    return orb.detectAndCompute(img, None)

# img = src
# img2 = template

#gray = graySrc
#gray2 = grayTemplate


def detect_ProcessImage(image):
    if image is None:
        raise Exception("Image is invalid")
    return processedImage(image, cv2.cvtColor(image, cv2.COLOR_RGB2GRAY), image.shape[:2])


def detect_CreateKeypoints(src, template):
    kp1, d1 = getKeypoints(src.greyscale)
    kp2, d2 = getKeypoints(template.greyscale)

    print("Got {}  and {} descs".format(len(d1), len(d2)))

    return keypointData(kp1, d1, kp2, d2)


def detect_FLANNMatch(keypointData):
    """
    Perform FLANN on a pair of keypoints
    :param keypointData: The pair of keypoints
    :return: The good matches
    """
    flann = cv2.FlannBasedMatcher(FLANN_CONFIG, {
        "checks": 50
    })

    matches = flann.knnMatch(np.asarray(keypointData.d2, np.float32), np.asarray(keypointData.d1, np.float32), k=2)

    return [p.x for p in filter(lambda p: p.x.distance < 0.7 * p.y.distance, [pair(m, n) for m, n in matches])]


def getImageBoundingBox(image):
    h, w = image.size
    return np.float32([[0,     0],
                       [0,     h - 1],
                       [w - 1, h - 1],
                       [w - 1, 0]]).reshape(-1, 1, 2)


DEBUG = False

from matplotlib import pyplot as plt
def debugShow(img):
    if not DEBUG:
        return
    plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    plt.show()

#TODO: rename to extract object
def detect_perspectiveTransform(keypointData, goodMatches, src, template):
    """
    Generate the perspective transform for extracting
    :param keypointData:
    :param goodMatches:
    :param src:
    :param template:
    :return:
    """
    # Get all the keypoints that were good matches between the template and the src
    src_pts = np.float32([ keypointData.kp2[m.queryIdx].pt for m in goodMatches ]).reshape(-1,1,2)
    dst_pts = np.float32([ keypointData.kp1[m.trainIdx].pt for m in goodMatches]).reshape(-1,1,2)

    perspectiveCorrectionMatrix, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
    matchesMask = mask.ravel().tolist()

    draw_params = dict(matchColor=(0, 255, 0), # draw matches in green color
                       singlePointColor=None,
                       matchesMask=matchesMask, # draw only inliers
                       flags=2)
    img3 = cv2.drawMatches(template.original, keypointData.kp2, src.original, keypointData.kp1, goodMatches, None, **draw_params)
    debugShow(img3)


    h, w = template.size
    pts = getImageBoundingBox(template)


    # get the perspective correction transform
    dst = cv2.perspectiveTransform(pts, perspectiveCorrectionMatrix)


    img3 = cv2.polylines(src.greyscale, [np.int32(dst)], True, 255, 3, cv2.LINE_AA)
    debugShow(img3)


    dst = cv2.perspectiveTransform(pts, perspectiveCorrectionMatrix)
    perM = cv2.getPerspectiveTransform(np.float32(dst), pts)
    fnd = cv2.warpPerspective(src.original, perM, (w, h))

    debugShow(fnd)

    return fnd


def extractText(img):
    info = img[400:1200, 600:1600]
    debugShow(info)

    info = cv2.cvtColor(info, cv2.COLOR_BGR2GRAY)
    info = cv2.threshold(info, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    text = pytesseract.image_to_string(info)

    print("Found full text:\n---")
    print(text)
    print("---")

    studentID = re.findall("[0-9]{9}", text)
    print(studentID, len(studentID))
    if len(studentID) > 0:
        studentID = studentID[0]
    else:
        studentID = None

    libID = re.findall("[A-Z][0-9]{7}[A-Z]", text)
    if len(libID) > 0:
        libID = libID[0]
    else:
        libID = None

    # Currently we don't care about anything other than the student id
    return results(studentID, libID, (studentID is not None))

"""




#fnd = fnd[0:h, 0:w]
debugShow(fnd)
cv2.imwrite("OUT.jpg", fnd)

info = fnd[400:1200, 600:1600]

info = cv2.cvtColor(info, cv2.COLOR_BGR2GRAY)
info = cv2.threshold(info, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

debugShow(info)
text = pytesseract.image_to_string(info)
print(f"Full text: {text}")
print(re.findall("[0-9]{9}", text)[0])
"""