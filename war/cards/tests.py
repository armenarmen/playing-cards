from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.test import TestCase
from cards.forms import EmailUserCreationForm
from cards.models import Player
from cards.test_utils import run_pyflakes_for_package, run_pep8_for_package
from cards.utils import create_deck


# class UtilTestCase(TestCase):
#     def test_create_deck(self):
#         """Check if 52 cards, no more no less, were made """
#         create_deck()
#         self.assertEqual(Card.objects.count(), 52)
#
#
# class ModelTestCase(TestCase):
#     def test_get_ranking(self):
#         """Test that we get the proper ranking for a card"""
#         card = Card.objects.create(suit=Card.CLUB, rank='jack')
#         self.assertEqual(card.get_ranking(), 11)
#
#
#     def test_war_result_user_win(self):
#         """see if winning coniditons return a win"""
#         user = Card.objects.create(suit=Card.CLUB, rank='king')
#         comp = Card.objects.create(suit=Card.CLUB, rank='jack')
#
#         self.assertEqual(Card.get_war_result(user, comp), 1)
#
#     def test_war_result_user_draw(self):
#         """see if winning coniditons return a win"""
#         user = Card.objects.create(suit=Card.CLUB, rank='king')
#         comp = Card.objects.create(suit=Card.CLUB, rank='king')
#
#         self.assertEqual(Card.get_war_result(user, comp), 0)
#
#
#     def test_war_result_user_loss(self):
#         """see if winning coniditons return a win"""
#         user = Card.objects.create(suit=Card.CLUB, rank='jack')
#         comp = Card.objects.create(suit=Card.CLUB, rank='king')
#
#         self.assertEqual(Card.get_war_result(user, comp), -1)


class FormTestCase(TestCase):
    def test_clean_username_exception(self):
        # this creates a guy with a name, so an error can happen
        Player.objects.create_user(username="test-user")

        # set up form for testing
        form = EmailUserCreationForm()
        form.cleaned_data = {'username': 'test-user'}

        # check for an error
        with self.assertRaises(ValidationError):
            form.clean_username()

    def test_clean_username_ok(self):
        form = EmailUserCreationForm()
        form.cleaned_data = {'username': 'test-user'}
        self.assertEqual(form.clean_username(), 'test-user')


class ViewTestCAse(TestCase):
    def setUp(self):
        create_deck()

    def test_home_page(self):
        response = self.client.get(reverse('home'))
        self.assertIn('<p>Suit: spade, Rank: two</p>', response.content)
        self.assertEqual(response.context['cards'].count(), 52)

    def test_register_page(self):
        username = "new-user"
        data = {
            'username': username,
            'email': 'test@test.com',
            'password1': 'test',
            'password2': 'test'
        }
        response = self.client.post(reverse('register'), data)

        self.assertTrue(Player.objects.filter(username=username).exists())

        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertTrue(response.get('location').endswith(reverse('profile')))

    def test_faq_view(self):
        response = self.client.get(reverse('faq'))
        self.assertIn("<p>Q: Can I win real money on this website?</p>", response.content)

    def test_filters_view(self):
        response = self.client.get(reverse('filters'))
        self.assertIn("<p>\n            Capitalized Suit: 3 <br>\n            "
                      "Uppercased Rank: SIX\n        </p>", response.content)

    def test_login_page(self):
        password = "password"
        username = Player.objects.create_user(username='test', email='test@test.com', password=password)
        self.client.login(username=username.username, password=password)
        response = self.client.get(reverse('profile'))
        self.assertIn("<h2>Past Games</h2>", response.content)


class SyntaxTest(TestCase):
    def test_syntax(self):
        """
        Run pyflakes/pep8 across the code base to check for potential errors.
        """
        packages = ['cards']
        warnings = []
        # Eventually should use flake8 instead so we can ignore specific lines via a comment
        for package in packages:
            warnings.extend(run_pyflakes_for_package(package, extra_ignore=("_settings",)))
            warnings.extend(run_pep8_for_package(package, extra_ignore=("_settings",)))
        if warnings:
            self.fail("{0} Syntax warnings!\n\n{1}".format(len(warnings), "\n".join(warnings)))
