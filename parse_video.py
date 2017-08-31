import numpy as np
import cv2
import time

def myPCA(img):
    y, x = np.nonzero(img)
    x_mean = np.mean(x)
    y_mean = np.mean(y)
    x = x - x_mean
    y = y - y_mean
    x[np.abs(x)>40] = 0
    y[np.abs(y)>40] = 0
    
    coords = np.vstack([x, y])
    cov = np.cov(coords)
    evals, evecs = np.linalg.eig(cov)
    sort_indices = np.argsort(evals)[::-1]
    evec1, evec2 = evecs[:, sort_indices]
    x_v1, y_v1 = evec1  # Eigenvector with largest eigenvalue
    # x_v2, y_v2 = evec2
    scale = 30
    x1 = int(-x_v1*scale*2+x_mean)
    y1 = int(-y_v1*scale*2+y_mean)
    x2 = int(x_v1*scale*2+x_mean)
    y2 = int(y_v1*scale*2+y_mean)
    # plt.plot([x_v1*-scale*2+x_mean, x_v1*scale*2+x_mean],
             # [y_v1*-scale*2+y_mean, y_v1*scale*2+y_mean], color='red')
    # plt.plot([x_v2*-scale, x_v2*scale],
             # [y_v2*-scale, y_v2*scale], color='blue')
    return x1, y1, x2, y2


def raw_moment(data, i_order, j_order):
    nrows, ncols = data.shape
    y_indices, x_indicies = np.mgrid[:nrows, :ncols]
    return (data * x_indicies**i_order * y_indices**j_order).sum()

def moments_cov(data):
    data_sum = data.sum()
    m10 = raw_moment(data, 1, 0)
    m01 = raw_moment(data, 0, 1)
    x_centroid = m10 / data_sum
    y_centroid = m01 / data_sum
    u11 = (raw_moment(data, 1, 1) - x_centroid * m01) / data_sum
    u20 = (raw_moment(data, 2, 0) - x_centroid * m10) / data_sum
    u02 = (raw_moment(data, 0, 2) - y_centroid * m01) / data_sum
    cov = np.array([[u20, u11], [u11, u02]])
    return cov

def moments(img):
    y, x = np.nonzero(img)
    x_mean = np.mean(x)
    y_mean = np.mean(y)
    cov = moments_cov(img)
    evals, evecs = np.linalg.eig(cov)
    sort_indices = np.argsort(evals)[::-1]
    evec1, evec2 = evecs[:, sort_indices]
    x_v1, y_v1 = evec1  # Eigenvector with largest eigenvalue
    x_v2, y_v2 = evec2
    scale = 30
    x1 = int(-x_v1*scale*2+x_mean)
    y1 = int(-y_v1*scale*2+y_mean)
    x2 = int(x_v1*scale*2+x_mean)
    y2 = int(y_v1*scale*2+y_mean)
    # plt.plot([x_v1*-scale*2+x_mean, x_v1*scale*2+x_mean],
             # [y_v1*-scale*2+y_mean, y_v1*scale*2+y_mean], color='red')
    # plt.plot([x_v2*-scale, x_v2*scale],
             # [y_v2*-scale, y_v2*scale], color='blue')
    return x1, y1, x2, y2


def lin_reg(img):
    y, x = np.nonzero(img)
    x_diff = x.max() - x.min()
    y_diff = y.max() - y.min()

    transposed = False
    if (y_diff > x_diff):
        transposed = True
        temp = x
        x = y
        y = temp

    x_mean = np.mean(x)
    y_mean = np.mean(y)

    scale = 80
    a,b = np.polyfit(x,y,1)
    print("a {} b {}".format(a, b))
    x1 = x_mean - scale
    y1 = x1 * a + b
    x2 = x_mean + scale
    y2 = x2 * a + b

    if (transposed):
        temp = x1
        x1 = y1
        y1 = temp
        temp = x2
        x2 = y2
        y2 = temp
    return int(x1),int(y1),int(x2),int(y2)

def diff_gray(image, prev_image):
    result = (128 + (image / 2)) - (prev_image / 2)
    delta = 16
    result[result > 128 + delta] = 255
    result[result <= 128 - delta] = 255
    result[result != 255] = 0
    return result

mask = np.zeros((480,852))
# mask.fill(0)
# cv2.rectangle(mask, box_corner1, box_corner2, 255, -1)
# empty[mask == 0] = (0, 0, 0)
# empty_gray[mask == 0] = 0

cap = cv2.VideoCapture('330 minute 1.mp4')

detector = cv2.SimpleBlobDetector_create()
prev_frame = np.zeros((480,852))
count = 0
playVideo = True
step = False
while(cap.isOpened()):
    if playVideo or step:
        step = False
        ret, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        out_frame = np.copy(gray)
        mask = diff_gray(gray, prev_frame)

        # mask out anything not the bug (prev / current) frame
        out_frame[mask == 0] = 0
        # clean "prev" frame location
        out_frame[out_frame > 170] = 0
        out_frame[out_frame != 0] = 255

        x1,y1,x2,y2 = lin_reg(out_frame)
        cv2.line(out_frame, (x1,y1), (x2,y2), 255)

        cv2.imshow('frame',out_frame.astype(np.uint8))
        prev_frame = gray
    # print(np.max(out_frame), np.min(out_frame), np.mean(out_frame))
        count+=1
    # time.sleep(0.1)

    char = cv2.waitKey(1)
    if char == ord('q'):
        break
    elif char == ord('n'):
        step = True
    elif char == ord('p'):
        playVideo = not playVideo

cap.release()
cv2.destroyAllWindows()

