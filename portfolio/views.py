from django.shortcuts import render
from .models import Asset, Portfolio
from .forms import PortfolioForm
from django.shortcuts import get_object_or_404, redirect
from django.views import generic

def home(request):
    return render(request, 'portfolio/home.html')

def create_portfolio(request):
    if request.method == "POST":
        form = PortfolioForm(request.POST)
        if form.is_valid():
            portfolio = form.save(commit=False)
            portfolio.user = request.user
            portfolio.save()
            form.save_m2m()
            return redirect('my-portfolios')
    else:
        form = PortfolioForm()
    return render(request, 'portfolio/portfolio_create.html', {'form': form})

def my_portfolios(request):
    portfolios_list = Portfolio.objects.all()
    return render(request, 'portfolio/my_portfolios.html', {'portfolios_list': portfolios_list})

def portfolio_analyses(request, pk):
    portfolio = Portfolio.objects.filter(pk=pk)
    return render(request, 'portfolio/portfolio_analyses.html', {'portfolio': portfolio})


# class PortfolioCreateView(generic.CreateView):
#     template_name = 'portfolio/portfolio_create.html'
#     form_class = PortfolioForm

# class PortfolioListView(generic.ListView):
#     model = Portfolio
#     context_object_name = 'portfolios_list'
#     template_name = 'portfolio/my_portfolios.html'
#
# class PortfolioDetailView(generic.DetailView):
#     model = Portfolio
#     context_object_name = 'portfolio'
#     template_name = 'portfolio/portfolio_analyses.html'
