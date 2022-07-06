import cv2
import numpy as np
import argparse
import imghdr

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", default="assets/avengers.jpeg", help="name of image in the same path (es: avengers.jpeg)")
args = vars(ap.parse_args())

class BoundingBoxWidget(object):
    def __init__(self):
        
        self.original_image = cv2.imread(args['image'])
        self.clone = self.original_image.copy()
        self.drawing = False
        self.name_image = str(args['image']).split('.', 1)[0]
        
        cv2.namedWindow(self.name_image)
        cv2.setMouseCallback(self.name_image, self.extract_coordinates)

        # Bounding box reference points
        self.start_point = ()
        self.end_point = ()


    def extract_coordinates(self, event, x, y, flags, parameters):
        # Record starting (x,y) coordinates on left mouse button click
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.start_point = (x,y)
        # Draw rectangle when mouse move
        elif event == cv2.EVENT_MOUSEMOVE:
            self.clone = self.original_image.copy()
            if self.drawing:
                cv2.rectangle(self.clone, self.start_point, (x, y), (36,255,12), 2)
                self.show_image()

        # Record ending (x,y) coordintes on left mouse button release
        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False
            self.end_point = (x,y)
            # print('first point: {}'.format(self.start_point))
            # print('second point: {}'.format(self.end_point))

            # Draw rectangle 
            cv2.rectangle(self.clone, self.start_point, self.end_point, (36,255,12), 2)
            self.show_image()

            # Start and end point to create bounding box
            w, h = (0, 0)
            if self.end_point[0] > self.start_point[0]:
                if self.end_point[1] > self.start_point[1]:
                    bounding_box = self.start_point[0], self.start_point[1], self.end_point[0] - self.start_point[0], self.end_point[1] - self.start_point[1]
                else:
                    w, h = self.end_point[0] - self.start_point[0], self.start_point[1] - self.end_point[1]
                    bounding_box = self.start_point[0], self.start_point[1]-h, w, h
            else:
                if self.end_point[1] < self.start_point[1]:
                    bounding_box = self.end_point[0], self.end_point[1], self.start_point[0] - self.end_point[0], self.start_point[1] - self.end_point[1]
                else:
                    w, h = self.start_point[0] - self.end_point[0], self.end_point[1] - self.start_point[1]
                    bounding_box = self.end_point[0], self.end_point[1]-h, w, h
            
            grabcut_algorithm(self.original_image, bounding_box)

    def show_image(self):
        return cv2.imshow(self.name_image, self.clone)


def grabcut_algorithm(original_image, bounding_box):
    
    # Attributes of the image
    segment = np.zeros(original_image.shape[:2], np.uint8)

    # Get values of bounding box
    x, y, width, height = bounding_box
    segment[y:y+height, x:x+width] = 1
    
    # Variables for the look of the masked part
    background_mdl = np.zeros((1,65), np.float64)
    foreground_mdl = np.zeros((1,65), np.float64)
    
    # Function grabCut
    cv2.grabCut(original_image, segment, bounding_box, background_mdl, foreground_mdl, 5, cv2.GC_INIT_WITH_RECT)

    # New mask and apply the mask to the original image
    new_mask = np.where((segment==2) | (segment==0), 0, 1).astype('uint8')
    new_image = original_image * new_mask[:, :, np.newaxis]

    # Display result
    cv2.imshow('Result', new_image)


if __name__ == '__main__':
    try:
        imghdr.what(args['image'])
        boundingbox_widget = BoundingBoxWidget()
        while True:
            boundingbox_widget.show_image()
            key = cv2.waitKey(1)

            # Close program with keyboard 'q'
            if key == ord('q'):
                cv2.destroyAllWindows()
                exit(1)
    except:
        print('No such file or is a directory: ', args['image'])
