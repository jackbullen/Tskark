from flask import Flask, request, Response, jsonify
import matplotlib
import mplfinance as mpf
from get_stock import get_stock
import io

app = Flask(__name__)

matplotlib.use('Agg')

@app.route('/stock_plot', methods=['GET'])
def stock_plot():
    ticker = request.args.get('ticker')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    if not ticker or not start_date or not end_date:
        return jsonify({"error": "Missing required parameters."}), 400
    
    df = get_stock(ticker, start_date, end_date)[0]
    
    buf = io.BytesIO()
    
    mpf.plot(df, type='candle', mav=(3,6,9), volume=True, show_nontrading=True, savefig=dict(fname=buf, format='png'))
    buf.seek(0)
    
    return Response(buf, content_type='image/png')

if __name__ == '__main__':
    app.run(debug=True)