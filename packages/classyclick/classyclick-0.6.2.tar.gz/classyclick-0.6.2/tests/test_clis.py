from unittest import TestCase

from click.testing import CliRunner


class Test(TestCase):
    def test_hello(self):
        from .cli_one import Hello

        runner = CliRunner()
        result = runner.invoke(Hello.click, args=['--name', 'classyclick'])

        self.assertEqual(result.exit_code, 0)
        self.assertIn('Hello, classyclick!', result.output)

    def test_hello_class(self):
        from .cli_one import Hello

        kls = Hello
        kls(name='classyclick')

    def test_hello_no_types(self):
        def _a():
            from .cli_two import Hello

            # no-op until "ruff format" gets pragma support (like # fmt: off)
            Hello.click()

        self.assertRaisesRegex(TypeError, "tests.cli_two.Hello is missing type for classy field 'name'", _a)

    def test_bye(self):
        from .cli_three import Bye

        runner = CliRunner()
        result = runner.invoke(Bye.click, args=['--name', 'classyclick'])

        self.assertEqual(result.exit_code, 0)
        self.assertIn('Bye, classyclick!', result.output)

    def test_next(self):
        from .cli_four import Next

        runner = CliRunner()
        result = runner.invoke(Next.click, args=['3'])

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, '4\n')
