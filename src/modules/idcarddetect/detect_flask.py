from . import detect
import cv2
import numpy as np

def doFind(ingData):
    src = cv2.imdecode(np.array(bytearray(ingData), dtype=np.uint8), -1)
    src = detect.detect_ProcessImage(src)
    template = detect.detect_ProcessImage(cv2.imread("dependencies/idcarddetect/card_blank.jpg"))

    keypointData = detect.detect_CreateKeypoints(src, template)
    goodMatches = detect.detect_FLANNMatch(keypointData)

    if len(goodMatches) > 10:
        img4 = detect.detect_perspectiveTransform(keypointData, goodMatches, src, template)
        results = detect.extractText(img4)

        if results.success:
            return {
                "Status": 0,
                "StudentID": results.studentID,
                "LibraryID": results.libraryID
            }

    return {
        "Status": 1,
        "Error": "ID card not found in image"
    }
