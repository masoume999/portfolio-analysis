from django.urls import path
from .views import JohansenWeightsAPI, PortfolioPriceAPI, PortfolioReturnAPI

urlpatterns = [
    path('johansen_weights/', JohansenWeightsAPI.as_view(), name='weights-api'),
    path('portfolio_price/', PortfolioPriceAPI.as_view(), name='portfolio-price-api'),
    path('portfolio_return/', PortfolioReturnAPI.as_view(), name='portfolio-return-api'),
]
