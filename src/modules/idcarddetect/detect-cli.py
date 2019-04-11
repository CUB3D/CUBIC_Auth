import detect
from matplotlib import pyplot as plt
import cv2


def debugShow(img):
    plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    plt.show()


def draw_keypoints(vis, keypoints, color = (0, 255, 255)):
    for kp in keypoints:
        x, y = kp.pt
        cv2.circle(vis, (int(x), int(y)), 2, color)


if __name__ == "__main__":
    src = detect.detect_ProcessImage(cv2.imread("./card-original.jpg"))
    template = detect.detect_ProcessImage(cv2.imread("./card_blank.jpg"))

    keypointData = detect.detect_CreateKeypoints(src, template)
    goodMatches = detect.detect_FLANNMatch(keypointData)

    if len(goodMatches) > 10:
        img4 = detect.detect_perspectiveTransform(keypointData, goodMatches, src, template)
        debugShow(img4)
        results = detect.extractText(img4)
        print("Student ID: {}".format(results.studentID))
        print("Library ID: {}".format(results.libraryID))
    else:
        print("Not enough matches are found - {}/{}".format(len(goodMatches), 10))
        exit(0)
