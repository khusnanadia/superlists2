from django.core.urlresolvers import resolve
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.test import TestCase

from lists.models import Item
from lists.views import home_page

class HomePageTest(TestCase):

	def test_root_url_resolves_to_home_page_view(self):
		found = resolve('/')
		self.assertEqual(found.func, home_page)

	def test_home_page_returns_correct_html(self):
		request = HttpRequest()
		response = home_page(request)
		expected_html = render_to_string('home.html', { 'comment' : 'yey, waktunya berlibur'})
		self.assertEqual(response.content.decode(), expected_html)

	def test_home_page_displays_all_list_items(self):
		Item.objects.create(text='itemey 1')
		Item.objects.create(text='itemey 2')

		request = HttpRequest()
		response = home_page(request)

		self.assertIn('itemey 1', response.content.decode())
		self.assertIn('itemey 2', response.content.decode())

	def test_home_page_can_save_a_POST_request(self):
		request = HttpRequest()
		request.method = 'POST'
		request.POST['item_text'] = 'A new list item'

		response = home_page(request)

		self.assertEqual(Item.objects.count(), 1)
		new_item = Item.objects.first()
		self.assertEqual(new_item.text, 'A new list item')

	def test_home_page_redirects_after_POST(self):
		request = HttpRequest()
		request.method = 'POST'
		request.POST['item_text'] = 'A new list item'

		response = home_page(request)

		self.assertEqual(response.status_code, 302)
		self.assertEqual(response['location'], '/')

	def test_home_page_only_saves_items_when_necessary(self):
		request = HttpRequest()
		home_page(request)
		self.assertEqual(Item.objects.count(), 0)

	def test_list_null(self):
		request = HttpRequest()
		response = home_page(request)

		self.assertEqual(Item.objects.count(),0)
		self.assertIn('yey, waktunya berlibur', response.content.decode())

	def test_list_less_that_5(self):
		Item.objects.create(text='komentar pribadi 1')
		
		request = HttpRequest()
		response = home_page(request)
		
		self.assertTrue(Item.objects.count() < 5)
		self.assertIn('sibuk tapi santai', response.content.decode())

	def test_list_greater_equal_than_5(self):
		Item.objects.create(text='komentar pribadi 1')
		Item.objects.create(text='komentar pribadi 2')
		Item.objects.create(text='komentar pribadi 3')
		Item.objects.create(text='komentar pribadi 4')
		Item.objects.create(text='komentar peibadi 5')

		request = HttpRequest()
		response = home_page(request)

		self.assertTrue(Item.objects.count() >= 5)
		self.assertIn('oh tidak', response.content.decode())

class ItemModelTest(TestCase):

	def test_saving_and_retrieving_items(self):
		first_item = Item()
		first_item.text = 'The first (ever) list item'
		first_item.save()

		second_item = Item()
		second_item.text = 'Item the second'
		second_item.save()

		saved_items = Item.objects.all()
		self.assertEqual(saved_items.count(), 2)

		first_saved_item = saved_items[0]
		second_saved_item = saved_items[1]
		self.assertEqual(first_saved_item.text, 'The first (ever) list item')
		self.assertEqual(second_saved_item.text, 'Item the second')
