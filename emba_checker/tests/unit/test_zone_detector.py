# -*- coding: utf-8 -*-
"""
test_zone_detector.py - 区域识别测试
"""
import pytest
import sys
sys.path.insert(0, 'D:/Projects/ThesisFormatCheck')

from emba_checker.zone_detector import detect_zones

@pytest.mark.unit
class TestZoneDetector:

    def test_cover_detected(self, zoned_doc):
        zone_map = detect_zones(zoned_doc)
        assert zone_map[0] == "cover"

    def test_abstract_cn_detected(self, zoned_doc):
        zone_map = detect_zones(zoned_doc)
        abstract_zones = [i for i, z in zone_map.items() if z == "abstract_cn"]
        assert len(abstract_zones) >= 2

    def test_abstract_en_detected(self, zoned_doc):
        zone_map = detect_zones(zoned_doc)
        en_zones = [i for i, z in zone_map.items() if z == "abstract_en"]
        assert len(en_zones) >= 1

    def test_body_chapter_detected(self, zoned_doc):
        zone_map = detect_zones(zoned_doc)
        body_zones = [i for i, z in zone_map.items() if z == "body_chapter"]
        assert len(body_zones) >= 2

    def test_references_detected(self, zoned_doc):
        zone_map = detect_zones(zoned_doc)
        ref_zones = [i for i, z in zone_map.items() if z == "references"]
        assert len(ref_zones) >= 1

    def test_acknowledgment_detected(self, zoned_doc):
        zone_map = detect_zones(zoned_doc)
        ack_zones = [i for i, z in zone_map.items() if z == "acknowledgment"]
        assert len(ack_zones) >= 1

    def test_empty_doc_no_crash(self, minimal_doc):
        zone_map = detect_zones(minimal_doc)
        assert all(z == "cover" for z in zone_map.values())

    def test_all_paragraphs_assigned(self, zoned_doc):
        zone_map = detect_zones(zoned_doc)
        assert len(zone_map) == len(zoned_doc.paragraphs)
