import unittest

import image_processor


class TestAvailability(unittest.TestCase):
    def test_compute_availability_single_stall(self):
        # Single stall occupying coordinates 0..100
        stalls = {"S1": {"x1": 0, "y1": 0, "x2": 100, "y2": 100}}
        preds = [{"class": "car", "confidence": 0.9, "x": 50, "y": 50}]

        availability = image_processor.compute_availability_from_predictions(preds, stalls)

        self.assertIn("S1", availability)
        self.assertTrue(availability["S1"]["occupied"])
        self.assertIsInstance(availability["S1"]["cars"], list)
        self.assertEqual(len(availability["S1"]["cars"]), 1)


if __name__ == "__main__":
    unittest.main()
