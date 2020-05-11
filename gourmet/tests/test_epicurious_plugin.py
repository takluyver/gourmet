import os.path
import unittest
import urllib.request

from bs4 import BeautifulSoup

from gourmet.plugins.import_export.website_import_plugins import epicurious_plugin


class DummyImporter(object):

    class WebParser(object):
        pass


class TestAllRecipesPlugin(unittest.TestCase):

    url = "https://www.epicurious.com/recipes/food/views/kiwi-lime-sorbet-233181"

    def _read_html(self, download=True):
        if download:
            with urllib.request.urlopen(self.url) as response:
                self.text = response.read().decode("utf8")
            return

        filename = os.path.join(os.path.dirname(__file__),
                                "recipe_files",
                                "epicurious_com.html")
        with open(filename, encoding="utf8") as f:
            data = f.read()
        return data

    def setUp(self):
        self.text = self._read_html(False)
        self.plugin = epicurious_plugin.EpicuriousPlugin()

    def test_url(self):
        self.assertEqual(self.plugin.test_url(self.url, self.text), 5)
        self.assertEqual(self.plugin.test_url("https://www.epicurious.com/recipes", self.text), 5)
        self.assertEqual(self.plugin.test_url("https://epicurious.com/recipe", self.text), 5)
        self.assertEqual(self.plugin.test_url("https://epicurious.net/", self.text), 0)
        self.assertEqual(self.plugin.test_url("https://google.com", self.text), 0)

    def test_parse(self):
        # Setup
        parser = self.plugin.get_importer(DummyImporter)()
        parser.text = self.text
        parser.soup = BeautifulSoup(self.text, features="lxml")
        # Do the parsing
        parser.preparse()
        # Pick apart results
        result = parser.preparsed_elements

        # Result is a list of tuples (text, keyword) and we are searching for the current
        # keyword. On success we retrieve the text itself and add it to the list.
        # For the name we create a list, but have only one text which we retrieve.
        ingredients = [r[0] for r in result if r[1] == "ingredients"]
        name = [r for r in result if r[1] == "recipe"][0][0]
        instructions = [r[0] for r in result if r[1] == "instructions"]
        modifications = [r[0] for r in result if r[1] == "modifications"]
        yields = [r for r in result if r[1] == "yields"][0][0]
        cooktime = [r for r in result if r[1] == "cooktime"][0][0]

        # Check results
        self.assertEqual(len(ingredients), 3)
        self.assertEqual(yields, "Makes about 3 1/2 cups")
        self.assertEqual(cooktime, "4 hours (includes churning, freezing, and softening time)")

        self.assertEqual(name, "Kiwi-Lime Sorbet")
        self.assertTrue("A perfect ending to any Asian meal." in modifications)
        self.assertTrue("Puree all ingredients in processor." in instructions)
        self.assertTrue(
            "Process in ice cream maker according to manufacturer's instructions. Transfer to container, cover, and freeze until solid, at least 3 hours. (Can be made 2 days ahead. Let stand at room temperature 30 minutes before serving.)" in instructions)


if __name__ == '__main__':
    unittest.main()
