"""
    template/ directory stores HTML templates
    that Django uses to render dynamic pages.

    Ex:

    In home.html
    <h1>Welcome, {{ name }}</h1>

    In a python file:

    from django.shortcuts import render

    def home(request):
        return render(request, "home.html", {"name": "Takapi"})
"""
