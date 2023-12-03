from django.contrib import messages
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.views import View


class LoginView(View):
    def get(self, request):
        # present a login form
        return render(request, 'frontend/auth/login.html')

    def post(self, request):
        # process the login form
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            # login and redirect to index
            login(request, user)
            return redirect('index')
        else:
            # show error
            return render(request, 'frontend/auth/login.html', {'error': 'Неправильный логин или пароль'})


class LogoutView(View):
    def get(self, request):
        # logout and redirect to index
        logout(request)
        return redirect('index')


class SignUpView(View):
    def get(self, request):
        # if logged in, redirect to index
        if request.user.is_authenticated:
            return redirect('index')

        # present a signup form
        form = UserCreationForm()
        # set field class to form-control
        for field in form.fields:
            form.fields[field].widget.attrs['class'] = 'form-control'

        return render(request, 'frontend/auth/signup.html', {'form': form})

    def post(self, request):
        # process the signup form
        form = UserCreationForm(request.POST)

        # set field class to form-control
        for field in form.fields:
            form.fields[field].widget.attrs['class'] = 'form-control'

        if form.is_valid():
            # create the user and redirect to login
            form.save()
            messages.success(request, 'Вы успешно зарегистрировались')
            
            return redirect('login')
        else:
            # show error
            print(form.errors)

            # add classes to form.errors, such as 'is-invalid'
            for field in form.errors:
                form.fields[field].widget.attrs['class'] += ' is-invalid'

            return render(request, 'frontend/auth/signup.html', {'form': form})
