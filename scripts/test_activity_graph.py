import unittest
import xml.etree.ElementTree as ET
from datetime import date, timedelta
from activity_graph import render


class GraphTests(unittest.TestCase):
    def days(self, count):
        return [{'date': (date(2026, 1, 1) + timedelta(days=i)).isoformat(),
                 'contributionCount': count} for i in range(40)]

    def test_real_counts_and_last_31_days(self):
        root = ET.fromstring(render(self.days(2), 'viniman27'))
        ns = {'s': 'http://www.w3.org/2000/svg'}
        self.assertEqual(len(root.findall('.//s:circle', ns)), 31)
        text = ''.join(root.itertext())
        self.assertIn('62 contributions', text)
        self.assertIn('2026-01-10', text)
        self.assertNotIn('2026-01-09', text)

    def test_zero_activity_and_xml_escaping(self):
        root = ET.fromstring(render(self.days(0), 'A & B'))
        self.assertIn('0 contributions', ''.join(root.itertext()))
        self.assertNotIn('nan', ET.tostring(root).decode().lower())

    def test_missing_data_is_not_fabricated(self):
        with self.assertRaises(ValueError):
            render([], 'viniman27')


if __name__ == '__main__':
    unittest.main()
