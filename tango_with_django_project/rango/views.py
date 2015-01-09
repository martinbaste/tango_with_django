from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm

def index(request):
	"""
	Query the database for a list of all the categories currently stored
	Order the categories by no. likes in descending Order
	Retrieve the top 5
	Place the list in our context_dict
	"""
	category_list = Category.objects.order_by("-likes")[:5]
	page_list = Page.objects.order_by("-views")[:5]
	context_dict = {'categories' : category_list, 'pages': page_list}
	return render(request, 'rango/index.html', context_dict)

def category(request, category_name_slug):
	#Create a context dict
	context_dict = {}
	try:
		category = Category.objects.get(slug=category_name_slug)
		context_dict['category_name'] = category.name

		pages = Page.objects.filter(category = category)
		context_dict['pages'] = pages
		context_dict['category'] = category
		context_dict['category_name_slug'] = category_name_slug
	except Category.DoesNotExist:
		pass
	return render(request, 'rango/category.html', context_dict)

def add_page(request, category_name_slug):
	try:
		cat = Category.objects.get(slug = category_name_slug)
	except Category.DoesNotExist:
		cat = None
	if request.method == 'POST':
		form = PageForm(request.POST)
		if form.is_valid():
			if cat:
				page = form.save(commit=False)
				page.category = cat
				page.views = 0
				page.save()
				return category(request,category_name_slug)

		else:
			print form.errors
	else:
		form = PageForm()
	context_dict = {'form': form, 'category': cat}

	return render(request, 'rango/add_page.html', context_dict)

def add_category(request):
	#A Http Post?
	if request.method == 'POST':
		form = CategoryForm(request.POST)
		if form.is_valid():
			form.save(commit=True)
			return index(request)
		else:
			print form.errors
	else:
		form = CategoryForm()
	return render(request, 'rango/add_category.html', {'form': form})


def about(request):
	return HttpResponse("Rango says here is the about page.<br/> <a href='/rango/'> Index </a>")