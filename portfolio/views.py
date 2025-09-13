from django.shortcuts import render
from .models import Asset, Portfolio
from .forms import NewPortfolioForm
from django.shortcuts import get_object_or_404, redirect

def home(request):
    return render(request, 'portfolio/home.html')

def my_portfolios(request):
    portfolios_list = Portfolio.objects.all()
    return render(request, 'portfolio/my_portfolios.html', {'portfolios_list': portfolios_list})

def create_portfolio(request):
    if request.method == "POST":
        form = NewPortfolioForm(request.POST)
        if form.is_valid():
            portfolio = form.save(commit=False)
            portfolio.user = request.user
            portfolio.save()
            form.save_m2m()
            return redirect('my-portfolios')
    else:
        form = NewPortfolioForm()

    return render(request, 'portfolio/portfolio_create.html', {'form': form})

def portfolio_analyses(request, pk):
    portfolio = Portfolio.objects.filter(pk=pk)
    return render(request, 'portfolio/portfolio_analyses.html', {'portfolio': portfolio})
