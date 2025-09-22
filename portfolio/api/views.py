from rest_framework.views import APIView
from rest_framework.response import Response
import pandas as pd

class JohansenWeightsAPI(APIView):
    def get(self, request):
        try:
            df = pd.read_csv('portfolio/media/johansen_weights.csv')
            df_long = df.melt(id_vars='date', var_name='asset_name', value_name='weight')
            df_long['weight'] = df_long['weight'].astype(float).round(6)
            return Response(df_long.to_dict(orient='records'))

        except FileNotFoundError:
            return Response({'error': 'Weights not found. Please generate them first.'}, status=404)

class PortfolioPriceAPI(APIView):
    def get(self, request):
        try:
            df = pd.read_csv('portfolio/media/portfolio_price.csv')
            return Response(df.to_dict(orient='records'))

        except FileNotFoundError:
            return Response({'error': 'Portfolio series not found. Please generate them first.'}, status=404)

class PortfolioReturnAPI(APIView):
    def get(self, request):
        try:
            df = pd.read_csv('portfolio/media/portfolio_return.csv')
            return Response(df.to_dict(orient='records'))

        except FileNotFoundError:
            return Response({'error': 'Portfolio series not found. Please generate them first.'}, status=404)

