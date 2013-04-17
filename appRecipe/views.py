from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import Context, loader
from django.shortcuts import render, get_object_or_404 #, get_list_or_404
from appRecipe.models import Recipe, Chef, RecipePicture, Ingredient, UnitOfMeasure, RecipeIngredient
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required

from appRecipe import forms

from smartfile import BasicClient

import Image
#import zlib

def home(request):
  recipe_list = Recipe.objects.all()
  chef_list = Chef.objects.all()
  recipe_picture_list = RecipePicture.objects.all()
  context = { 'chef_list' : chef_list,
              'recipe_list': recipe_list,
              'recipe_picture_list' : recipe_picture_list, }
  return render(request, 'recipe/home.html', context)

def recipeIndex(request):
  recipe_list = Recipe.objects.all()
  context = { 'recipe_list': recipe_list,}
  return render(request, 'recipe/recipeIndex.html',context)
  
def recipeDetail(request, recipe_id):
  recipe = get_object_or_404(Recipe, pk=recipe_id)
  review = None
  if request.user.is_authenticated():
    revList = recipe.review_set.filter(chef_id=request.user.id)
    if revList.count() > 0:
      review = revList[0]
  return render(request, 'recipe/recipeDetail.html', {'recipe':recipe, 'review':review})
  
def recipeReviews(request, recipe_id):
  recipe = get_object_or_404(Recipe, pk=recipe_id)
  return render(request, 'recipe/recipeReviews.html', {'recipe':recipe})

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

      chef = Chef(name=name, email=email, password=password)
      chef.save()

      return HttpResponseRedirect('/chefs')
  else:
    form = forms.AddChef()
  return render(request, 'recipe/addChef.html', {'form':form})

def addReview(request,recipe_id):
  recipe = get_object_or_404(Recipe, pk=recipe_id)
  if request.method == 'POST':
    comment = request.POST.get('Comment')
    rating = request.POST.get('staraddStars')
    revList = recipe.review_set.filter(chef_id=request.user.id)
    if revList.count() > 0:
      review = revList[0]
      review.comment = comment
      review.rating = rating
      review.save()
    else:
      recipe.review_set.create(comment=comment,rating=rating,chef_id=request.user.id)
    return HttpResponseRedirect('/recipes/'+str(recipe_id))

''' unused because using django's login function in urls
def login(request):
  if request.method == 'POST':
    form = forms.Login(request.POST, request.FILES)
    if form.is_valid():
      username = form.cleaned_data['username']
      pw = form.cleaned_data['password']

      try:
        chef = Chef.objects.get(name=username)
      except ObjectDoesNotExist:
        return HttpResponseRedirect('/login')

      if chef.password == pw:
        request.session['username'] = username
      else:
        return HttpResponseRedirect('/login')
    return HttpResponseRedirect('/')

  else:
    form = forms.Login()
  return render(request, 'recipe/awefawef.html', {'form':form})'''

@login_required(login_url='/login/')
def addRecipe(request):
  if request.method == 'POST':
    form = forms.AddRecipe(request.POST, request.FILES, extra=request.POST.get('inst'), ings=request.POST.get('ings'), pics=request.POST.get('pics'))
    if form.is_valid():
      recipeName = form.cleaned_data['recipe_Name']
      prepTime = form.cleaned_data['prep_Time']
      cookTime = form.cleaned_data['cook_Time']
      comments = form.cleaned_data['comments']
      
      instructions = form.cleaned_data['instructions']

      #api.post('/path/data/images/', file=(recipeName+'.'+picName[-1], picData))

      recipe = Recipe.objects.create(chef=get_object_or_404(Chef, pk=1), name=recipeName, prepTime=prepTime, cookTime=cookTime, chefComment=comments)#TODO: add chef, picture, ingredients, etc
      
      recipe.instruction_set.create(text=instructions)
      for i in range(form.cleaned_data['inst']):
        inst = request.POST.get('extra_field_'+str(i+1))
        recipe.instruction_set.create(text=inst)


      for i in range(form.cleaned_data['ings']):
        ingName = request.POST.get('extra_ings_'+str(i))
        amount = request.POST.get('amount_extra_ings_'+str(i))
        unitName = request.POST.get('unit_extra_ings_'+str(i))
        unit = UnitOfMeasure.objects.get(name=unitName)

        ingList = Ingredient.objects.filter(name=ingName)
        if ingList.count()>0:
          ingredient = ingList[0]
        else:
          ingredient = Ingredient.objects.create(name=ingName)
        RecipeIngredient.objects.create(recipe=recipe,ingredient=ingredient,amount=amount,unit=unit)

      api = BasicClient('VATx6OASrU4KYLaWshrxIvyyYUIl8x','xkpKJ3Wti1cXilKJYnMSqaOLvmNnwe')

      #make folder for pictures
      pictureFolder = '/RecipePicture/'+str(recipe.id)+'/'
      api.post('/path/oper/mkdir',path=pictureFolder)

      for p in request.FILES.getlist('picture'):
        picData = p.read()
        picName = p.name.split(".")
  
        f = open("tmp."+picName[-1], 'w')
        f.write(picData)
        f.close()

        im = Image.open("tmp."+picName[-1]) 
        size = 64, 64
        im.save(picName[0]+"."+picName[-1], "JPEG", quality=30)
        im.thumbnail(size, Image.ANTIALIAS)
        im.save("thumb.jpg", "JPEG")

        #upload picture
        fileName = recipeName+'_'+picName[0]+'.'+picName[-1]
        api.post('/path/data'+pictureFolder, file=(fileName, open(picName[0]+"."+picName[-1], 'r').read()))
        api.post('/path/data'+pictureFolder, file=(picName[0]+'_thumb.jpg', open('thumb.'+picName[-1], 'r').read()))

        #make picture object
        rpic = recipe.recipepicture_set.create()
        rpic.setPath(fileName)
        rpic.setSmallPath(picName[0]+'_thumb.jpg')

        #set this pic as recipe's main pic
        recipe.mainPicture = rpic
      recipe.save()

      return HttpResponseRedirect('/recipes')
  else:
    form = forms.AddRecipe()
  ingredients = Ingredient.objects.all()

  ings = "["
  for i in ingredients:
    ings += '"'+i.name+'",'
  ings = ings[:-1]+']' 
  
  units = UnitOfMeasure.objects.all()

  return render(request, 'recipe/addRecipe.html', {'form':form, 'ingredients':ings, 'units': units})

def test(request):
  return render(request, 'recipe/test.html', {})