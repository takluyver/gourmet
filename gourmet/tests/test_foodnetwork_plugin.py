import os.path
import unittest
from bs4 import BeautifulSoup

from gourmet.plugins.import_export.website_import_plugins import foodnetwork_plugin

class DummyImporter(object):

    class WebParser(object):

        def preparse(dummy):
            pass


class TestFoodnetworkPlugin(unittest.TestCase):

    url = "https://foodnetwork.co.uk/recipes/pan-roasted-chicken-thighs-grapes-and-olives/"

    def _read_html(self, download=True):
        if download:
            with urllib.request.urlopen(self.url) as response:
                self.text = response.read().decode("utf8")
            return

        filename = os.path.join(os.path.dirname(__file__),
                                "recipe_files",
                                "foodnetwork.html")
        with open(filename, encoding="utf8") as f:
            data = f.read()
        return data

    def setUp(self):
        self.text = self._read_html(False)
        self.plugin = foodnetwork_plugin.FoodNetworkPlugin()

    def test_url(self):
        self.assertEqual(self.plugin.test_url(self.url, self.text), 5)
        self.assertEqual(self.plugin.test_url("http://www.foodnetwork.co.uk/recipes", self.text), 5)
        self.assertEqual(self.plugin.test_url("http://foodnetwork.co.uk/recipes", self.text), 5)
        self.assertEqual(self.plugin.test_url("http://www.foodnetwork.co.uk", self.text), 5)
        self.assertEqual(self.plugin.test_url("http://www.foodnetwork.net", self.text), 0)
        self.assertEqual(self.plugin.test_url("http://google.com", self.text), 0)

    def test_parse(self):
        # Setup
        parser = self.plugin.get_importer(DummyImporter)()
        parser.soup = BeautifulSoup(self.text, "lxml")
        # Do the parsing
        parser.preparse()
        # Pick apart results
        result = parser.preparsed_elements

        # Result is a list of tuples (text, keyword) and we are searching for the current
        # keyword. On success we retrieve the text itself and add it to the list.
        # For the name we create a list, but have only one text which we retrieve.
        ingredients = [r[0] for r in result if r[1] == "ingredients"]
        name = [r for r in result if r[1] == "title"][0][0]
        instructions = [r[0] for r in result if r[1] == "recipe"]
        preptime = [r for r in result if r[1] == "preptime"][0][0]
        cooktime = [r for r in result if r[1] == "cooktime"][0][0]
        yields = [r for r in result if r[1] == "yields"][0][0]

        # Check results
        self.assertEqual(len(ingredients), 11)
        self.assertEqual(preptime, "15 mins")
        self.assertTrue(cooktime, "25 mins")
        self.assertEqual(yields, "4")

        self.assertEqual(name, "Pan Roasted Chicken Thighs with Grapes and Olives")

        self.assertTrue(
            "Place the skillet underneath the broiler to crisp the chicken skin, about 2 minutes. Watch carefully to avoid burning." in instructions)


if __name__ == '__main__':
    unittest.main()
