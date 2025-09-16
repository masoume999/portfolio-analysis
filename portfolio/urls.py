from django.urls import path

from . import views

urlpatterns = [
    path('home/', views.home, name='home'),
    path('my_portfolios/', views.my_portfolios, name='my-portfolios'),
    path('create_portfolio/', views.create_portfolio, name='create-portfolio'),
    path('<int:pk>/', views.portfolio_analyses, name='portfolio-analyses'),
    path('all_assets/', views.all_assets, name='all-assets'),
    path('<str:symbol>/', views.asset_analyses, name='asset-analyses'),
]
