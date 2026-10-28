"""Synthetic preview fan-out; no web server, model or media access."""

import io
import threading
import unittest
from dataclasses import replace
from unittest.mock import patch

from PIL import Image

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.inference.streaming import FrameStamp
from ai_exam_monitoring.web.preview import PreviewBuffer


class PreviewTests(unittest.TestCase):
    def stamp(self, index=0, epoch=0):
        return FrameStamp("fixture", epoch, index, float(index), index + 1, 16, 16)

    def test_slow_readers_get_latest_without_consuming_other_readers(self):
        buffer = PreviewBuffer("fixture", quality=85)
        for index in range(10):
            buffer.publish(self.stamp(index), Image.new("RGB", (16, 16), "white"))
        first = buffer.wait(0, 0)
        second = buffer.wait(0, 0)
        self.assertIs(first, second)
        self.assertEqual(first.stamp.sequence, 9)
        self.assertEqual(first.revision, 10)
        with Image.open(io.BytesIO(first.jpeg)) as decoded:
            self.assertEqual(decoded.size, (16, 16))
            self.assertEqual(decoded.getpixel((0, 0)), (255, 255, 255))

    def test_reset_discards_old_epoch_and_allows_source_time_to_restart(self):
        buffer = PreviewBuffer("fixture", quality=85)
        image = Image.new("RGB", (16, 16))
        buffer.publish(self.stamp(10), image)
        buffer.reset(1)
        reset = buffer.wait(1, 0)
        self.assertIsNone(reset.jpeg)
        self.assertFalse(buffer.publish(self.stamp(11), image))
        self.assertTrue(buffer.publish(self.stamp(0, 1), image))
        self.assertEqual(buffer.snapshot().stamp.epoch, 1)

    def test_reset_while_encoding_rejects_late_pixels(self):
        buffer = PreviewBuffer("fixture", quality=85)
        original = Image.Image.save
        def save(image, *args, **kwargs):
            buffer.reset(1)
            original(image, *args, **kwargs)
        with patch.object(Image.Image, "save", save):
            self.assertFalse(buffer.publish(self.stamp(), Image.new("RGB", (16, 16))))
        self.assertIsNone(buffer.snapshot().jpeg)

    def test_close_wakes_readers_and_is_idempotent(self):
        buffer = PreviewBuffer("fixture", quality=85)
        entered = threading.Event()
        results = []
        def reader():
            entered.set()
            results.append(buffer.wait(0, 2))
        thread = threading.Thread(target=reader)
        thread.start()
        self.assertTrue(entered.wait(1))
        buffer.close()
        buffer.close()
        thread.join(1)
        self.assertFalse(thread.is_alive())
        self.assertTrue(results[0].closed)
        self.assertIsNone(results[0].jpeg)
        self.assertEqual(results[0].revision, 1)
        self.assertFalse(buffer.publish(self.stamp(), Image.new("RGB", (16, 16))))

    def test_identity_geometry_and_order_guards(self):
        buffer = PreviewBuffer("fixture", quality=85)
        image = Image.new("RGB", (16, 16))
        for stamp, payload in (
            (replace(self.stamp(), session_id="other"), image),
            (self.stamp(), Image.new("RGB", (20, 16))),
        ):
            with self.assertRaises(DataContractError):
                buffer.publish(stamp, payload)
        buffer.publish(self.stamp(), image)
        with self.assertRaises(DataContractError):
            buffer.publish(self.stamp(), image)
        with self.assertRaises(DataContractError):
            buffer.reset(0)
