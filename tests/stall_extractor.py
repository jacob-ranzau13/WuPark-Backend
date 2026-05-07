import cv2
import numpy as np
import matplotlib.pyplot as plt
import json
from datetime import datetime


clicked_points = []

def mouse_callback(event, x, y, flags, param):
    global clicked_points
    if event == cv2.EVENT_LBUTTONDOWN:
        clicked_points.append({'x': x, 'y': y})
        print(f"Clicked: x={x}, y={y}")
       
        output_file = 'tests/clicked_coordinates.json'
        with open(output_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'points': clicked_points
            }, f, indent=2)
        print(f"Saved to {output_file}")




def click_to_capture(image_path):
    """Display image and capture mouse clicks"""
    global clicked_points
    clicked_points = []  # Reset points
   
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Could not load image from {image_path}")
        return
   
    window_name = "Click on image - Press 'q' to quit"
    cv2.namedWindow(window_name)
    cv2.setMouseCallback(window_name, mouse_callback)
   
    print("Click on the image to capture coordinates. Press 'q' to quit.")
   
    while True:
        # Draw circles on clicked points
        display_img = img.copy()
        for point in clicked_points:
            cv2.circle(display_img, (point['x'], point['y']), 5, (0, 0, 255), -1)
            cv2.putText(display_img, f"({point['x']},{point['y']})",
                       (point['x'] + 10, point['y'] - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
       
        cv2.imshow(window_name, display_img)
       
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
   
    cv2.destroyAllWindows()
    return clicked_points




def extract_stall_boundaries(image_path, min_column_gap=20, stall_width_estimate=50, show=True):
    img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)




    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)




    lines = cv2.HoughLinesP(thresh, 1, np.pi/180, threshold=60,
                            minLineLength=20, maxLineGap=5)




    stall_boundaries = []
    if lines is not None:
        verticals = [l[0] for l in lines if abs(l[0][0] - l[0][2]) < 5]
        verticals = sorted(verticals, key=lambda x: x[0])




        xs = []
        for v in verticals:
            if not xs or abs(v[0] - xs[-1]) > min_column_gap:
                xs.append(v[0])




        for i, x in enumerate(xs):
            col_mask = thresh[:, x-2:x+2]
            hist = np.sum(col_mask, axis=1)




            divs = np.where(hist > np.max(hist)*0.5)[0]
            if len(divs) > 1:
                clusters, cluster = [], [divs[0]]
                for d in divs[1:]:
                    if d - cluster[-1] < 10:
                        cluster.append(d)
                    else:
                        clusters.append(cluster)
                        cluster = [d]
                clusters.append(cluster)




                lines_y = [int(np.mean(c)) for c in clusters]




                # Calculate stall boundaries between dividing lines
                col_stalls = []
                for j in range(len(lines_y)-1):
                    # Calculate x boundaries
                    if i == 0:
                        x1 = max(0, x - stall_width_estimate // 2)
                    else:
                        x1 = (xs[i-1] + x) // 2
                   
                    if i == len(xs) - 1:
                        x2 = min(img.shape[1], x + stall_width_estimate // 2)
                    else:
                        x2 = (x + xs[i+1]) // 2
                   
                    # Y boundaries are the dividing lines
                    y1 = lines_y[j]
                    y2 = lines_y[j+1]
                   
                    col_stalls.append({
                        'x1': x1,
                        'y1': y1,
                        'x2': x2,
                        'y2': y2
                    })
               
                stall_boundaries.append(col_stalls)




    if show:
        debug_img = img.copy()
        for col in stall_boundaries:
            for stall in col:
                cv2.rectangle(debug_img,
                            (stall['x1'], stall['y1']),
                            (stall['x2'], stall['y2']),
                            (0, 255, 0), 2)
                # Draw center point
                cx = (stall['x1'] + stall['x2']) // 2
                cy = (stall['y1'] + stall['y2']) // 2
                cv2.circle(debug_img, (cx, cy), 5, (0, 0, 255), -1)
        plt.figure(figsize=(10, 10))
        plt.imshow(cv2.cvtColor(debug_img, cv2.COLOR_BGR2RGB))
        plt.title("Detected Stall Boundaries")
        plt.show()




    return stall_boundaries




if __name__ == "__main__":
    image_path = "LotImages/lot2_eoh_final.jpg"
   
    # Use click capture mode
    print("Starting click capture mode...")
    points = click_to_capture(image_path)
   
    print(f"\nTotal points captured: {len(points)}")
    for i, point in enumerate(points, 1):
        print(f"Point {i}: x={point['x']}, y={point['y']}")