from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from django.views import generic

from .models import Asset, Portfolio
from .forms import PortfolioForm, AllAssetsForm
from .asset_analysis import LoadData, Statistics

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

def all_assets(request):
    form = AllAssetsForm(request.POST)
    symbols = list(Asset.objects.values_list('symbol', flat=True))
    charts = {}
    if form.is_valid():
        start_date = form.cleaned_data['start_date']
        end_date = form.cleaned_data['end_date']
        interval = form.cleaned_data['interval']
        load_data = LoadData(start_date, end_date, interval, symbols)
        for symbol in symbols:
            charts[symbol] = load_data.plot_price(symbol)

    return render(request, 'portfolio/all_assets.html', {
        'form': form, 'charts': charts, 'symbols': symbols})

def asset_analyses(request, pk):
    return

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
