from rango.bing_search import run_query
from django.shortcuts import render, redirect
from django.http import HttpResponse
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from datetime import datetime


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

	visits = request.session.get('visits')

	if not visits:
		visits = 1

	reset_last_visit_time = False

	last_visit = request.session.get('last_visit')
	if last_visit:
		last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")
		if (datetime.now() - last_visit_time).seconds > 0:
			visits = visits + 1	
			reset_last_visit_time = True
	else:
		reset_last_visit_time = True


	if reset_last_visit_time:
		request.session['last_visit'] = str(datetime.now())
		request.session['visits'] = visits
	context_dict['visits'] = visits

	response = render(request, 'rango/index.html', context_dict)
	return response





def category(request, category_name_slug):
	#Create a context dict
	context_dict = {}
	context_dict['result_list'] = None
	context_dict['query'] = None
	if request.method == "POST":
		query = request.POST['query'].strip()

		if query:
			# Run our Bing function to get the results list!
			result_list = run_query(query)
			context_dict['result_list']= result_list
			context_dict['query'] = query
			
		
	try:
		category = Category.objects.get(slug=category_name_slug)
		context_dict['category_name'] = category.name
		pages = Page.objects.filter(category=category).order_by('-views')
		context_dict['pages'] = pages
		context_dict['category'] = category
		context_dict['category_name_slug'] = category_name_slug
	except Category.DoesNotExist:
		pass
	if not context_dict['query']:
		context_dict['query'] = category.name
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
	return render(request, 'rango/about.html', {})

def register_profile(request):
	registered = False
	if request.method == "POST":
		profile_form = UserProfileForm(data = request.POST)
		if profile_form.is_valid():
			profile = profile_form.save(commit = False)
			profile.user = request.user
			if 'picture' in request.FILES:
				profile.picture = request.FILES['picture']
			profile.save()
			registered = True
		else:
			print profile_form.errors
	else:
		profile_form = UserProfileForm()
	return render(request, 'rango/profile_registration.html', {'profile_form' : profile_form, 'registered' : registered})


# def register(request):
# 	if request.session.test_cookie_worked():
# 		print ">>> TEST COOKIE WORKED!"
# 		request.session.delete_test_cookie()
# 	registered = False
# 	if request.method == "POST":
# 		user_form = UserForm(data=request.POST)
# 		profile_form = UserProfileForm(data = request.POST)

# 		if user_form.is_valid() and profile_form.is_valid():
# 			user = user_form.save()
# 			user.set_password(user.password)
# 			user.save()
# 			profile = profile_form.save(commit = False)
# 			profile.user = user

# 			if 'picture' in request.FILES:
# 				profile.picture = request.FILES['picture']
# 			profile.save()

# 			registered = True
# 		else:
# 			print user_form.errors, profile_form.errors
# 	else:
# 		user_form = UserForm()
# 		profile_form = UserProfileForm()

# 	return render(request, 'rango/register.html', {'user_form': user_form, 'profile_form': profile_form, 'registered' : registered})

# def user_login(request):
# 	if request.method == "POST":
# 		username = request.POST['username']
# 		password = request.POST['password']

# 		user = authenticate(username=username, password=password)

# 		if user:
# 			if user.is_active:
# 				login(request,user)
# 				return HttpResponseRedirect('/rango/')
# 			else:
# 				return HttpResponse("Your Rango account is disabled.")

# 		else:
# 			print "Invalid login details: {0}, {1}".format(username, password)
# 			return HttpResponse("invalid login details supplied")

# 	else:
# 		return render(request, 'rango/login.html', {})


@login_required
def restricted(request):
	return render(request, 'rango/restricted.html', {})

# @login_required
# def user_logout(request):
# 	logout(request)
# 	return HttpResponseRedirect("/rango/")




def search(request):

    result_list = []

    if request.method == 'POST':

        query = request.POST['query'].strip()

        if query:
            # Run our Bing function to get the results list!
            result_list = run_query(query)

    return render(request, 'rango/search.html', {'result_list': result_list})

def track_url(request):
	if request.method == 'GET':
	    if 'page_id' in request.GET:
	        page_id = request.GET['page_id']

	try:
		page = Page.objects.get(id = page_id)
	except Page.DoesNotExist:
		page = None
	if page:
		page.views += 1
		page.save()
		return redirect(page.url)
	return HttpResponseRedirect('/rango/')	
