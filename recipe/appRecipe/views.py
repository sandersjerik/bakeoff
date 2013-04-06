from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import Context, loader
from django.shortcuts import render, get_object_or_404 #, get_list_or_404

from appRecipe.models import Recipe, Chef, RecipePicture
from appRecipe import forms

from smartfile import BasicClient
import zlib

def home(request):
  recipe_list = Recipe.objects.all()
  chef_list = Chef.objects.all()
  context = { 'chef_list' : chef_list,
              'recipe_list': recipe_list, }
  return render(request, 'recipe/home.html', context)

def recipeIndex(request):
  recipe_list = Recipe.objects.all()
  context = { 'recipe_list': recipe_list,}
  return render(request, 'recipe/recipeIndex.html',context)
  
def recipeDetail(request, recipe_id):
  recipe = get_object_or_404(Recipe, pk=recipe_id)
  return render(request, 'recipe/recipeDetail.html', {'recipe':recipe})
  
def recipeIngredients(request, recipe_id):
  return HttpResponse("You're looking at the ingredients for recipe %s." % recipe_id)

def chefIndex(request):
  chef_list = Chef.objects.all()
  context = { 'chef_list' : chef_list }
  return render(request, 'recipe/chefIndex.html', context)

def chefDetail(request, chef_id):
  chef = get_object_or_404(Chef, pk=chef_id)
  return render(request, 'recipe/chefDetail.html', {'chef':chef})

def getPic(request, pic_name):
  api = BasicClient('VATx6OASrU4KYLaWshrxIvyyYUIl8x','xkpKJ3Wti1cXilKJYnMSqaOLvmNnwe')
  pic = api.get('/path/data/images/',pic_name)
  #img = zlib.decompress(pic.data, 16+zlib.MAX_WBITS)
  img = pic.data
  response = HttpResponse(img, content_type='image')
  return response

  

def addChef(request):
  if request.method == 'POST':
    form = forms.AddChef(request.POST)
    if form.is_valid():
      name = form.cleaned_data['name']
      email = form.cleaned_data['email']
      password = form.cleaned_data['password']
      print password

      chef = Chef(name=name, email=email, password=password)
      chef.save()

      return HttpResponseRedirect('/chefs')
  else:
    form = forms.AddChef()
  return render(request, 'recipe/addChef.html', {'form':form})

def addRecipe(request):
  if request.method == 'POST':
    form = forms.AddRecipe(request.POST, request.FILES)
    if form.is_valid():
      recipeName = form.cleaned_data['recipe_Name']
      prepTime = form.cleaned_data['prep_Time']
      cookTime = form.cleaned_data['cook_Time']
      comments = form.cleaned_data['comments']
      
      instructions = form.cleaned_data['instructions']

      picData = request.FILES['picture'].read()
      picName = request.FILES['picture'].name.split(".")
  

      api = BasicClient('VATx6OASrU4KYLaWshrxIvyyYUIl8x','xkpKJ3Wti1cXilKJYnMSqaOLvmNnwe')
      api.post('/path/data/images/', file=(recipeName+'.'+picName[-1], picData))

      recipe = Recipe(chef=get_object_or_404(Chef, pk=1), name=recipeName, prepTime=prepTime, cookTime=cookTime, chefComment=comments)#TODO: add chef, picture, ingredients, etc
      rpic = RecipePicture(path=recipeName+'.'+picName[-1])
      recipe.mainPicture = rpic
      recipe.save()
      rpic.save()

      return HttpResponseRedirect('/recipes')
  else:
    form = forms.AddRecipe()
  return render(request, 'recipe/addRecipe.html', {'form':form})
