import json
import os
import unittest

import image_processor


class TestAvailability(unittest.TestCase):
    def test_compute_availability_single_stall(self):
        # Now include width/height so the helper routines can calculate a rectangle.
        stalls = {"S1": {"x1": 0, "y1": 0, "x2": 100, "y2": 100}}
        preds = [
            {"class": "car", "confidence": 0.9, "x": 50, "y": 50, "width": 10, "height": 10}
        ]

        availability = image_processor.compute_availability_from_predictions(preds, stalls)

        self.assertIn("S1", availability)
        self.assertTrue(availability["S1"]["occupied"])
        self.assertIsInstance(availability["S1"]["cars"], list)
        self.assertEqual(len(availability["S1"]["cars"]), 1)

    def test_geometry_helpers(self):
        det = {"width": 2, "height": 4, "x": 5, "y": 6}
        rect = image_processor.rect_from_prediction(det)
        self.assertEqual(rect, {"x1": 4.0, "y1": 4.0, "x2": 6.0, "y2": 8.0})

        box = {"x1": 0.0, "y1": 0.0, "x2": 10.0, "y2": 10.0}
        self.assertEqual(image_processor.area(box), 100.0)

        b1 = {"x1": 0, "y1": 0, "x2": 10, "y2": 10}
        b2 = {"x1": 5, "y1": 5, "x2": 15, "y2": 15}
        self.assertEqual(image_processor.overlap_area(b1, b2), 25)
        self.assertEqual(image_processor.overlap_area(b1, {"x1": 20, "y1": 20, "x2": 30, "y2": 30}), 0)

    def test_compute_availability_overlap(self):
        stalls = {"S1": {"x1": 0, "y1": 0, "x2": 10, "y2": 10}}
       
        preds = [
            {"class": "car", "confidence": 0.9, "x": 9, "y": 9, "width": 4, "height": 4, "class_id": 0}
        ]
        availability = image_processor.compute_availability_from_predictions(
            preds, stalls, overlap_thresh=0.5
        )
        self.assertTrue(availability["S1"]["occupied"])

    def test_demo_json_file(self):
        filename = os.path.join(os.path.dirname(__file__), "wf_result.json")
        with open(filename) as f:
            data = json.load(f)
        preds = data[0]["predictions"]["predictions"]

        stalls = {"A8": {"x1": 912, "y1": 497, "x2": 1151, "y2": 634}}
        availability = image_processor.compute_availability_from_predictions(
            preds, stalls, overlap_thresh=0.1
        )
        self.assertTrue(availability["A8"]["occupied"])

    def test_run_workflow_on_sample_image(self):
        
        if not os.getenv("ROBOFLOW_API_KEY"):
            self.skipTest("ROBOFLOW_API_KEY not set")

        img_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "LotImages", "lot2 (1).jpg")
        )
        if not os.path.exists(img_path):
            self.skipTest("sample lot image not found")

        preds = image_processor.run_roboflow_workflow(img_path)
        self.assertIsInstance(preds, list)
        self.assertGreater(len(preds), 0)


if __name__ == "__main__":
    unittest.main()
